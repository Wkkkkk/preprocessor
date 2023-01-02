use crate::cache::UniCache;
use indexmap::IndexMap;
use lfu_cache::LfuCache;
use std::fmt::Debug;
use std::hash::Hash;
use std::marker::PhantomData;

pub struct LfuUniCache<T: Clone + Debug + Hash + Eq> {
    capacity: usize,
    lfu_cache: LfuCache<usize, PhantomData<bool>>,
    index_cache: IndexMap<T, PhantomData<bool>>,
}

impl<T: Clone + Debug + Hash + Eq> UniCache<T> for LfuUniCache<T> {
    fn new(capacity: usize) -> Self {
        Self {
            capacity,
            lfu_cache: LfuCache::with_capacity(capacity),
            index_cache: IndexMap::with_capacity(capacity),
        }
    }

    fn put(&mut self, item: T) {
        let (index, _) = self.index_cache.insert_full(item, PhantomData);
        if self.lfu_cache.insert(index, PhantomData).is_some() {
            // already exists
            return;
        }   // not exists so insert it and check if full
        else if self.lfu_cache.len() > self.capacity {
            // full, pop out one item
            self.lfu_cache.pop_lfu_key_value();
        }
    }

    fn get_encoded_index(&mut self, item: &T) -> Option<usize> {
        if let Some(index) = self.index_cache.get_index_of(item) {
            // Have seen it before
            if self.lfu_cache.get(&index).is_some() {
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
