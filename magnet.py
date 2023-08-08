import pandas as pd
import os
import requests
from bs4 import BeautifulSoup
import logging
from rich.progress import track
from concurrent.futures import ThreadPoolExecutor

#keep only the 3 most recent log including the current one
log_files = [f for f in os.listdir('./log') if f.endswith('.log')]
log_files.sort(key=lambda x: os.path.getmtime(os.path.join('./log', x)))
if len(log_files) > 4:
    for file in log_files[:-4]:
        os.remove(os.path.join('./log', file))
import time
logging.basicConfig(filename=f'./log/magnet_{time.strftime("%Y%m%d-%H%M%S")}.log', level=logging.WARNING)

def fetchMagnet0Mag(response, num=3):
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
    links = links[:num]
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
try:
    num = input("Enter how many magnet link you want to extract for each bango(default is 3, press enter to skip): ")
    if num:
        num = int(num)
    else:
        pass
except ValueError:
    num = None
    print("Invalid input. Revert back to default.")
    
from tqdm import tqdm
from tqdm.contrib.concurrent import thread_map

def Mag(bango):
    #print(bango)
    url = f"https://0mag.net/search?q={bango}"
    try:
        response = requests.get(url)
        if num:
            mags_0mag = fetchMagnet0Mag(response, num=num)
        else:
            mags_0mag = fetchMagnet0Mag(response)
        df.loc[df['bango'] == bango, 'magnet'] = mags_0mag
    except requests.exceptions.ConnectionError:
        logging.warning(f"Couldn't connect to {url}")
        return
    
   
'''
with ThreadPoolExecutor() as executor:
    with tqdm(total = len(df['bango'])) as progress:
        for bango in list(df['bango']):
            future = executor.submit(Mag, bango)
            future.add_done_callback(lambda p: progress.update())
'''
#with ThreadPoolExecutor() as executor:
#    tqdm(executor.map(Mag, df['bango']), total=len(df['bango']))
thread_map(Mag, df['bango'])

if '_magnet' not in selected_file:
    df.to_csv(f'./data/{selected_file[:-4]}_magnet.csv', index=False)
else:
    df.to_csv(f'./data/{selected_file}', index=False)
    
    
    
