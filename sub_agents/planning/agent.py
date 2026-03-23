from google.adk.agents import Agent, SequentialAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools import FunctionTool, google_search
from sub_agents.planning.prompts import (
    instructions_flight_planner,
    itenary_agent_instruction,
    planning_agent_instruction,
    request_flight_approval_instruction,
)
from tools.scrapper import search_google_flights, search_iata_code_airpots_city, user_selected_flight

flight_planner_agent = Agent(
    model="gemini-2.5-flash",
    name="flight_planner_agent",
    description="A flight planner agent that can search for flights and return the flight information.",
    static_instruction=instructions_flight_planner,
    tools=[search_google_flights, search_iata_code_airpots_city],
    output_key="flight_information",
)

user_selected_flight_tool = FunctionTool(
    func=user_selected_flight,
    require_confirmation=True,
)

request_flight_approval_agent = Agent(
    model="gemini-2.5-flash",
    name="request_flight_approval_agent",
    description="A flight approval agent that presents the found flights to the user and asks them to select one.",
    static_instruction=request_flight_approval_instruction,
    tools=[user_selected_flight_tool],
    output_key="selected_flight_information",
)

itenary_agent = Agent(
    model="gemini-2.5-flash",
    name="itenary_agent",
    description="A itenary agent that can create a itenary for the user.",
    static_instruction=itenary_agent_instruction,
    tools=[google_search],
)

flight_planner_and_approval_agent = SequentialAgent(
    name="FlightPlannerandApprovalAgent",
    description="A agent that can coordinate the flight planner and approval agent.",
    sub_agents=[flight_planner_agent, request_flight_approval_agent],
)

planning_agent = Agent(
    model="gemini-2.5-flash",
    name="planning_agent",
    description="A planning agent that coordinates the flight planner and itinerary agents.",
    static_instruction=planning_agent_instruction,
    tools=[
        AgentTool(flight_planner_and_approval_agent),
        AgentTool(itenary_agent),
    ],
)
