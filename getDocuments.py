import json
import logging
from logging.handlers import RotatingFileHandler
import sys
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from collections import Counter
import re
import csv

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


# Read in a file of strings and add each string to the urls list
urls_file = os.getenv("URLS_FILE_PATH", "output/urls.txt")
if os.path.exists(urls_file):
    with open(urls_file, 'r') as file:
        urls = [line.strip() for line in file.readlines()]
else:
    print(f"URLs file not found at path: {urls_file}")
    logger.error(f"URLs file not found at path: {urls_file}")
    sys.exit(1)

# Initialize the list of documents and URLs for temp storage
documents = []

# Function to grab URLs from a page
def grab_doc(url):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            logger.error(f"Failed to retrieve {url} with status code {response.status_code}")
            print(f"Failed to retrieve {url} with status code {response.status_code}")
            return None
        soup = BeautifulSoup(response.content, 'html.parser')
        logger.info("Processing document capture")
        print(f"Processing document capture: {url}")
        current_document = {}
        current_document['url'] = url
        current_document['title'] = soup.title.string
        current_document['tables'] = []

        for table in soup.find_all('table'):
            table_data = []
            headers = [header.get_text(strip=True) for header in table.find_all('th')]
            rows = table.find_all('tr')
            
            for row in rows:
                columns = row.find_all(['td', 'th'])
                row_data = [column.get_text(strip=True) for column in columns]
                table_data.append(row_data)
            
            # Remove redundant header row if it exists in rows
            if table_data and headers and table_data[0] == headers:
                table_data = table_data[1:]
            
            table_dict = {
            'headers': headers,
            'rows': table_data
            }
            current_document['tables'].append(table_dict)
        print(f"Returning document")
        return current_document
    
    except Exception as e:
        print("\n\nError occurred while making the request to", url, "\nGot error:", str(e), "\nContinuing\n\n")
        logger.info(f"Error occurred while making the request to {url}")
        logger.error(f"Error: {str(e)}")
        return urls
    
def clean_json(json_str):
    # Clean JSON
    # Use regular expression to find the first '{' and the last '}'
    # Remove duplicated \n characters
    logger.debug(f"Cleaning JSON for {json_str}")
    json_str = re.sub(r'\\n+', '\\n', json_str)
    json_str = re.sub(r'\\t+', '\\t', json_str)
    json_str = re.sub(r'\n+', '\n', json_str)
    json_str = re.sub(r'\t+', '\t', json_str)
    logger.debug(f"Cleaned JSON: {json_str}")

    # Use regular expression to find the first '{' and the last '}'
    match = re.search(r'[\{,\[].*[\},\]]', json_str, re.DOTALL)
    if match:
        logger.info(f"Returning cleaned JSON")
        return match.group(0)
    else:
        raise ValueError("Invalid JSON format")


print('\n\n\n\nProcessing:')

# Iterate through the URLs. Note that this will begin with the first
# URL in the list but will continue to add URLs to the list as it finds them
for url in urls:
    # Counter for the number of URLs processed    
    results = grab_doc(url)
    results = clean_json(json.dumps(results))
    documents.append(results)

output_dir = os.getenv('OUTPUT_DIR',"output/")
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Handle output for documents
documents_output_file = os.path.join(output_dir, os.getenv("DOCUMENTS_FILE",'documents.json'))
if os.path.exists(documents_output_file):
    os.remove(documents_output_file)

with open(documents_output_file, 'w') as file:
    json.dump(documents, file, indent=4)


# Function to write documents to CSV
def write_documents_to_csv(documents, output_csv_file):
    with open(output_csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write headers
        writer.writerow(['URL', 'Title', 'Table Headers', 'Table Rows'])
        
        for doc in documents:
            doc = json.loads(doc)  # Convert JSON string back to dictionary
            url = doc.get('url', '')
            title = doc.get('title', '')
            for table in doc.get('tables', []):
                headers = ', '.join(table.get('headers', []))
                for row in table.get('rows', []):
                    writer.writerow([url, title, headers, ', '.join(row)])

# Define the output CSV file path
documents_csv_file = os.path.join(output_dir, os.getenv("DOCUMENTS_CSV_FILE", 'documents.csv'))

# Write documents to CSV
write_documents_to_csv(documents, documents_csv_file)