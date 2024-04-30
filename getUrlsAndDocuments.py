import json
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import pickle
from collections import Counter

# Load the environment variablese
load_dotenv()


# Feed the URL that you want to start from here
urls=['https://security.twilio.com']

# Initialize the list of documents and URLs for temp storage
documents = []
found_urls = []

# initialize the number of URLs processed
urls_processed=0

# Function to grab URLs from a page
def grab_urls(url,required_string=None):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        link_elements = soup.select("a[href]")
        # Test if URL was added or not to the urls list. Duplicates will be skipped. Used to process document capture
        add_url=0

        for link_element in link_elements:
            found_url = link_element['href'].strip()

            if (found_url.startswith('http') or found_url.startswith('https')) and (required_string in found_url if required_string else False):

                if found_url not in urls:  # Check if URL already exists in the list

                    print('Adding URL:', found_url) if os.getenv('DEBUG').lower() == "true" else None
                    urls.append(found_url)
                    # Did we add the url?
                    add_url=1
                    
                else:
                    print('URL not added (duplicate):', found_url) if os.getenv('DEBUG').lower() == "true" else None

            elif found_url.startswith('/'):
                full_url = url + found_url

                if full_url not in urls and (required_string in found_url if required_string else True):  # Check if URL already exists in the list
                    print('Adding URL:', full_url) if oos.getenv('DEBUG').lower() == "true" else None
                    urls.append(full_url)
                    # Simplify the URL for comparison later
                    found_url=full_url
                    # Did we add the url?
                    add_url=1

                else:
                    print('URL not added (duplicate):', full_url) if os.getenv('DEBUG').lower() == "true" else None

            else:
                print('URL not added:', found_url) if os.getenv('DEBUG').lower() == "true" else None

        if add_url==1 or int(len(urls))==1:
            print("Processing document capture for URL:", url) if os.getenv('DEBUG').lower() == "true" else None
            add_url=0
            current_document = {}
            current_document['url'] = url
            current_document['title'] = soup.title.string
            current_document['content'] = soup.get_text()
            documents.append(current_document)

        return urls
    except Exception as e:
        print("\n\nError occurred while making the request to", url, "\nGot error:", str(e), "\nContinuing\n\n")
        return urls

print("*****  DEBUG NOTICE - DEBUGGING:", os.getenv('DEBUG')) if os.getenv('DEBUG').lower() == "true" else None

print('\n\n\n\nProcessing:')

# Iterate through the URLs. Note that this will begin with the first
# URL in the list but will continue to add URLs to the list as it finds them
for url in urls:
    # Counter for the number of URLs processed
    urls_processed+=1
    
    # Debugging output
    if os.getenv('DEBUG').lower() == "true":
        duplicate_urls = [url for url, count in Counter(urls).items() if count > 1]
        print('\n\nProcessing URL:', url, ' - #:', urls_processed,' of ',len(urls), ' - Dup URLs:', len(duplicate_urls))

    # Limit the number of pages to MAX_PAGES or 50
    if urls_processed <= int(os.getenv("MAX_PAGES",50)):
        grab_urls(url,required_string='twilio.com')
    else:
        urls_processed-=1
        print('\n\nMax pages reached:', urls_processed, 'URLs processed')
        break

    print('.', end='', flush=True) if os.getenv('DEBUG').lower() == "false" else None

print('\n\n Processed', urls_processed, 'URLs')

output_dir = os.getenv('OUTPUT_DIR',"output/")
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Handle output for URLs
url_output_file = os.path.join(output_dir, os.getenv("URLS_FILE","urls.txt"))
if os.path.exists(url_output_file):
    os.remove(url_output_file)

with open(url_output_file, 'w') as file:
    for url in urls:
        file.write(url + '\n')

# Handle output for documents
documents_output_file = os.path.join(output_dir, os.getenv("DOCUMENTS_FILE",'documents.json'))
if os.path.exists(documents_output_file):
    os.remove(documents_output_file)

with open(documents_output_file, 'w') as file:
    json.dump(documents, file, indent=4)



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