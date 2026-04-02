from llm import call_llm
from prompts import prompt
from mock_tools import fetch_calendar,book_slot
import json


def run_agent(query):
    message = query

    tools = [
      {
          "type": "function",
          "function": {
              "name": "fetch_calendar",
              "description": "Get google calendar for a user and find the latest available slot",
              "parameters": {
                  "type": "object",
                  "properties": {
                      "user_email": {
                          "type": "string",
                          "description": "email id of the user whose google calendar is to be accessed"
                      }
                  },
                  "required": ["user_email"]
              }
          }
      },
      {
          "type": "function",
          "function": {
              "name": "book_slot",
              "description": "Book a meeting slot on the calendar",
              "parameters": {
                  "type": "object",
                  "properties": {
                      "user_email": {
                          "type": "string",
                          "description": "email id of the user whose google calendar is to be accessed"
                      },
                      "slot": {
                          "type": "string",
                          "description": "Time in ISO 8601 format (e.g., 2026-03-23T14:30:00Z)"
                      }
                  },
                  "required": ["user_email", "slot"]
              }
          }
      }
  ]
    tool_map = {"fetch_calendar": fetch_calendar,"book_slot":book_slot}
    while True:

        
        
        response = call_llm(message,tools)
        if response.tool_calls:
            tool_name = response.tool_calls[0].function.name
            tool = tool_map[tool_name] ## fetch_tools(process,tool_name)
            tool_output = tool(**json.loads(response.tool_calls[0].function.arguments))
            message.append(response)

            message.append({"role":"tool","content":str(tool_output),"tool_call_id":response.tool_calls[0].id})
        else:
            return response,message

    


