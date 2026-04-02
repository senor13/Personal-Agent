import sys
sys.path.append("ai")
from agent import run_agent
from prompts import prompt
from memory import read_memory,add_memory
sys.path.append("mcp") 
from client import connect_server,disconnect_server

memory = read_memory()
conversation_history = []
process1,process2 = connect_server()
conversation_history.append({"role":"system","content":prompt(memory)})
while True:
    user_input = input("Your input: ")
    conversation_history.append({"role":"user","content":user_input})
    response,conversation_history = run_agent(conversation_history,process1,process2)
    print(f"{response.content}")
    if 'exit' in user_input:
        break
disconnect_server(process1)
disconnect_server(process2)
content = input("do you wish to save anything in memory? (press enter to skip) ")
if content:
    category = input("what category it would go into? ")
    add_memory(category,content)

