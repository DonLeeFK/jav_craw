import pandas as pd
import os
import requests
from bs4 import BeautifulSoup
import logging

#keep only the 3 most recent log including the current one
log_files = [f for f in os.listdir('./log') if f.endswith('.log')]
log_files.sort(key=lambda x: os.path.getmtime(os.path.join('./log', x)))
if len(log_files) > 4:
    for file in log_files[:-4]:
        os.remove(os.path.join('./log', file))
import time
logging.basicConfig(filename=f'./log/magnet_{time.strftime("%Y%m%d-%H%M%S")}.log', level=logging.WARNING)

def fetchMagnet0Mag(response):
    soup = BeautifulSoup(response.content, 'html.parser')
    #link = soup.find('a')['href']
    table = soup.find('div',{'class':'container'})\
        .find('table').find('tbody').find_all('tr')
    links = []
    
    for tr in table:
        try:
            link = 'https://0mag.net'+tr.find('a')['href']
            links.append(link)
        except:
            continue
    mags = []
    #limit the number of magnet links to 3
    links = links[:3]
    if links:
        for link in links:
            response = requests.get(link)
            soup = BeautifulSoup(response.content, 'html.parser')
            mag = soup.find('input', {'id': 'input-magnet'})['value']
            mags.append(mag)
    mags = '\n'.join(mags)
    #print(mags)
    return mags
    


#takes only file without '_verbose'
csv_files = [f for f in os.listdir('./data') if f.endswith('.csv') \
             and '_verbose' not in f]



while True:
    for i, file in enumerate(csv_files):
        print(f"{i+1}. {file}")
    selected_file = input("Enter the number of the file you want to use (press 0 to exit): ")
    if selected_file == '0':
        exit()
        break
    try:
        selected_file = int(selected_file)
        if selected_file > 0 and selected_file <= len(csv_files):
            selected_file = csv_files[selected_file-1]
            break
        else:
            print("Invalid input. Please enter a valid number.")
    except ValueError:
        print("Invalid input. Please enter a valid number.")

df = pd.read_csv(f'./data/{selected_file}')
df['magnet'] = pd.Series(dtype='object')
df['magnet'].fillna(value='', inplace=True)
#print(df.head())
#print(df['bango'])

from tqdm import tqdm


for bango in tqdm(df['bango']):
    url = f"https://0mag.net/search?q={bango}"
    try:
        response = requests.get(url)
        mags_0mag = fetchMagnet0Mag(response)
        df.loc[df['bango'] == bango, 'magnet'] = mags_0mag
    except requests.exceptions.ConnectionError:
        logging.warning(f"Couldn't connect to {url}")
        continue
   

if '_magnet' not in selected_file:
    df.to_csv(f'./data/{selected_file[:-4]}_magnet.csv', index=False)
else:
    df.to_csv(f'./data/{selected_file}', index=False)
    
    
    
