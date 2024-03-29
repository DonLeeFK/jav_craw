import requests
from bs4 import BeautifulSoup
import csv
from tqdm import tqdm
import logging
import pandas as pd
from rich.progress import track
from concurrent.futures import ThreadPoolExecutor

def findActor(name):
    actor_dict = {}
    
    url = f"https://javdb.com/search?q={name}&f=actor"
    print(f"link: {url}")
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
    except:
        logging.warning(f"Couldn't find {name}")
        #print("Couldn't find alias name")
        return actor_dict
    body = soup.find('body', {'data-lang': 'zh'})
    try:
        section = body.find('section', {'class': 'section'})
    except:
        logging.warning(f"Couldn't find {name}")
        return actor_dict
    container = section.find('div', {'class': 'container'})
    try:
        actor_box = container.find('div', {'class': 'actors'}).find_all('div', {'class': 'box actor-box'})
        for item in actor_box:
            actor = item.find('a')
            primary_name = actor.find('strong').text.strip()
            names = actor['title']
            
            try:
                flag = actor.find('figure', {'class': 'image'}).find('span', {'class': 'info'}).text
                if flag == "無碼" :
                    primary_name += ('('+flag+')')

            except:
                pass
            
            href = "https://javdb.com"+actor['href']
            actor_dict[primary_name] = href
            #print(f"{primary_name}: {href}")
            names = names.split(',')
    except:
        pass
        
    return actor_dict

def findList(name):
    name  = name.replace(" ", "%20")
    
    list_dict = {}
    
    url = f"https://javdb.com/search?q={name}&f=list"
    print(f"link: {url}")
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
    except:
        logging.warning(f"Couldn't find {name}")
        #print("Couldn't find alias name")
        return list_dict
    body = soup.find('body', {'data-lang': 'zh'})
    try:
        section = body.find('section', {'class': 'section'})
    except:
        logging.warning(f"Couldn't find {name}")
        return list_dict
    container = section.find('div', {'class': 'container'})
    try:
        list_box = container.find_all('a', {'class': 'box'})
        #print(list_box[19])
        for item in list_box:
            list_name = item.find('strong').text.strip()
            list_len = item.find('span').text.strip()
            list_len = list_len.replace("(", "").replace(")", "")
            list_key = list_name+':'+list_len
            href = "https://javdb.com"+item['href']
            list_dict[list_key] = href
            #print(f"{primary_name}: {href}")
    except:
        pass
        
    return list_dict


def cleanActors(input_list):
        male_list = []
        female_list = []

        # iterate through input list
        for element in input_list:
            # check if element contains male symbol
            if '♂' in element:
                # remove male symbol and append to male list
                male_list.append(element.replace('♂', ''))
            # check if element contains female symbol
            elif '♀' in element:
                # remove female symbol and append to female list
                female_list.append(element.replace('♀', ''))
            else:
                female_list.append(element)
        return female_list, male_list

def cleanCategory(input_list):
    output_list = [s.replace(',', '') for s in input_list]
    return output_list


def fetchPage(soup, DETAIL):
    data = []
    data_detailed = []
    body = soup.find('body', {'data-lang': 'zh'})
    try:
        section = body.find('section', {'class': 'section'})
    except:
        print("That is the end!")
        return 0
    container = section.find('div', {'class': 'container'})
    videos = container.find_all('a')
    if len(videos) == 0:
        print("That is the end!")
        return 0

    for video in tqdm(videos):
        bango = video.find('strong')
        if not bango:
            continue
        if bango:
            bango = bango.text
            title = video.find('div', {'class': 'video-title'}).text
            title = title.split()[1:]
            title = ' '.join(title)
            href = "https://javdb.com"+video['href']
            if DETAIL:
                try:
                    response = requests.get(href)
                    #print(response.status_code)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    #print(f"subpage {href} opened")
                    data_e = getDetailedInfo(soup)#extra info
                    
                except:
                    #print(f"Error: Could not fetch page: {href}, status code: {response.status_code}")
                    continue
            data_frame = [bango, title, href]
            data.append(data_frame)
            if DETAIL:
                data_frame_e = data_frame + data_e
                data_detailed.append(data_frame_e)
                #print(data_frame_e)
            else:
                pass
                #print(data_frame)
    if not DETAIL:
        return data
    else:
        return data, data_detailed


def getDetailedInfo(soup):
    body = soup.find('body', {'data-lang': 'zh'})
    section = body.find('section', {'class': 'section'})
    container = section.find('div', {'class': 'container'})
    meta = container.find('div',{'class': 'video-detail'}).find('div',{'class': 'video-meta-panel'}).find_all('div',{'class': 'panel-block'})

    data_extra = []#[joyu, danyu, cat]
    dict = { 'joyu': None, 'danyu': None, 'cat': None }
    
    
    for block in meta:
        #print(data_extra)
        mark = block.find('strong')
        mark_text = mark.text
        #print(f"tag is {mark_text}")
        
        if mark_text == "類別:":
            category = mark.find_all('span',{'class': 'value'})
            category = block.text.split()[1:]
            #print("CATEGORY: ", end="")
            category = cleanCategory(category)
            cat = " ".join(category)
            dict['cat']=cat
            #data_extra.append(cat)
            #print(cat)
        if mark_text == "演員:":
            actors = block.text.split()[1:]
            #print("ACTORS: ", end="")
            j_actors, d_actors = cleanActors(actors)
            joyu = " ".join(j_actors)
            if joyu != 'N/A':
                dict['joyu']=joyu
            if len(d_actors) != 0:
                danyu = " ".join(d_actors)
                dict['danyu']=danyu
            else:
                dict['danyu']="N/A"
                
            #print(f"j: {dict['joyu']}, d: {dict['danyu']}")
            data_extra = [dict['joyu'],dict['danyu'],dict['cat']]
            return data_extra
        
def removeDuplicate(df_raw):
    df = df_raw.copy()
    df.drop_duplicates(subset='bango', inplace=True)
    df.replace(['N/A', 'n/a'], None, inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

def writeCSV(prefix, data, data_detailed=None):
    output_path = './data/'+prefix+'.csv'
    output_path_verbose = './data/'+prefix+'_verbose.csv'
    print(output_path)
    df = pd.DataFrame(data, columns=['bango', 'title', 'link'])
    df = removeDuplicate(df)
    df.to_csv(output_path, index=False)
    '''
    with open(output_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['bango', 'title', 'link'])  # Add the header row
        writer.writerows(data)
    '''
    if data_detailed:
        df_detailed = pd.DataFrame(data_detailed, columns=['bango', 'title','link', 'j_actors', 'd_actors', 'category'])
        df_detailed = removeDuplicate(df_detailed)
        df_detailed.to_csv(output_path_verbose, index=False)
        '''
        with open(output_path_verbose, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['bango', 'title','link', 'j_actors', 'd_actors', 'category'])  # Add the header row
            writer.writerows(data_detailed)
        '''
    
    



def better_fetchPage(soup, DETAIL):
    data = []
    data_detailed = []
    body = soup.find('body', {'data-lang': 'zh'})
    try:
        section = body.find('section', {'class': 'section'})
    except:
        print("That is the end!")
        return 0
    container = section.find('div', {'class': 'container'})
    videos = container.find_all('a')
    if len(videos) == 0:
        print("That is the end!")
        return 0
    
    
    def extract(video):
        nonlocal data
        nonlocal data_detailed
        bango = video.find('strong')
        if not bango:
            return
        if bango:
            bango = bango.text
            title = video.find('div', {'class': 'video-title'}).text
            title = title.split()[1:]
            title = ' '.join(title)
            href = "https://javdb.com"+video['href']
            if DETAIL:
                try:
                    response = requests.get(href)
                    #print(response.status_code)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    #print(f"subpage {href} opened")
                    data_e = getDetailedInfo(soup)#extra info
                    
                except:
                    #print(f"Error: Could not fetch page: {href}, status code: {response.status_code}")
                    return
            data_frame = [bango, title, href]
            data.append(data_frame)
            if DETAIL:
                data_frame_e = data_frame + data_e
                data_detailed.append(data_frame_e)
                #print(data_frame_e)
            else:
                pass
                #print(data_frame)
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError as e:
        if str(e).startswith('There is no current event loop in thread'):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        else:
            raise

    tasks = [asyncio.ensure_future(extract(video)) for video in videos]
    loop.run_until_complete(asyncio.wait(tasks))
    #for video in track(videos):
        #extract(video)
    """
    with ThreadPoolExecutor() as executor:
        executor.map(extract, videos)    
    if not DETAIL:
        return data
    else:
        return data, data_detailed