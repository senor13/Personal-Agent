import json
import sys
sys.path.append("ai") 
from agent import run_agent
from prompts import prompt
from memory import read_memory,extract_memory
sys.path.append("mcp") 
from client import connect_server
from pathlib import Path
from llm import call_llm_advanced
from datetime import datetime

def judge_response(actual_response,expected_outcome):
    system_prompt = """ You have to act as judge. Your task is to compare the actual response and expected response and 
    generate a score from 1-5 (1 is worst and 5 is best) basis how well the actual and rexpected responses are matching.
    """
    message = [{"role":"system","content":system_prompt}]
    message.append({"role":"user","content":"actual_response is: " + actual_response + " ; expected response is: " + expected_outcome})
    result = call_llm_advanced(message,tools = None)
    return result.content

file = Path("/Users/sagrikasrivastav/Desktop/AI/Personal-Agent/AI/evals/test_cases.json")
if file.exists():
    with open("/Users/sagrikasrivastav/Desktop/AI/Personal-Agent/AI/evals/test_cases.json","r") as f:
        data = json.load(f)
else:
    print("test_cases file doesnot exists")
process1,process2 = connect_server()


for case in data:
    query = case["input"]
    conversation_history = []
    memory = read_memory()
    conversation_history.append({"role":"system","content":prompt(memory)})
    conversation_history.append({"role":"user","content":query})
    response,updated_history = run_agent(conversation_history,process1,process2,stop_flag = None)
    conversation_history[:] = updated_history

    tools_called = []
    for item in conversation_history:
        if not isinstance(item,dict) and item.role == "assistant" and item.tool_calls:
            for tool in item.tool_calls:
                tools_called.append(tool.function.name)

    if tools_called == case["expected_tool_sequence"]:
        tool_eval = f"Correct sequence of tools called for {case["id"]}"
    else:
       tool_eval = f"failed to pull the correct sequence of tools for {case["id"]}"

    llm_response = judge_response(response.content,case["expected_outcome"])
    llm_eval = f"Score from LLM Judge for {case["id"]} is : {llm_response}"

    file = Path("/Users/sagrikasrivastav/Desktop/AI/Personal-Agent/AI/evals/results.json")
    if file.exists():
        with open("/Users/sagrikasrivastav/Desktop/AI/Personal-Agent/AI/evals/results.json", "r") as f:
            entry = json.load(f)
    else:
        entry = []
        print("writing to file")
        with open("/Users/sagrikasrivastav/Desktop/AI/Personal-Agent/AI/evals/results.json", "w") as file:
            file.write("[]")
    new_entry = {
        "id" : f"eval_{len(entry)+1:03d}",
        "input":case["input"],
        "case id": case["id"],
        "tool_eval": tool_eval,
        "response_eval": llm_eval,
        "created_at": datetime.now().isoformat()
    }
    entry.append(new_entry)
    with open("/Users/sagrikasrivastav/Desktop/AI/Personal-Agent/AI/evals/results.json", "w") as f:
        json.dump(entry,f)
    print("eval result added")


