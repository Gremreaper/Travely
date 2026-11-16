import os 
from typing import TypedDict, Annotated
import operator

import psycopg
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_core.messages import (
    AnyMessage,
    HumanMessage,
    AIMessage,
    SystemMessage,
)

from langchain_groq import ChatGroq

from Tools.tavily_tool import tavily_search
from Tools.flight_tool import search_flights

from dotenv import load_dotenv
load_dotenv()

llm = ChatGroq(
    model = "llama - 3 .3- 70b-versatile"
)

DATABASE_URL = os.getenv("DATABASE_URL")

# We would create a state in Langgraph where we use the same memory and update it with every task we want

class TravelState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    user_query: str
    flight_results: str
    hotel_results: str
    itinerary: str
    llm_calls: int 

# Now we would be creating Nodes -> as a part of the state graph, we would create nodes that would represent the different tasks we want to perform. Each node would have a function that would be called when the node is executed. The function would take in the current state and return a new state.These would act as at the agents

def flight_agent(state: TravelState) -> TravelState:
    # Call the flight search tool
    query = state["user_query"]
    flight_data = search_flights(query)
    return {
        "flight_results": flight_data,
        "messages": [
            AIMessage(content=f"Flight search results fetched")
        ],

        # Used to check if LLM calls are being made, and to keep track of the number of calls made to the LLM
        "llm_calls": state.get("llm_calls", 0) + 1
    }

def hotel_agent(state: TravelState):
    query = f"Best hotels for {state['user_query']}"
    hotel_results = tavily_search(query)
    return {
        "hotel_results" : hotel_results,
        "messages": [
            AIMessage(content=f"Hotel search results fetched")
        ],
        "llm_calls": state.get("llm_calls", 0) + 1
    }