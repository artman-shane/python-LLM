import os
import time
import requests
from bs4 import BeautifulSoup
import pickle
from collections import Counter
from dotenv import load_dotenv
load_dotenv()


urls=['https://www.twilio.com/docs/flex/developer']
documents = []
found_urls = []

# print("URLS to process: ", urls)
def grab_urls(url,required_string=None):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    link_elements = soup.select("a[href]")
    for link_element in link_elements:
        found_url = link_element['href'].strip()
        if found_url.startswith('http') or found_url.startswith('https') and (required_string in found_url if required_string else True):
            if found_url not in urls:  # Check if URL already exists in the list
                print('Adding URL:', found_url) if os.getenv('DEBUG_LIST_ADDITIONS') else None
                urls.append(found_url)
            else:
                print('URL not added (duplicate):', found_url) if os.getenv('DEBUG_LIST_ADDITIONS') else None
        elif found_url.startswith('/'):
            full_url = url + found_url
            if full_url not in urls and (required_string in found_url if required_string else True):  # Check if URL already exists in the list
                print('Adding URL:', full_url) if os.getenv('DEBUG_LIST_ADDITIONS') else None
                urls.append(full_url)
            else:
                print('URL not added (duplicate):', full_url) if os.getenv('DEBUG_LIST_ADDITIONS') else None
        else:
            print('URL not added:', found_url) if os.getenv('DEBUG_LIST_ADDITIONS') else None
    return urls
x=0
print('Processing:')
for url in urls:
    x+=1
    duplicate_urls = [url for url, count in Counter(urls).items() if count > 1]
    print('\n\nProcessing URL:', url, ' - #:', x,' of ',len(urls), ' - Dup URLs:', len(duplicate_urls)) if os.getenv('DEBUG_LIST_URLS') else None
    grab_urls(url,required_string='twilio.com')
    print('.', end='', flush=True) if not os.getenv('DEBUG') else None

print("URLS:", urls)
with open('urls.txt', 'w') as file:
    for url in urls:
        file.write(url + '\n')


# while len(urls) != 0:
#     print('How many times are we here?', len(urls))
#     current_url = urls.pop()
#     response = requests.get(current_url)
#     soup = BeautifulSoup(response.content, 'html.parser')

#     link_elements = soup.select("a[href]")

#     for link_element in link_elements:
#         url = link_element['href']
#         if (url.startswith('http') or url.startswith('https') or url.startswith('/')) and url not in urls:
#             # print('Adding URL:',url)
#             urls.append(url)
#             # print('Currently there are ', len(urls), 'URLs to process')
    
#     # print('Processing URL:', current_url)
#     print('Currently there are ', len(urls), 'URLs to process')
#     # print('Found document with title', soup.title.string)
#     current_document = {}
#     current_document['url'] = current_url
#     current_document['title'] = soup.title.string
#     current_document['content'] = soup.get_text()

#     documents.append(current_document)

#     # print(documents)
#     # with open('documents.json', 'wb') as file:
#     #     pickle.dump(documents, file, pickle.HIGHEST_PROTOCOL)

#     print('Processed page and found', len(documents), 'documents')
#     break