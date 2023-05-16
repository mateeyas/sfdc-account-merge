# %%
# Merges accounts with the same name and postal code.
# The data is loaded from a csv-file with these columns:
# Id, Name, BillingPostalCode
# If there are more than two accounts with the same PID,
# the process only merges the first two. To merge the rest,
# a new input file needs to be provided.
# Uses simple_salesforce for authentication.

# %%
# Import packages
from simple_salesforce import Salesforce
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv
import requests
import tkinter as tk
from tkinter import filedialog

# %%
# Set working directory
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

# %%
# Set environment variables
load_dotenv()
SFDC_USERNAME = os.getenv('SFDC_USERNAME')
SFDC_PASSWORD = os.getenv('SFDC_PASSWORD')
SFDC_TOKEN = os.getenv('SFDC_TOKEN')
SFDC_URL = 'https://rs.my.salesforce.com/services/Soap/u/53.0/'

# %%
# Initiate SFDC connection
sf = Salesforce(username=SFDC_USERNAME, password=SFDC_PASSWORD, security_token=SFDC_TOKEN)

# %%
# Load data
root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename()
df = pd.read_csv(file_path)
print(df.shape)

# %%
# Add group index
df['idx'] = df.groupby(['Name', 'BillingPostalCode']).ngroup()

# %%
# Reduce dataframe and generate lists of duplicate accounts
df = df.groupby('idx')['Id'].apply(list).reset_index(name='dupes')

# %%
# Generate list of lists
dupes = df['dupes'].to_list()

# %%
# Only keep first two items in each sublist
# (If there are more, the script will have to be rerun with a new input file)
dupe_pairs = [l[0:2] for l in dupes]

# %%
# Filter out non-pairs
dupe_pairs = [pair for pair in dupe_pairs if len(pair) == 2]

# %%
# Build request and merge
headers = { 
    'Content-Type': 'text/xml', 
    'Accept': 'application/soap+xml,application/dime, multipart/related, text/*', 
    'Authorization': 'Bearer ' + sf.session_id, 
    'SOAPAction': 'merge', 
    'Sforce-Auto-Assign': 'false', 
    'charset':'UTF-8'
}
results = []

for pair in dupe_pairs:
    master_id = pair[0]
    child_id = pair[1]

    body = f"""<?xml version="1.0" encoding="UTF-8"?>
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn="urn:enterprise.soap.sforce.com" xmlns:urn1="urn:sobject.enterprise.soap.sforce.com">
        <soapenv:Header> 
            <urn:SessionHeader>
                <urn:sessionId>{sf.session_id}</urn:sessionId>
            </urn:SessionHeader> 
        </soapenv:Header>
    <soapenv:Body>
        <ns1:merge xmlns:ns1='urn:partner.soap.sforce.com'>
            <ns1:merge>
                <ns1:masterRecord>
                    <ens:type xmlns:ens='urn:sobject.partner.soap.sforce.com'>Account</ens:type>
                    <ens:Id xmlns:ens='urn:sobject.partner.soap.sforce.com'>{master_id}</ens:Id>
                </ns1:masterRecord>
                <ns1:recordToMergeIds>{child_id}</ns1:recordToMergeIds>             
            </ns1:merge>                                   
        </ns1:merge>  
    </soapenv:Body>
    </soapenv:Envelope>"""
    
    try:
        # Send request
        result = {}
        response = sf.session.request(method='POST', url=SFDC_URL, data=body, headers=headers)
        print(response)
        result['pair'] = pair
        result['code'] = response
        result['text'] = response.text
        results.append(result)
    except:
        result = {}
        result['pair'] = pair
        result['code'] = 999
        result['text'] = 'Fail'
        results.append(result)

# %%
# Save results
with open(r'results_' + datetime.today().strftime('%Y-%m-%d-%H-%M-%S') + '.txt', 'w') as f:
    for line in results:
        f.write(f"{line}\n")

# %%
