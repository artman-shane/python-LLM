import json
import logging
from logging.handlers import RotatingFileHandler
import sys
import os
from urllib.parse import urljoin, urlparse
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from collections import Counter

# Load the environment variablese
load_dotenv()
# Clear screen
os.system('cls' if os.name == 'nt' else 'clear')

# Configure logging
if not os.path.exists(os.getenv("LOGGING_FOLDER")):
    os.makedirs(os.getenv("LOGGING_FOLDER"), exist_ok=True)

try:
    log_file = os.path.join(os.getenv("LOGGING_FOLDER"),os.getenv("LOGGING_FILE"))
    handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=10) # 5MB log files, 10 files
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(str.upper(os.getenv("LOGGING_LEVEL")))
except Exception as e:
    print(f"An error occurred while setting up the logging: {e}")
    print(f"Check the .env file for the LOGGING_FOLDER, LOGGING_FILE, and LOGGING_LEVEL for accuracies.")
    sys.exit(1)


# Feed the URL that you want to start from here
urls=['https://www.twilio.com/en-us/guidelines/sms']

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
            print('Found URL:', found_url)
            logger.debug(f"URLs:{urls}")

            if (found_url.startswith('http') or found_url.startswith('https')):
                logger.info("Starts with http or https")
                if found_url not in urls:  # Check if URL already exists in the list
                    logger.info(f"required_string:{required_string}\nfound_url:{found_url}")
                    if (required_string in found_url if required_string else True):  # Check if URL already exists in the list
                        logger.info("Adding URL:{found_url}")
                        print("Added\n")
                        urls.append(found_url)
                        # Did we add the url?
                        add_url=1
                    else:
                        logger.info("URL not added (does not contain required string): {found_url}")
                        print('URL not added (does not contain required string)')
                else:
                    logger.info("URL not added (duplicate): {found_url}")
                    print('URL not added (duplicate)')
            elif found_url.startswith('/'):
                logger.info("Starts with /")
                
                parsed_url = urlparse(url)
                root_domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
                logger.info(f"Root domain: {root_domain}")
                full_url = urljoin(root_domain, found_url)

                logger.info(f"Full URL:{full_url}")
                logger.info(f"required_string:{required_string}")
                if full_url not in urls:
                    logger.info(f"The URL is NOT in the list of URLs.")
                    logger.info(f"Is required_string in found_url:{str.lower(required_string) in str.lower(full_url)}")
                    if (required_string in full_url if required_string else True):  # Check if URL already exists in the list
                        logger.info(f"Adding URL: {full_url}")
                        print("Added\n")
                        urls.append(full_url)
                        # Simplify the URL for comparison later
                        found_url=full_url
                        # Did we add the url?
                        add_url=1
                    else:
                        logger.info(f"URL not added (does not contain required string): full_url")
                        print('URL not added (does not contain required string):')
                else:
                    logger.info(f"URL not added (duplicate): {full_url}")
                    print("URL not added (duplicate)")

            else:
                logger.info(f"URL not valid: {found_url.strip()}")
                print("URL not valid")

        if add_url==1 or int(len(urls))==1:
            logger.info("Processing document capture")
            add_url=0
            current_document = {}
            current_document['url'] = url
            current_document['title'] = soup.title.string
            # current_document['content'] = soup.get_text()
            documents.append(current_document)

        return urls
    except Exception as e:
        print("\n\nError occurred while making the request to", url, "\nGot error:", str(e), "\nContinuing\n\n")
        logger.info(f"Error occurred while making the request to {url}")
        logger.error(f"Error: {str(e)}")
        return urls


print('\n\n\n\nProcessing:')

# Iterate through the URLs. Note that this will begin with the first
# URL in the list but will continue to add URLs to the list as it finds them
for url in urls:
    # Counter for the number of URLs processed
    urls_processed+=1
    
    # Debugging output
    duplicate_urls = [url for url, count in Counter(urls).items() if count > 1]
    print('Duplicate URLs:', duplicate_urls)
    print('\n\nProcessing URL:', url, ' - #:', urls_processed,' of ',len(urls), ' - Dup URLs:', len(duplicate_urls))

    # Limit the number of pages to MAX_PAGES or 50
    if urls_processed <= int(os.getenv("MAX_PAGES",2)):
        logger.debug(f"Processing URL: {url}")
        print('Processing URL:', url)
        grab_urls(url,required_string='en-us/guidelines')
    else:
        urls_processed-=1
        print('\n\nMax pages reached:', urls_processed, 'URLs processed')
        break

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