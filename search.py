from utils import cleanActors
from utils import cleanCategory
from utils import getDetailedInfo
from utils import fetchPage, better_fetchPage
from utils import findActor
from utils import findList
from utils import writeCSV
import logging
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from rich.progress import track
import httpx
import asyncio
import nest_asyncio
nest_asyncio.apply()
import csv
from pprint import pprint
#import backgroud




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
            for index, key in enumerate(actor_dict):
                value = actor_dict[key]
                print(f"{key}: {value}")
            url = list(actor_dict.values())[0]
            primary_name = list(actor_dict.keys())[0]
    
    
    data = [] #[bango, title, href]
    if DETAIL:
        data_detailed = []
    # Loop through all the pages
    for page in track(range(1, MAX_PAGE+1)):
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
        
        
    if DETAIL:
        writeCSV(primary_name, data, data_detailed)
    else:
        writeCSV(primary_name, data)
        

def listsearch(DETAIL=True):
    name = input("Enter a list to search for: ")
    list_dict = findList(name)
    if len(list_dict) == 0:
        print(f"Couldn't find list related to '{name}'!")
        return
    else:
        if len(list_dict) >1:
            for index, key in enumerate(list_dict):
                value = list_dict[key]
                print(f"{index+1}. {key}: {value}")
                
            choice = int(input("Enter your choice of list: "))
            url = list(list_dict.values())[choice-1]
            list_key = list(list_dict.keys())[choice-1].split(':')
            list_name = list_key[0]
            list_len = int(list_key[1])
            
        else:
            for index, key in enumerate(list_dict):
                value = list_dict[key]
                print(f"{key}: {value}")
            url = list(list_dict.values())[0]
            list_key = list(list_dict.keys())[0]
            list_name = list_key[0]
            list_len = int(list_key[1])
    
    PAGE_NUM = int(list_len/40)+1
    data = [] #[bango, title, href]
    if DETAIL:
        data_detailed = []
    # Loop through all the pages
    for page in track(range(1, PAGE_NUM+1)):
        if len(data)>501:
            break
        page_url = f'{url}?page={page}'
        
        try:
            response = requests.get(page_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            #print(f"page{page} opened")
        except:
            print("That's all")
            break
        
        if DETAIL:
            new_data, new_data_detailed = better_fetchPage(soup, DETAIL)
            if new_data == 0:
                break
            data += new_data
            data_detailed += new_data_detailed
        else:
            new_data = better_fetchPage(soup, DETAIL)
            if new_data == 0:
                break
            data += new_data
        
        
    if DETAIL:
        writeCSV(list_name, data, data_detailed)
    else:
        writeCSV(list_name, data)
        


def keywordsearch(DETAIL=True, MAX_PAGE=50): 
    keyword = input("Enter a keyword to search for(press enter to skip): ")

    data = [] #[bango, title, href]
    if DETAIL:
        data_detailed = []
    # Loop through all the pages
    for page in track(range(1, MAX_PAGE+1)):
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
    
    if DETAIL:
        if keyword:    
            writeCSV(keyword, data, data_detailed)
        else:
            writeCSV('recommendations', data, data_detailed)
    else:
        if keyword:    
            writeCSV(keyword, data)
        else:
            writeCSV('recommendations', data)



def better_keywordsearch(DETAIL=True, MAX_PAGE=50): 
    keyword = input("Enter a keyword to search for(press enter to skip): ")

    data = [] #[bango, title, href]
    if DETAIL:
        data_detailed = []
    if keyword:
        pages_url = [f'https://javdb.com/search?q={keyword}&page={page}' for page in range(1, MAX_PAGE+1)]
    else:
        pages_url = [f'https://javdb.com/?page={page}' for page in range(1, MAX_PAGE+1)]
    
    #pprint(pages_url)
    
    
    async def getPages():
        async with httpx.AsyncClient(timeout=None) as client:
            tasks = (client.get(url) for url in pages_url)
            reqs = await asyncio.gather(*tasks)
        
        responses = [req for req in reqs]
        
        return responses
    

    def parsePages(response):
        #pprint(response)
        nonlocal data
        if DETAIL:
            nonlocal data_detailed
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
        except:
            print("That's all")
            return
        
        if DETAIL:
            try:
                new_data, new_data_detailed = better_fetchPage(soup, DETAIL)
            except TypeError:
                return
            if new_data == 0:
                return
            data += new_data
            data_detailed += new_data_detailed
        else:
            try:
                new_data, new_data_detailed = better_fetchPage(soup, DETAIL)
            except TypeError:
                return
            if new_data == 0:
                return
            data += new_data
        #print(data)
    responses = asyncio.run(getPages())
    #for response in responses: 
    #    pprint(response.content) 
    
    

    for response in track(responses):
        parsePages(response)
    #print(data)
    if DETAIL:
        if keyword:    
            writeCSV(keyword, data, data_detailed)
        else:
            writeCSV('recommendations', data, data_detailed)
    else:
        if keyword:    
            writeCSV(keyword, data)
        else:
            writeCSV('recommendations', data)
    
def better_joyusearch(DETAIL=True, MAX_PAGE=50):
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
            for index, key in enumerate(actor_dict):
                value = actor_dict[key]
                print(f"{key}: {value}")
            url = list(actor_dict.values())[0]
            primary_name = list(actor_dict.keys())[0]
    
    
    data = [] #[bango, title, href]
    if DETAIL:
        data_detailed = []
        
    pages_url = []
    for page in track(range(1, MAX_PAGE+1)):
        page_url = f'{url}?page={page}'
        pages_url.append(page_url)
    
    
    async def getPages():
        async with httpx.AsyncClient() as client:
            tasks = (client.get(url) for url in pages_url)
            reqs = await asyncio.gather(*tasks)
        
        responses = [req for req in reqs]
        
        return responses

    def parsePages(response):
        nonlocal data
        if DETAIL:
            nonlocal data_detailed
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
        except:
            print("That's all")
            return
        
        if DETAIL:
            try:
                new_data, new_data_detailed = better_fetchPage(soup, DETAIL)
            except TypeError:
                return
            if new_data == 0:
                return
            data += new_data
            data_detailed += new_data_detailed
        else:
            try:
                new_data, new_data_detailed = better_fetchPage(soup, DETAIL)
            except TypeError:
                return
            if new_data == 0:
                return
            data += new_data
    
    responses = asyncio.run(getPages())
    for response in track(responses):
        parsePages(response)
        
    if DETAIL:
        writeCSV(primary_name, data, data_detailed)
    else:
        writeCSV(primary_name, data)