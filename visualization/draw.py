import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from functools import partial

para_list = ['algorithm','number_of_nodes', 'number_of_proposals', 
    'concurrent_proposals', 'reconfiguration', 'reconfig_policy', 
    'network_scenario', 'probability', 'data_size', 'compression_rate',
    'preprocessing_time', '']

SMALL_SIZE = 16
MEDIUM_SIZE = 18
BIG_SIZE = 22

def line_style(rate):
    return {
        0.2: 'v',
        0.5: 's',
        0.8: 'o'
    }.get(rate, '*') 

def marker_style(preprocessing):
    return {
        0: 'y-',
        2: 'r-.',
        5: 'g--',
        10: 'b:',
    }.get(preprocessing, 'y-') 

def read_to_df(file):
    df = pd.read_csv(file, sep=',')

    df[para_list] = df['PARAMS'].str.split('!N!',expand=True)
    for para in para_list:
        df[para] = df[para].str.split(':').str[1]

    df['label'] = df['probability'] + df['data_size'] + df['compression_rate'] + df['preprocessing_time']
    df['number_of_proposals'] = df['number_of_proposals'].astype('int')
    df['concurrent_proposals'] = df['concurrent_proposals'].astype('int')
    df['data_size'] = df['data_size'].astype('int')
    df['compression_rate'] = df['compression_rate'].astype('float')
    df['probability'] = df['probability'].astype('float')
    df['preprocessing_time'] = df['preprocessing_time'].astype('int')
    df['throughput'] = df['number_of_proposals'] / df['MEAN']

    return df

def format_y(y, _):
    return "{}k".format(int(y))

def format_demical(y, _):
    return "{:.1f}k".format(y)

def format_x(x, _):
	if x >= 1000 or x <= -1000:
		return "{}K".format(int(x/1000))
	else:
		return int(x)

if __name__ == "__main__":
    input = str(sys.argv[1])
    print("Reading input file: " + input)

    # params
    number_of_subplots = 3
    number_of_columns  = 3
    number_of_rows     = number_of_subplots // number_of_columns
    print("Display as ", number_of_rows, " rows, ", number_of_columns, " columns")

    df = read_to_df(input)
    print("Head: \n", df.head())

    # create subtitles for each row
    fig, big_axes = plt.subplots(nrows=number_of_rows, ncols=number_of_columns, sharey=True) 
    for row, big_ax in enumerate(big_axes, start=1):
        # Turn off axis lines and ticks of the big subplot 
        # obs alpha is 0 in RGBA string!
        big_ax.tick_params(labelcolor=(1.,1.,1., 0.0), top='off', bottom='off', left='off', right='off')
        # removes the white frame
        big_ax._frameon = False
        big_ax.set_xticks([])
        big_ax.set_yticks([])

    # seperate baseline from tests
    base_df = df[df['probability'] == 0.0]
    df = df[df['probability'] != 0.0]

    # create subplots
    position = range(1, number_of_subplots + 1)
    fig.set_size_inches(18, 8)
    index = 0
    for p, grp1 in df.groupby('probability'):
        # add subplot one by one
        ax = fig.add_subplot(number_of_rows, number_of_columns, position[index])
        index += 1
        
        # format title
        proba = "{}%".format(int(p*100))
        ax.set_title("Cache Hit Rate:%s" % (proba))
        
        # draw baseline
        label = "No caching"
        ax.plot(base_df['data_size'], base_df['throughput'], line_style(0) + marker_style(0), label=label)
        ax.set_xticks(base_df['data_size'])

        # set x-axis scale as log
        ax.set_xscale('log')

        # draw tests
        for k2, grp2 in grp1.groupby(['compression_rate', 'preprocessing_time']):
            (rate, pre) = k2
            style = line_style(rate) + marker_style(pre)
            rate  = "{:2}%".format(int(rate*100))
            pre   = "{:2}μs".format(int(pre))
            label = "Compression: {}, Preprocess:{}".format(rate, pre)
                
            ax.plot(grp2['data_size'], grp2['throughput'], style, label=label)
            ax.set_xticks(grp2['data_size'])

        for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] + ax.get_xticklabels() + ax.get_yticklabels()):
            item.set_fontsize(MEDIUM_SIZE)

        # format x/y labels
        ax.xaxis.set_major_formatter(format_x)
        ax.yaxis.set_major_formatter(format_y)

        # add some custom operations here
        #ax.set_ylim([0, 300])
    
    # Add legends
    handles, labels = ax.get_legend_handles_labels()
    handles.reverse() # looks better in the reversed order
    labels.reverse()
    # set as top-left
    fig.legend(handles, labels, prop={'size': SMALL_SIZE}, bbox_to_anchor=(0.3, 1.02))
    
    # Add Labels
    fig.text(0.5, 0.06, 'Data Size (Bytes)', ha='center', va='center', size=BIG_SIZE)
    fig.text(0.05, 0.5, 'Throughput (Operations/s)', ha='center', va='center', rotation='vertical', size=BIG_SIZE)
    plt.subplots_adjust(left=0.1,
                        bottom=0.15,
                        right=0.9,
                        top=0.7,
                        wspace=0.3,
                        hspace=0.3)
    # Increase the dpi if needed
    plt.savefig("{}.pdf".format(input), dpi = 1000, bbox_inches='tight')
