# System libraries
import json
import os
from dotenv import load_dotenv
import pandas as pd

# load_dotenv()
print(os.getenv('DEBUG'))
file_path = 'Documents/ans.xlsx'
combined_df = pd.DataFrame()
data2 = str(
    {\"Page 7\": [{\"Page Number\": \"7\", \"ID\": \"G.15\", \"Question\": \"What types of Personal Information (PI) will you access, transmit, process, or store to provide the Services?\", \"Description\": \"\", \"Choices\": \"Name, Address (City, Post Code, Country), Email Address, Phone Number, Social media handle, Date of birth, Age, Gender, Employment Information (e.g., CV/Resume), Credentials (e.g., user name or password), Location data (including GPS Latitude/Longitude), Analytics data (e.g., site traffic report, performance metrics), Behavioral data (e.g., website clicks), Photos, videos, or voice records of an individual, Survey responses, Other - if 'Other', please provide details, None\"}], \"Page 8\": [{\"Page Number\": \"8\", \"ID\": \"G.16\", \"Question\": \"What types of online identifiers will you access, transmit, process or store to provide the Services?\", \"Description\": \"\", \"Choices\": \"IP Address, Advertising ID (e.g., IDFA, GAID, ECID, Roku ID, DPID, EAID, etc.), Device ID, Cookie ID, Other unique IDs (please specify), None\"}, {\"Page Number\": \"8\", \"ID\": \"G.17\", \"Question\": \"What types of Sensitive Personal Information (SPI) will you access, transmit, process, or store to provide the Services?\", \"Description\": \"\", \"Choices\": \"Credit or debit card numbers, Other financial account numbers (e.g., bank accounts, investment accounts, etc), Bank statements, Insurance information (e.g., account number), Passport details/Visa ID, Other official documents (e.g., copies of drivers\' licenses, birth certificates), SSN/National identification numbers, Talent personal contact information or other talent sensitive data, Children\'s data, None\"}], \"Page 9\": [{\"Page Number\": \"9\", \"ID\": \"G.18\", \"Question\": \"What types of Special Categories of Personal Data will you access, transmit, process, or store to provide the Services?\", \"Description\": \"\", \"Choices\": [\"Racial or ethnic origin\", \"Political opinions\", \"Religious, philosophical, or similar beliefs\", \"Trade union membership\", \"Genetic data\", \"Biometric data\", \"Health information (e.g., medical history, disability related information, beneficiary or dependent information, health insurance details etc.)\", \"Sexual life or orientation\", \"Criminal convictions or offences (actual or alleged)\", \"Other (please provide details)\", \"None\"]}], \"Page 10\": [{\"Page Number\": \"10\", \"ID\": \"G.19\", \"Question\": \"What non-Personal Data will you access, transmit, process, or store to provide the Services?\", \"Description\": \"\", \"Choices\": \"Warner Bros. Discovery financial information, Pre-release Media (Scripts, Images, Storyboards, Video/Content), Post-release content, Vendor and supplier contracts (beyond your contract with WBD), Other contracts and deal information, Trade secrets (e.g., product development documentation), WBD/WB Games Source Code, Chat content (e.g., chatbot exchanges, Instant Messaging, texting), Non-public information (please describe), Other (please provide details), None\"}, {\"Page Number\": \"10\", \"ID\": \"G.20\", \"Question\": \"Please describe how WBD Data is sent or transmitted to your system?\", \"Description\": \"\", \"Choices\": \"email, manual upload into a vendor portal, SFTP, etc.\"}, {\"Page Number\": \"10\", \"ID\": \"G.21\", \"Question\": \"Where within your infrastructure is WBD Data stored?\", \"Description\": \"\", \"Choices\": \"cloud storage bucket, data storage, database, etc.\"}], \"Page 11\": [{\"Page Number\": \"11\", \"ID\": \"G.22\", \"Question\": \"Does your service require an integration with any of WBD\'s core production or operating environments, or otherwise require a high level of system access (e.g., admin privileges)?\", \"Description\": \"\", \"Choices\": [\"Yes, through an application interface (e.g. API, SDK, source code)\", \"Yes, through a dedicated interface (e.g. dedicated circuit or network connection, SFTP)\", \"No\"]}, {\"Page Number\": \"11\", \"ID\": \"G.23\", \"Question\": \"Will your service require inserting code on or in a WBD digital service (e.g., SDKs, pixels, tags, JavaScript)?\", \"Description\": \"If yes, please provide details.\", \"Choices\": [\"Yes\", \"No\"]}, {\"Page Number\": \"11\", \"ID\": \"AI.1\", \"Question\": \"What type of AI solution is used to provide your service to WBD (including for optional functionality or functionality provided by a third-party)?\", \"Description\": \"Select all that apply:\", \"Choices\": [\"Deep Learning (e.g., neural networks)\", \"Foundation models (e.g., Large Language Models)\", \"Generative AI (e.g., image generator, code generator)\", \"Machine Learning (e.g., supervised learning, non-supervised learning)\", \"Rules-based Algorithm\", \"Other\", \"N/A - no AI solutions are used to provide service\"]'}
)
data_json = json.loads(data2)
print(f"Only one sheet found...")
print(f"Creating DataFrame...")
df = pd.DataFrame(data2)
print(f"Inserting sheet...")
df.insert(0, 'Sheet Name', "Responses")
print(f"Combining DataFrames...")
combined_df = pd.concat([combined_df, df], ignore_index=True)
print(f"data2 is: {type(data2)}")
print(f"combined_df is: {type(combined_df)}")   
print(f"df is: {type(df)}") 
print(f"data_json is: {type(data_json)}")
print(f"data_json is:\n{data_json}")

print(f"Converting df to logic excel file...")
print(f"\n***** BEGIN Data to write *****\n{combined_df}\n***** END Data to write *****\n")
# Write the DataFrame to an Excel file
combined_df.to_excel(file_path, index=False)
