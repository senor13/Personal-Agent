import subprocess
import json
import time
import os
from dotenv import load_dotenv

load_dotenv()
def connect_server():
    process1 = subprocess.Popen(["npx", "@cocal/google-calendar-mcp"],
    stdin = subprocess.PIPE,
    stdout = subprocess.PIPE,
    stderr = subprocess.PIPE,
    env = {**os.environ,"GOOGLE_OAUTH_CREDENTIALS": os.environ["GOOGLE_OAUTH_CREDENTIALS"]})
    process2 = subprocess.Popen(["npx", "@instructa/mcp-youtube-music"],
    stdin = subprocess.PIPE,
    stdout = subprocess.PIPE,
    stderr = subprocess.PIPE,
    env = {**os.environ,"YOUTUBE_API_KEY": os.environ["YOUTUBE_API_KEY"]}
    )
    time.sleep(3)                                                                                                                        
    return process1,process2


def fetch_tools(process):
    tool_list = {
        "jsonrpc":"2.0",
        "id":int(time.time()*1000),
        "method":"tools/list",
        "params": {}
    }
    message = json.dumps(tool_list) + "\n"
    
    process.stdin.write(message.encode())
    process.stdin.flush()
    response = process.stdout.readline()
    tool_response =  json.loads(response)
    mcp_tools = tool_response["result"]["tools"]
    tools = []
    for tool in mcp_tools:
        tools.append({

            "type": "function",
            "function" : {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["inputSchema"]
            }
            
        }
        )
    return tools

def execute_tools(process,tool_name,arguments):
    tool_call = {
        "jsonrpc": "2.0",
        "id" : int(time.time()*1000),
        "method":"tools/call",
        "params":{
            "name": tool_name,
            "arguments":arguments
        }
    }

    message = json.dumps(tool_call) + "\n"
    process.stdin.write(message.encode())
    process.stdin.flush()

    response = process.stdout.readline()
    return json.loads(response)

def disconnect_server(process):
    process.stdin.close()
    process.wait()
   

