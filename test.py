# System libraries
import json
import os
from dotenv import load_dotenv
import pandas as pd

# load_dotenv()
print(os.getenv('DEBUG'))
file_path = 'Documents/ans.xlsx'
combined_df = pd.DataFrame()
data2 = str(['{\n  "question": {\n    "number": "1.1",\n    "question": "What is your Organization\'s Registered Name & Trading Name?",\n    "description": "Please include Trading Name in the format \\"Registered Name t/a Trading Name\\" where applicable",\n    "answer": {\n      "response": "Twilio Inc. trading as Lithia US",\n      "justification": "Twilio Inc. is commonly trading under the name Lithia US in certain business operations.",\n      "Control Family": "Business Continuity",\n      "Control Attribute": "Information Security",\n      "shared assessments SC": "n/a",\n      "ISO 27001:2022": "n/a",\n      "other references": "n/a"\n    }\n  }\n}', '{\n  "Question": "1.2 In what country is your organizations headquarters? (Single selection allowed) *",\n  "Description": null,\n  "Unique Identifier": "943ad95e-061b-47ef-a305-50626df95e1a",\n  "Response": null,\n  "Justification": null,\n  "Question Type": "Attribute - single select",\n  "new_id": "Assessment Responses - v2 (2)",\n  "Answer": {\n    "response": "Information not available in the provided document",\n    "justification": "The document does not contain specifics about the headquarters location of the organization.",\n    "control_family": "General Information",\n    "control_attribute": "Organizational Information"\n  }\n}', '{\n  "Question": "1.3 In what US state is your organizations headquarters? (Single selection allowed) *",\n  "Description": null,\n  "Unique Identifier": "edbd4f15-6ad1-4c51-a507-b588bb2afbc2",\n  "Response": "California",\n  "Justification": "Twilio Inc., known for cloud communications and customer engagement platforms, is headquartered in California.",\n  "Question Type": "Attribute - single select",\n  "new_id": "Assessment Responses - v2 (2)",\n  "Control Family": "Company Information",\n  "Control Attribute": "Geographic Location",\n  "Shared Assessments SC": null,\n  "ISO 27001:2022": null,\n  "References": null\n}', '{\n  "Question": "1.4 What is the postal/mailing address of your organizations headquarters? *",\n  "Description": "Please provide the complete postal/mailing address of the organization headquarters",\n  "Unique Identifier": "9482ea6c-40fb-4142-8c43-7c03f777b679",\n  "Response": "The postal/mailing address for Twilio\'s headquarters is: 375 Beale Street, Suite 300, San Francisco, CA 94105, USA.",\n  "Justification": "This is the official registered address of the organization as required for communications and official matters.",\n  "Question Type": "Attribute",\n  "new_id": "Assessment Responses - v2 (2)",\n  "Control Family": "Organizational",\n  "Control Attribute": "Administrative",\n  "Shared Assessments SC": null,\n  "ISO 27001:2022": null\n}'])
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
