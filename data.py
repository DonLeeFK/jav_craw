import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from wordcloud import WordCloud
import requests
from bs4 import BeautifulSoup
import logging
import os

mpl.rcParams['font.family'] = 'SimHei' # set font family to SimHei to allow displaying Chinese characters in the chart

csv_files = [f for f in os.listdir('./data') if f.endswith('.csv') and '_verbose' in f]

print("Choose a CSV file to proceed:")
for i, file in enumerate(csv_files):
    print(f"{i+1}. {file}")

selected_file = input("Enter the number of the file you want to use: ")
selected_file = csv_files[int(selected_file)-1]

df_raw = pd.read_csv(f'./data/{selected_file}')
#df_raw = pd.read_csv('data/水菜麗_verbose.csv')
output_path = f'./data/{selected_file[:-4]}.csv'

def findAliasName(name):#find alias name of an actor and return list of all alias names
    url = f"https://javdb.com/search?q={name}&f=actor"
    name_dict = {}
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
    except:
        logging.warning("Couldn't find alias name")
        #print("Couldn't find alias name")
        return {name:name}
    body = soup.find('body', {'data-lang': 'zh'})
    try:
        section = body.find('section', {'class': 'section'})
    except:
        logging.warning("Couldn't find alias name")
        return {name:name}
    container = section.find('div', {'class': 'container'})
    try:
        actor_box = container.find('div', {'class': 'actors'}).find_all('div', {'class': 'box actor-box'})
        for item in actor_box:
            actor = item.find('a')
            primary_name = actor.find('strong').text.strip()
            names = actor['title']
            names = names.split(',')
            name_dict[primary_name]=names
            
    except:
        return {name:name}
    if name_dict:
        return name_dict
    else:
        return {name:name}
    
    

def filterJoyu(df, keyword):
    df_filtered = df.copy()
    df_filtered = df_filtered.dropna(subset=['j_actors'])
    df_filtered = df_filtered[df_filtered['j_actors'].str.contains(keyword)]
    df_filtered = df_filtered.reset_index(drop=True)
    return df_filtered

def filterJoyuEnhanced(df, keyword):
    name_dict = findAliasName(keyword)
    #get all alias names and store them in name_list
    name_list = [item for key in name_dict.keys() for item in name_dict[key]]
    df_filtered_all = pd.DataFrame(columns=df.columns)
    for name in name_list:
        df_filtered = filterJoyu(df, name)
        df_filtered_all = pd.concat([df_filtered_all, df_filtered], sort=False)
    df_filtered_all = df_filtered_all.reset_index(drop=True)
    return df_filtered_all
    
    

def filterTag(df, keyword):
    df_filtered = df.copy()
    df_filtered = df_filtered.dropna(subset=['category'])
    df_filtered = df_filtered[df_filtered['category'].str.contains(keyword)]
    df_filtered = df_filtered.reset_index(drop=True)
    return df_filtered

# remove duplicate rows based on column 'bango'
def removeDuplicate(df_raw):
    df = df_raw.copy()
    df.drop_duplicates(subset='bango', inplace=True)
    df.replace(['N/A', 'n/a'], None, inplace=True)
    df.insert(0, 'original_idx', df.index)
    df.reset_index(drop=True, inplace=True)
    return df

def saveCSV(df_raw):
    df = df_raw.copy()
    if 'original_idx' in df.columns:
        df.drop('original_idx', axis=1, inplace=True)
    df.to_csv(output_path, index=False)
    del df



def plotTag(df):
    tags = df['category'].str.split() # split the content in each row by space to get tags
    tag_counts = {} # create an empty dictionary to store the tag counts
    for row in tags:
        for tag in row:
            if tag in tag_counts:
                tag_counts[tag] += 1
            else:
                tag_counts[tag] = 1
    tag_df = pd.DataFrame.from_dict(tag_counts, orient='index', columns=['count'])
    font = 'SimHei'
    stop_words = ['單體作品',
                '4小時以上作品',
                '介紹影片',
                '數位馬賽克',
                '精選綜合',
                ]
    tag_counts_clean = {k:v for k,v in tag_counts.items() if k not in stop_words}
    wordcloud = WordCloud(width = 800, height = 800, 
                    background_color ='white',
                    font_path=font, 
                    min_font_size = 10).generate_from_frequencies(tag_counts_clean) 

    plt.figure(figsize = (8, 8), facecolor = None) 
    plt.imshow(wordcloud) 
    plt.axis("off") 
    plt.tight_layout(pad = 0) 
    #tag_df_sorted.plot(kind='bar') # display the tag counts in a bar chart
    #plt.xticks(rotation=45)


    plt.show() # display the plot using matplotlib
    
def printDfWithDots(df):
    num_rows = 10
    df_subset = df.iloc[-num_rows:]
    print(df_subset)


def main():
    df = removeDuplicate(df_raw)
    print(df.info())
    print(df.tail(10))
    plotTag(df)
    saveCSV(df)
    

main()