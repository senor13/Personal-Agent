from llm import call_llm
from prompts import prompt
import json
import sys                                                                                                                                               
sys.path.append("/Users/sagrikasrivastav/Desktop/AI/Personal-Agent/AI/mcp")
from client import fetch_tools,execute_tools
from tools import save_memory,update_memory,youtube_search
import time
sys.path.append("/Users/sagrikasrivastav/Desktop/AI/Personal-Agent/AI/rag")
from rag import retrieval

def run_agent(query,process1,process2,stop_flag=None):
    message = query

    tool1 = fetch_tools(process1)
    tool2 = fetch_tools(process2)
    custom_tools = [
        {
            "type":"function",
            "function": {
                "name": "book_retrieval_tool",
                "description":"ALWAYS use this tool first when the user asks ANY question about AI, LLMs, agents, RAG, fine-tuning, evaluation, or any technical AI engineering topic. Do not answer from your own knowledge first - retrieve from the book first.",
                "parameters" : {
                    "type":"object",
                    "properties": {
                        "message": {
                            "type": "string" ,
                            "description": "the query asked by the user regarding which the retrieval has to be performed"
                        }
                    },
                    "required":["message"]

                }
            }
        },
        {
            "type":"function",
            "function": {
                "name": "save_memory",
                "description":"save the user input as memory when asked specifically by user to remmeber going forward",
                "parameters" : {
                    "type":"object",
                    "properties": {
                        "category": {
                            "type": "string" ,
                            "description": "the memory category could be about the user, user preferneces etc"
                        },
                        "content":{
                            "type": "string",
                            "description": "the exact information from the user message that is relevant for future and will be saved in memory"
                        }
                    },
                    "required":["category","content"]

                }
            }
        },
        {
            "type":"function",
            "function": {
                "name": "update_memory",
                "description":"update the existing memory whenever user shares updated details",
                "parameters" : {
                    "type":"object",
                    "properties": {
                        "id": {
                            "type": "string" ,
                            "description": "the memory id of the old memories that are saved in json file. It will be used to fetch the content which needs to be replaced."
                        },
                        "new_content":{
                            "type": "string",
                            "description": "the latest or the updated information provided by the user that will be replacing the old memory content in the json file."
                        }
                    },
                    "required":["id","new_content"]

                }
            }

        },
        {
            "type":"function",
            "function": {
                "name": "youtube_search",
                "description":"searches the youtube as per the requests from the user and outputs the filtered videos.",
                "parameters" : {
                    "type":"object",
                    "properties": {
                        "query": {
                            "type": "string" ,
                            "description": "the query asked by the user regarding video search on youtube"
                        },
                        "channel_id":{
                            "type": "string",
                            "description": "the channel id for the channel name shared by the user from which the video needs to be searched"
                        },
                        "published_after":{
                            "type":"string",
                            "description":"time of video published on youtube in ISO 8601 timestamp. Convert relative times like 'last 24 hours' or 'today' to the actual datetime before passing. Example: 'last 24 hours' = current time minus 24 hours in format YYYY-MM-DDTHH:MM:SSZ"
                        },
                        "min_view_count":{
                            "type":"integer",
                            "description":"number of views on a video. needed when user asks videos basis the minimum view count criteria"
                        },
                        "max_results":{
                            "type":"integer",
                            "description":"maxinum number of searched videos shared with the user"
                        },
                        "sort_by_views":{
                            "type":"boolean",
                            "description":"used when user asks for videos basis the maximum number of view count"
                        }
                    },
                    "required":["query"]

                }
            }
        }



    ]
    tools = tool1 + tool2 + custom_tools
    function_map = {"book_retrieval_tool": retrieval, "save_memory": save_memory,"update_memory":update_memory,"youtube_search":youtube_search}
    input_token_count = 0
    output_token_count = 0
    tool_call_latency = 0
    while True:
        if stop_flag and stop_flag[0]:
            return None,message
        response,turn_usage = call_llm(message,tools)
        input_token_count += turn_usage.prompt_tokens
        output_token_count += turn_usage.completion_tokens
        if response.tool_calls:
            start = time.time()
            tool_name = response.tool_calls[0].function.name
            arguments = json.loads(response.tool_calls[0].function.arguments)
            if tool_name in [tool["function"]["name"] for tool in tool1]:
                tool_output = execute_tools(process1,tool_name,arguments)
            elif tool_name in [tool["function"]["name"] for tool in tool2]:
                tool_output = execute_tools(process2,tool_name,arguments)    
            else:
                try:
                    tool_output = function_map[tool_name](**arguments)
                except Exception as e:
                    tool_output = f"Error: {str(e)}"
            end = time.time()
            tool_call_latency += (end-start)
            message.append(response)
            message.append({"role":"tool","content":str(tool_output),"tool_call_id":response.tool_calls[0].id})

        else:
            return response,message,input_token_count,output_token_count,tool_call_latency

    


