import requests
from bs4 import BeautifulSoup
import csv
from tqdm import tqdm
import logging


def findActor(name):
    actor_dict = {}
    
    url = f"https://javdb.com/search?q={name}&f=actor"
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
    except:
        logging.warning("Couldn't find such name")
        #print("Couldn't find alias name")
        return actor_dict
    body = soup.find('body', {'data-lang': 'zh'})
    try:
        section = body.find('section', {'class': 'section'})
    except:
        logging.warning("Couldn't find such name")
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

    for video in videos:
        bango = video.find('strong')
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
                print(data_frame_e)
            else:
                print(data_frame)
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

def writeCSV(prefix, data, data_detailed=None):
    output_path = './data/'+prefix+'.csv'
    output_path_verbose = './data/'+prefix+'_verbose.csv'
    print(output_path)
    with open(output_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['bango', 'title', 'link'])  # Add the header row
        writer.writerows(data)
    if data_detailed:
        with open(output_path_verbose, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['bango', 'title','link', 'j_actors', 'd_actors', 'category'])  # Add the header row
            writer.writerows(data_detailed)