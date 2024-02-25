import google.generativeai as genai
import os
import pandas as pd
import docker
from dotenv import load_dotenv
# Web3 imports
from web3 import Web3, AsyncWeb3

load_dotenv()
api_key = os.getenv("API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-pro')
BASE_URL = "C:/Users/dhana/coding/Personal Projects/Scrutiny/client/"
NODE_URL = "https://eth-sepolia.g.alchemy.com/v2/YrcRBtPyzQZxWtNt-Cd8sYXh46GSSczW"
w3 = Web3(Web3.HTTPProvider(NODE_URL))

def generate_dataFrame(logFile):
    url = BASE_URL + logFile
    data = []
    with open(url, "r") as file:
        for i, line in enumerate(file):
            try:
                line = eval(line)
                line["uids"] = i
                data.append(line)
            except:
                pass
            
        file.close()
    # print(data)
    # return data
    return pd.DataFrame(data)

def find_vulnerabilities(file_url: str):
    df = generate_dataFrame(file_url)
    data = df.to_string()+" Find the vulnerabilities in the system via the given logs data. Also prettify the text generated in plain text and proper gaps and strips so that It is framed properly"
    # print(data)
    response = model.generate_content(data)
    return response.text
    
def find_anomaly(file_url: str):
    df = generate_dataFrame(file_url)
    data = df.to_string()+" Find the potential granular level anomalies and threats in the system logs from the above data with detailed reasoning and also ignore the codes that does not specify the systems status or is not contributing towards finding the end goal. Also prettify the text generated in plain text and proper gaps and strips so that It is framed properly"
    response = model.generate_content(data)
    return response.text

def getContainerLogs(containerName: str):
    client = docker.from_env()
    container = client.containers.get(containerName)
    # print(client.containers.list(), client.images.list())
    data = container.logs().decode('utf-8')+" Find potential granular vulnerabilities and anomalies in this docker container logs and ignore all the Exceptions and messages of exceptions that does not depict the state of the container only use those data that depicts some vulnerability or status of the container. Also prettify the entire response"
    print(data)
    response = model.generate_content(data)
    return response.text

def read_json(abi: str):
    file = open(abi)
    data = json.load(file)
    file.close()
    return data["abi"]

def getLogVulnerabilities(contract_address="0x61eFE56495356973B350508f793A50B7529FF978", fromBlock=0, toBlock="latest"):
    # contractwithsigner = w3.eth.contract(address=address, abi=abi)
    # bytecode_data = w3.eth.get_code(address).hex()+" Find potential security vulnerabilities in the given smart contract bytecode as detailed as you can in clean and precise language"
    # print(bytecode_data)
    # response = model.generate_content(bytecode_data)
    # Filter for all logs from the contract, starting from block 0 to the latest block
    filter = {
        'fromBlock': fromBlock,
        'toBlock': toBlock,
        'address': contract_address,
    }

    # response = model.generate_content(logs)
    # print(response.text)
    
def getCodeVulnerabilities(filename: str):
    file = open(filename, "r")
    sol_content = file.read()+" security audit the given smart contract with granular details and clear, easy and subtle explanation"
    file.close()
    response = model.generate_content(sol_content)
    return response.text

    
    
    