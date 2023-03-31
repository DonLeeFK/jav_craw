import requests
from bs4 import BeautifulSoup
import csv
from tqdm import tqdm


MAX_PAGE = 50
DETAIL = True

keyword = input("Enter a keyword to search for(press enter to skip): ")

url = f'https://javdb.com/search?q={keyword}'
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')




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



def getDetailedInfo(meta):
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

     



data = [] #[bango, title, href]
if DETAIL:
    data_detailed = []
# Loop through all the pages
for page in tqdm(range(1, MAX_PAGE+1)):
    if keyword:
        page_url = f'https://javdb.com/search?q={keyword}&page={page}'
    else:
        page_url = f'https://javdb.com/?page={page}'
    
    try:
        response = requests.get(page_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        #print(f"page{page} opened")
    except:
        print("That's all")
        break

    body = soup.find('body', {'data-lang': 'zh'})
    try:
        section = body.find('section', {'class': 'section'})
    except:
        print("That is the end!")
        break
    container = section.find('div', {'class': 'container'})
    videos = container.find_all('a')
    
    
    
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
                        body = soup.find('body', {'data-lang': 'zh'})
                        section = body.find('section', {'class': 'section'})
                        container = section.find('div', {'class': 'container'})
                        meta = container.find('div',{'class': 'video-detail'}).find('div',{'class': 'video-meta-panel'}).find_all('div',{'class': 'panel-block'})
                        data_e = getDetailedInfo(meta)#extra info
                        
                        
                    except:
                        #print(f"Error: Could not fetch page: {href}, status code: {response.status_code}")
                        continue
                data_frame = [bango, title, href]
                data.append(data_frame)
                if DETAIL:
                    data_frame_e = data_frame + data_e
                    data_detailed.append(data_frame_e)
                    print(data_frame_e)




# Open a new file in write mode
with open('output.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['bango', 'title', 'link'])  # Add the header row
    writer.writerows(data)
if DETAIL:
    with open('output_verbose.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['bango', 'title','link', 'j_actors', 'd_actors', 'category'])  # Add the header row
        writer.writerows(data_detailed)