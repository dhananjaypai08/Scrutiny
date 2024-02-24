from pandasai import PandasAI
import pandas as pd
from pandasai.llm.openai import OpenAI

api_key = "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"
llm = OpenAI(api_token=api_key)
pandas_ai = PandasAI(llm)
df = pd.read_csv(r"C:\Users\dhana\coding\Personal Projects\Scrutiny\response.csv")
response = pandas_ai.run(imported_data, prompt="Find anomalies in the given logs dataset and also give the quality of the logs")
print(response)