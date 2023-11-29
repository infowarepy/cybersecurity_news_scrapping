from config import secret_key
import openai
import pandas as pd
from urllib.parse import urlparse

def link_verification(links):
    openAI_url="https://api.openai.com/v1/chat/completions"

    header={
    'Authorization':'Bearer '+secret_key,
    'Content-Type':'application/json'
    }

    payload={
    'model':'text-davinci-002',
    'messages':[
        {'role':'user','content':'''I will give you a url and you have to check if the link possibly is a news article related to cybersecurity policy/strategy by reading the url only:
Just one word answer
Yes if possible
No, if not'''},
        {'role':'system','content':'Sure, please provide the URL, and I will check if it possibly relates to a news article on cybersecurity policy or strategy.'},
        {'role':'user','content':f'URL={links}'}
    ]}

def filter1(links,country_name):
    filter1_links = list() 
    https_links = [link for link in links if 'https://' in link.lower()] 
    authentic_site_extension = extension_for_url(country_name)
    print("extension name : ",authentic_site_extension)
    com_ex = ['.gov','.org','.eu','itu']
    c_ex = [i for i in authentic_site_extension if i not in com_ex]
    print('length >>>' ,len(c_ex))
    if len(c_ex)<=0:
        c_ex = authentic_site_extension
        first_stage_filter = [link for i in authentic_site_extension for link in https_links if i.lower() in link.lower()]
        first_stage_filter = https_links if len(first_stage_filter) == 0 else first_stage_filter
        filter1_links = list(set(first_stage_filter))
    else:
        first_stage_filter = [link for i in authentic_site_extension for link in https_links if i.lower() in link.lower()]
        first_stage_filter = https_links if len(first_stage_filter) == 0 else first_stage_filter
        filter1_links = list(set(first_stage_filter))
    return filter1_links,c_ex

def extension_for_url(country):

    df = pd.read_csv("WebScrap.csv")
    key =[]
    for i in df['Country']:
        if country.replace(" ",'').lower() in i.lower().replace(" ",''):
            x = (df.loc[(df['Country'] == i )]).values.tolist()
            url_kwy = [i for i in x[0][1:] if str(i) != 'nan']
            key += url_kwy
    ke = list(set(key))
    return ke

def extract_source(url):
    parsed_url = urlparse(url)
    source = parsed_url.netloc 
    return source

def filter_final_news_links(links):
    lst = ['cybersecurity','cybersecurity-act','act','cyber','policy','information','strategies','attacks','threats','security']
    keyword_list = [i for i in lst if str(i) != 'nan']
    url = []
    list = []
    lnk = []
    for link in links:
        str1 = link.split("/")
        if str1[-1]=='':
            s = str1[-2].split('-')
            check = any(item in s for item in keyword_list)
            if check is True:
                lnk.append(link)
        else:
            s = str1[-1].split('-')
            check = any(item in s for item in keyword_list)
            if check is True:
                lnk.append(link)

    return lnk

def filter3(link_list): 
    l = ['linkedin','facebook','twitter','youtube','instagram','wiki','contact','yahoo','whatsapp','login','signin','unodc','cyberwiser.eu']
    q = [link for link in link_list if any(ext in link for ext in l)]
    links = [i for i in link_list if i not in q]
    return links

def filter_sublinks(sublink_list,main_extension):
    df = pd.read_excel("Regulator.xlsx", sheet_name='keywords')
    keyword_list = [i for i in df['Url_keywords'].tolist() if str(i) != 'nan']
    filter2_sublinks = []
    for keyword in keyword_list:
        y = keyword.translate(str.maketrans('', '', string.punctuation))
        for each_sublink in sublink_list:
            if main_extension in each_sublink:
                 filter2_sublinks.append(each_sublink)            
            x = each_sublink.translate(str.maketrans('', '', string.punctuation))
            if y.lower() in x.lower():
                filter2_sublinks.append(each_sublink)
    filter2_sublinks = list(set(filter2_sublinks))
    return filter2_sublinks