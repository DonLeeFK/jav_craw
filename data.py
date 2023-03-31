import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.rcParams['font.family'] = 'SimHei' # set font family to SimHei to allow displaying Chinese characters in the chart

df = pd.read_csv('output_verbose.csv')


def joyu_filter(df, keyword):
    df.dropna(subset=['j_actors'], inplace=True)
    #print(df)
    df = df[df['j_actors'].str.contains(keyword)]
    df.reset_index(drop=True, inplace=True)
    return df

df = joyu_filter(df, '河北彩花')
tags = df['category'].str.split() # split the content in each row by space to get tags
tag_counts = {} # create an empty dictionary to store the tag counts
for row in tags:
    for tag in row:
        if tag in tag_counts:
            tag_counts[tag] += 1
        else:
            tag_counts[tag] = 1
tag_df = pd.DataFrame.from_dict(tag_counts, orient='index', columns=['count'])
tag_df_sorted = tag_df.sort_values(by='count', ascending=False)
tag_df_sorted.plot(kind='bar') # display the tag counts in a bar chart
plt.xticks(rotation=45)

df.to_csv('output_verbose.csv', index=False)

plt.show() # display the plot using matplotlib