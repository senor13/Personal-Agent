import json
from datetime import datetime
from pathlib import Path
from llm import call_llm


def add_memory(category, content):

    file = Path("/Users/sagrikasrivastav/Desktop/AI/Personal-Agent/AI/memory/long_term.json")
    if file.exists():
        with open("/Users/sagrikasrivastav/Desktop/AI/Personal-Agent/AI/memory/long_term.json", "r") as f:
            data = json.load(f)
    else:
        data = []
        print("writing to file")
        with open("/Users/sagrikasrivastav/Desktop/AI/Personal-Agent/AI/memory/long_term.json", "w") as file:
            file.write("[]")
    new_entry = {
        "id" : f"mem_{len(data)+1:03d}",
        "category": category,
        "content": content,
        "created_at": datetime.now().isoformat()
    }
    data.append(new_entry)

    with open("/Users/sagrikasrivastav/Desktop/AI/Personal-Agent/AI/memory/long_term.json", "w") as f:
        json.dump(data,f)
    print("add_memory called", category, content)
        

def read_memory():
    file = Path("/Users/sagrikasrivastav/Desktop/AI/Personal-Agent/AI/memory/long_term.json")
    if file.exists():
        with open("/Users/sagrikasrivastav/Desktop/AI/Personal-Agent/AI/memory/long_term.json", "r") as f:
            data =  json.load(f)
            memory_text = ""
            memory_id = []
            for entry in data:
                memory_text += entry["id"]
                memory_text += ": "
                memory_text += entry["content"]
                memory_text += "\n"
                
            return memory_text
    else:
        return ""

def extract_memory(conversation_history):
    prompt = """ 
    Your job is to extract important information from the conversation history which is given. Only extract clear and specific
    facts about the user which is worth remembering long term
    Ignore small talk and questions. 
    Return a JSON list like below example. note that below is just an example so don't save it memory.
    ------
    [{"category":"example_content","content":"example_category"}]
    ------
    Return only raw JSON, no markdown, no code fences
    """
    print("extract_memory_called")
    for_memory = [item for item in conversation_history if item["role"] != "system" ]
    message = for_memory + [{"role":"system","content":prompt}]
    print("check")
    response = call_llm(messages = message,tools = None)
    facts = json.loads(response.content)
    print(response)
    for mem in facts:
        add_memory(mem["category"],mem["content"])
        print("add_memory is called")
    


   
    