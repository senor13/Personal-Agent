import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv() # reads .env file and loads variables into os.environ


client = OpenAI(api_key = os.environ["OPENAI_API_KEY"])

def call_llm(messages,tools):
    response = client.chat.completions.create(model = "gpt-4o-mini", messages = messages, tools = tools)
   
    return response.choices[0].message,response.usage
    
def call_llm_advanced(messages,tools):
    response = client.chat.completions.create(model = "gpt-4o", messages = messages, tools = tools)
   
    return response.choices[0].message,response.usage

