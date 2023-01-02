use crate::cache::UniCache;
use indexmap::IndexMap;
use lru::LruCache;
use std::fmt::Debug;
use std::hash::Hash;
use std::marker::PhantomData;
use std::num::NonZeroUsize;

pub struct LruUniCache<T: Clone + Debug + Hash + Eq> {
    capacity: usize,
    lru_cache: LruCache<usize, PhantomData<bool>>,
    index_cache: IndexMap<T, PhantomData<bool>>,
}

impl<T: Clone + Debug + Hash + Eq> UniCache<T> for LruUniCache<T> {
    fn new(capacity: usize) -> Self {
        Self {
            capacity,
            lru_cache: LruCache::new(NonZeroUsize::new(capacity).unwrap()),
            index_cache: IndexMap::with_capacity(capacity),
        }
    }

    fn put(&mut self, item: T) {

        let (index, _) = self.index_cache.insert_full(item, PhantomData);
        if self.lru_cache.push(index, PhantomData).is_some() {
            // already exists
            return;
        }   // not exists so insert it and check if full
        else if self.lru_cache.len() > self.capacity {
            // full, pop out one item
            self.lru_cache.pop_lru();
        }
    }

    fn get_encoded_index(&mut self, item: &T) -> Option<usize> {
        if let Some(index) = self.index_cache.get_index_of(item) {
            // Have seen it before
            if self.lru_cache.get(&index).is_some() {
                // exists in cache
                return Some(index);
            }
            // not in cache, already popped out
        }

        None
    }

    fn get_with_encoded_index(&mut self, index: usize) -> T {
        let item = self.index_cache.get_index(index).unwrap().0.clone();
        item
    }
}
