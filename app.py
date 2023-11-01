from googlesearch import search
from bs4 import BeautifulSoup
import requests
import pandas as pd
import csv
from utils import *
from urllib.parse import urlparse


def extract_news(country):
    country_tld = {
    'India': 'in',
    'Singapore': 'sg',
    'United States': 'us',
    'Netherlands': 'nl',
    'Luxembourg': 'lu',
    'Norway': 'no',
    'Spain': 'es',
    'United Kingdom': 'uk',
    'South Korea': 'kr',
    'Belgium': 'be',
    'Turkey': 'tr',
    'Finland': 'fi',
    'Greece': 'gr',
    'Iceland': 'is',
    'Italy': 'it',
    'Portugal': 'pt',
    'Denmark': 'dk',
    'Mexico': 'mx',
    'New Zealand': 'nz',
    'Sweden': 'se',
    'Austria': 'at',
    'Ireland': 'ie',
    'Slovakia': 'sk',
    'Czechia': 'cz',
    'Chile': 'cl',
    'Estonia': 'ee',
    'Hungary': 'hu',
    'Israel': 'il',
    'Slovenia': 'si',
    'Australia': 'au',
    'Canada': 'ca',
    'Japan': 'jp',
    'Latvia': 'lv',
    'Lithuania': 'lt'
}
    query=f"cybersecurity policy/strategy news in \"{country}\""
    print('>>>',query)
    news_links=[]
    c=0
    # for link in search(query, tld="co.in", num=1, stop=10, pause=2,tbs='qdr:w',user_agent='your bot 0.1'):
    for link in search(query, num=20, stop=20, pause=5,tbs='qdr:w',user_agent='your bot 0.2',verify_ssl=False,country=country_tld[country]):
        news_links.append(link)
        c=c+1
        print('Links fetched:',c,end='\r')

    return news_links



def log_data(cnt):
    for country in cnt["Country_Name"]:
        news_links=extract_news(country)
        filter1_links=filter1(links=news_links,country_name=country)        
        log_data=[country,news_links,filter1_links]
        print(f'{country} Raw Links = {len(news_links)}, Filter1 Links = {len(filter1_links[0])}')
        with open("news_links_2.csv", "a",newline='') as f:
                writer = csv.writer(f)
                writer.writerow(log_data)

cnt = pd.read_csv('country.csv')
log_data(cnt)