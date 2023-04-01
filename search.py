from utils import cleanActors
from utils import cleanCategory
from utils import getDetailedInfo
from utils import fetchPage
from utils import findActor
from utils import writeCSV
import logging
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import csv

def joyusearch(DETAIL=True, MAX_PAGE=50):
    name = input("Enter a name to search for: ")
    actor_dict = findActor(name)
    #print(actor_dict)
    if len(actor_dict) == 0:
        print(f"Couldn't find joyu named '{name}'!")
        return
    else:
        if len(actor_dict) >1:
            for index, key in enumerate(actor_dict):
                value = actor_dict[key]
                print(f"{index+1}. {key}: {value}")
                
            choice = int(input("Enter your choice of joyu: "))
            url = list(actor_dict.values())[choice-1]
            primary_name = list(actor_dict.keys())[choice-1]
            
        else:
            url = list(actor_dict.values())[0]
            primary_name = list(actor_dict.keys())[0]
    
    
    data = [] #[bango, title, href]
    if DETAIL:
        data_detailed = []
    # Loop through all the pages
    for page in tqdm(range(1, MAX_PAGE+1)):
        page_url = f'{url}?page={page}'
        
        try:
            response = requests.get(page_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            #print(f"page{page} opened")
        except:
            print("That's all")
            break
        
        if DETAIL:
            new_data, new_data_detailed = fetchPage(soup, DETAIL)
            if new_data == 0:
                break
            data += new_data
            data_detailed += new_data_detailed
        else:
            new_data = fetchPage(soup, DETAIL)
            if new_data == 0:
                break
            data += new_data
        
        
    
    writeCSV(primary_name, data, data_detailed)
    


def keywordsearch(DETAIL=True, MAX_PAGE=50): 
    keyword = input("Enter a keyword to search for(press enter to skip): ")

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
        
        if DETAIL:
            new_data, new_data_detailed = fetchPage(soup, DETAIL)
            if new_data == 0:
                break
            data += new_data
            data_detailed += new_data_detailed
        else:
            new_data = fetchPage(soup, DETAIL)
            if new_data == 0:
                break
            data += new_data
        
    writeCSV(keyword, data, data_detailed)

    