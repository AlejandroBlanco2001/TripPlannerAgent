from google.adk.agents.llm_agent import Agent
from tools.scrapper import search_google_flights, search_iata_code_airpots_city
from db.prompts import instructions_flight_planner, root_agent_instruction

flight_planner_agent = Agent(
    model="gemini-2.5-flash",
    name="flight_planner_agent",
    description="A flight planner agent that can search for flights and return the flight information.",
    static_instruction=instructions_flight_planner,
    tools=[search_google_flights, search_iata_code_airpots_city],
)

root_agent = Agent(
    model="gemini-2.5-flash",
    name="root_agent",
    description="A helpful assistant that can answer user questions and search for flights.",
    static_instruction=root_agent_instruction,
    sub_agents=[flight_planner_agent],
)
