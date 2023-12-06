from config import secret_key
import openai
import datetime
from datetime import datetime,timedelta
import string
import pandas as pd
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import time

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

def get_date(days):
    today_date = datetime.now()
    new_days_ago = today_date - timedelta(days)
    new_days_ago_format = new_days_ago.strftime('%Y-%m-%d')
    return new_days_ago_format

def reduce_json(json_data, max_results):
    # Check if 'articles' key is present
    if json_data['totalResults'] == max_results:
        return json_data
    
    if 'articles' in json_data and json_data['totalResults'] > max_results:
        json_data['articles'] = json_data['articles'][:max_results]
        json_data['totalResults'] = max_results
    else:
        reduce_json(json_data, max_results-1)
    
    return json_data

def filter1(links,country_name):
    filter1_links = list() 
    https_links = [link for link in links if 'https://' in link.lower()] 
    authentic_site_extension = extension_for_url(country_name)
    print("extension name : ",authentic_site_extension)
    com_ex = ['.gov','.org','.eu','itu']
    c_ex = [i for i in authentic_site_extension if i not in com_ex]
    print('length >>>' ,len(c_ex))
    print('c_ex>>>>>',c_ex)
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

def take_url_keyword():
    data_key = pd.read_excel('Regulator.xlsx',sheet_name='keywords')
    url_keyword = []
    for i in data_key['news_url_keywords']:
        if str(i) == 'nan':
            pass
        else:
            url_keyword.append(i)
            
def extract_news_sublinks(links): #,c_ex):
    news_links = []
    #------------------extract sublinks---------------------------------
    for link in links:
        print("URL for news ------------------>>>>>>> ",link)

        options = webdriver.ChromeOptions()
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")
        # driver = webdriver.Chrome(chrome_options=options,service=ChromeService(ChromeDriverManager(version="114.0.5735.90").install()))
        driver = webdriver.Chrome(service= Service(ChromeDriverManager().install()))
        driver.maximize_window()
        driver.get(link)
        driver.set_page_load_timeout(60)
        time.sleep(1)
        current_link = driver.current_url

        list_=[] 
        lnk=driver.find_elements(By.XPATH, "//a[@href]")
        try:
            for i in lnk:
                list_.append(str(i.get_attribute('href'))) 
        except:
            pass
        final_list = [link]+list_
        sublink_list = list(set(final_list))
        driver.quit()

        # print("raw_sublink >>> ",sublink_list)
        print("sublink list :",len(sublink_list))
        filter1_links,c_ex=filter1(sublink_list,'Italy')
        Filter_Sublinks = filter_sublinks(filter1_links,c_ex[0])
        u_filter_sublinks = filter3(sublink_list)
        https_filtersublinks = [sublink for sublink in u_filter_sublinks if 'https://' in sublink.lower()]

        print("sublinks after filter >>>>>>>>>>>>>>> ",https_filtersublinks)
        print("len of filter sublink :",len(https_filtersublinks))

        url_keyword=take_url_keyword()
        for lnk in https_filtersublinks:
            check_data = any(item in lnk for item in url_keyword)
            if check_data == True:
                news_links.append(lnk)
    
    nws_lnk = []
    for i in news_links:
        if i not in nws_lnk:
            if '#' in i:
                pass
            else:
                nws_lnk.append(i) 
    nws_lnk_1 = filter_final_news_links(nws_lnk)
    print("len>>>>>>>>",len(nws_lnk_1))
    return nws_lnk_1
    #-------------------for news inner sub links------------------------------
#     for l in nws_lnk_1:
#         print("URL for news ------------------>>>>>>> ",l)
        
#         options = webdriver.ChromeOptions()
#         options.add_argument("--headless")
#         options.add_argument('--ignore-certificate-errors')
#         options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")
#         driver = webdriver.Chrome(options=options,service= Service(ChromeDriverManager().install()))
#         driver.minimize_window()
#         driver.get(l)
#         driver.set_page_load_timeout(60)
#         time.sleep(2)
#         current_link = driver.current_url       
        
#         list_=[] 
#         lnk=driver.find_elements(By.XPATH, "//a[@href]")
#         try:
#             for i in lnk:
#                 list_.append(str(i.get_attribute('href'))) 
#         except:
#             pass
#         final_list = [l]+list_
#         sublink_list = list(set(final_list))
#         driver.quit()

#         # print("raw_sublink >>> ",sublink_list)
#         print("sublink list :",len(sublink_list))
#         filter1_links,c_ex=filter1(sublink_list,'Italy')
#         Filter_Sublinks = filter_sublinks(filter1_links,c_ex[0])
#         u_filter_sublinks = filter3(Filter_Sublinks)
#         https_filtersublinks = [sublink for sublink in u_filter_sublinks if 'https://' in sublink.lower()]

#         print("sublinks after filter >>>>>>>>>>>>>>> ",https_filtersublinks)
#         print("len of filter sublink :",len(https_filtersublinks))
        
#         for http_lnk in https_filtersublinks:
#             check_data = any(item in http_lnk for item in url_keyword)
#             if check_data == True:
#                 news_links.append(http_lnk)
        
#     nws_l = []
#     for i in news_links:
#         if i not in nws_l:
#             if '#' in i:
#                 pass
#             else:
#                 nws_l.append(i)
    
#     filter_news_sub_link = filter_final_news_links(nws_l)

#     return list(set(filter_news_sub_link))
