import google.generativeai as genai
import os
import pandas as pd
import docker
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-pro')
BASE_URL = "C:/Users/dhana/coding/Personal Projects/Scrutiny/client/"

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
    response = model.generate_content(data)
    return response.text
    