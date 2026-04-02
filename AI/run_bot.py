import sys
sys.path.append("ai")
from agent import run_agent
from prompts import prompt
from memory import read_memory,extract_memory
sys.path.append("mcp") 
from client import connect_server
import time
from datetime import datetime
import json

process1,process2 = connect_server()
conversation_history = []
memory = read_memory()
stop_flag=[False]
conversation_history.append({"role":"system","content":prompt(memory)})
async def process_message(message):
    start = time.time()
    stop_flag[0]=False
    conversation_history.append({"role":"user","content":message})
    response,updated_history,input_token_count,output_token_count,tool_call_latency = run_agent(conversation_history,process1,process2,stop_flag)
    conversation_history[:] = updated_history
    if response is None:
        return "Stopped."
    end = time.time()
    total_latency = end-start
    
    new_entry = {
        "run_id": datetime.now().isoformat(),
        "input":message,
        "total_latency": total_latency,
        "tool_latency": tool_call_latency,
        "input_token_count":input_token_count,
        "output_token_count":output_token_count,
        "cost_usd": (input_token_count * 0.00000015 + output_token_count * 0.0000006)
    }
    with open("/Users/sagrikasrivastav/Desktop/AI/Personal-Agent/AI/logs/metrics.jsonl","a") as f:
        f.write(json.dumps(new_entry)+"\n")

    
    return response.content
    

    

