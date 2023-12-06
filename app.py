from googlesearch import search
from bs4 import BeautifulSoup
import requests
import pandas as pd
import csv
from utils import *
from urllib.parse import urlparse
from datetime import datetime,timedelta
import json
API_KEY='01a425686ae74b939601e6adf09e9b7b'


def extract_newsapi_links(country_name):
    api_links=[]

    url=f'https://newsapi.org/v2/everything?q=cybersecurity+AND+{country_name}+AND+cyber&from={get_date(3)}&sortBy=popularity&apiKey={API_KEY}'
    response = requests.get(url)
    response_json=response.json()
    articles_data=reduce_json(response_json,response_json['totalResults'])

    for i,article in enumerate(articles_data['articles']):
        api_links.append(article['url'])    
    print('newsapi links done')
    return api_links

def extract_google_links(country_name):
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
    tld=country_tld[country_name]
    query=f"cybersecurity news articles in \"{country_name}\" "# \" site:{source}"
    # query='"united kingdom" site:https://www.cshub.com/'
    print('>>>',query)
    news_links=[]
    c=0
    # for link in search(query, tld="co.in", num=1, stop=10, pause=2,tbs='qdr:w',user_agent='your bot 0.1'):
    # for link in search(query, num=20, stop=20, pause=5,tbs='qdr:w',user_agent='your bot 0.2',verify_ssl=False,country='nl'):
    for link in search(query, num=20, stop=20, pause=5,tbs='qdr:m',user_agent='your bot 0.2',country=tld,tld=tld):
        news_links.append(link)
        c=c+1
        print('News Links fetched:',c,end='\r')

    return news_links

def extract_regulator_based_links(country_name):
    file=open('static/country_codes.json','r')
    country_code=json.load(file)

    regulator=pd.read_excel('REGULATORS (3).xlsx')
    filtered_data = regulator[regulator['COUNTRY_CODE'] == country_code['India']]
    links=[]
    for regulator_name in filtered_data['REGULATOR_NAME']:
        url = filtered_data.loc[filtered_data['REGULATOR_NAME'] == regulator_name, 'REGULATOR_WEB_URL'].values
        if len(url) > 0 and str(url[0])!='nan':
            links.append(url[0])
        
    
    return links
        

def get_news_links(country_name):
    newsapi_links=extract_newsapi_links(country_name)
    google_links=extract_google_links(country_name)
    regulator_based_links=extract_regulator_based_links(country_name)
    links=newsapi_links+google_links+regulator_based_links
    # filter1_links=filter1(links,country_name)
    # filter3_links=filter3(filter1_links[0])
    final_news_links=filter_final_news_links(links)
    sublinks=extract_news_sublinks(final_news_links)
    final_news_links=final_news_links+sublinks
    return final_news_links



def get_json(final_news_links,country_name):
    json_data={
        'country':country_name,
        'noOfResults':len(final_news_links),
        'articles':[]
        }
    for news_link in final_news_links:
        link_dict={}
        source=extract_source(news_link)
        link_dict['url']=news_link
        link_dict['source']=source
        json_data['articles'].append(link_dict)
    
    return json_data


 
def log_data(cnt):
    new_log_filename=f'[{get_date(0)}] news_links.csv'
    with open(f"{new_log_filename}", "w",newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Country','JSON'])
    for country in cnt["Country_Name"]:
        print(country)
        try:
            news_links=get_news_links(country)
            json_data=get_json(news_links,country)
            log_data=[country,json_data]
            print(f'{country} Raw Links = {len(news_links)}')
            with open(new_log_filename, "a",newline='') as f:
                writer = csv.writer(f)
                writer.writerow(log_data)
        except Exception as e:
            print(f'error in {country}',e)

if __name__ == '__main__':        
    cnt = pd.read_csv('country.csv')
    log_data(cnt)
    
