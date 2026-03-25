from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools import google_search
from sub_agents.planning.prompts import (
    instructions_flight_planner,
    itenary_agent_instruction,
    planning_agent_instruction,
)
from tools.scrapper import search_google_flights, search_iata_code_airpots_city, user_selected_flight

flight_planner_agent = Agent(
    model="gemini-2.5-flash",
    name="flight_planner_agent",
    description="A flight planner agent that can search for flights and return the flight information.",
    static_instruction=instructions_flight_planner,
    tools=[search_google_flights, search_iata_code_airpots_city, user_selected_flight],
    output_key="flight_information",
)


itenary_agent = Agent(
    model="gemini-2.5-flash",
    name="itenary_agent",
    description="A itenary agent that can create a itenary for the user.",
    static_instruction=itenary_agent_instruction,
    tools=[google_search],
)

planning_agent = Agent(
    model="gemini-2.5-flash",
    name="planning_agent",
    description="A planning agent that coordinates the flight planner and itinerary agents.",
    static_instruction=planning_agent_instruction,
    tools=[
        AgentTool(flight_planner_agent),
        AgentTool(itenary_agent),
    ],
)
