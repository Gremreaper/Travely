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
    model="openai/gpt-oss-20b"
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

# Itinerary agent taking up the contents from flight and hotel agents and creating a travel itinerary for the user
def itinerary_agent(state: TravelState):
    # Create a prompt for the LLM to generate an itinerary based on the flight and hotel results
    prompt = f"""
    You are a travel assistant. Based on the following flight and hotel search results, create a detailed travel itinerary for the user.

    User Query:
    {state['user_query']}

    Flight Results:
    {state['flight_results']}

    Hotel Results:
    {state['hotel_results']}

    Please provide a day-by-day itinerary including activities, dining options, and any other relevant information.
    """

    # Call the LLM to generate the itinerary
    response = llm.invoke([
        SystemMessage(content="You are a helpful travel assistant."),
        HumanMessage(content=prompt)
    ])

    return {
        "itinerary": response.content,
        "messages": [response],
        "llm_calls": state.get("llm_calls", 0) + 1
    }

#Final Agent that would be called to execute the entire travel planning process, calling the flight, hotel and itinerary agents in sequence

def final_agent(state: TravelState):
    final_prompt = f"""
    Generate a final travel response.
    Flights: {state['flight_results']}
    Hotels: {state['hotel_results']}
    Itinerary: {state['itinerary']}
    """

    response = llm.invoke([
        HumanMessage(content= final_prompt)
    ])

    return {
        "messages": [response],
        "llm_calls": state.get("llm_calls", 0) + 1
    }

#Now we would create a langgraph state graph that would represent the entire travel planning process, with the nodes representing the different agents we have created. The edges would represent the flow of data between the nodes.-> how are they connected communicated and all

graph = StateGraph(TravelState)

graph.add_node("flight_agent", flight_agent)
graph.add_node("hotel_agent", hotel_agent)
graph.add_node("itinerary_agent", itinerary_agent)
graph.add_node("final_agent", final_agent)

# Establishing the flow of data between the nodes, ensuring that the output of one agent is passed as input to the next agent in the sequence.

graph.add_edge(START, "flight_agent")
graph.add_edge("flight_agent", "hotel_agent")
graph.add_edge("hotel_agent", "itinerary_agent")
graph.add_edge("itinerary_agent", "final_agent")
graph.add_edge("final_agent", END)

# Now the task of Compilation and memory usage in Post

Database_conn = psycopg.connect(DATABASE_URL, autocommit=True)
checkpointer = PostgresSaver(Database_conn)
checkpointer.setup()

app = graph.compile(checkpointer=checkpointer)

if __name__ == "__main__":
    config = {
        "configurable": {
            "thread_id" : "user_travely"
        }
    }

    user_input = input("Enter your Travel Request:")

    result = app.invoke(
        {
            "messages" : [
                HumanMessage(content=user_input)
            ],
            "user_query" : user_input,
            "flight_results" : "",
            "hotel_results" : "",
            "itinerary" : "",
            "llm_calls" : 0
        },
        config=config
    )

    print("\n Final Response \n")

    for msg in result["messages"]:
        print(msg.content)