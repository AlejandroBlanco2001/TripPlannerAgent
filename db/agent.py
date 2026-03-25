from google.adk.agents.llm_agent import Agent
from sub_agents.planning.agent import planning_agent
from db.prompts import root_agent_instruction
from google.adk.apps import App, ResumabilityConfig
from sub_agents.ideator.agent import ideator_agent

root_agent = Agent(
    model="gemini-2.5-flash",
    name="root_agent",
    description="A trip coordinator agent that can coordinate the flight planner and itenary agents.",
    static_instruction=root_agent_instruction,
    sub_agents=[planning_agent, ideator_agent],
)

app = App(
    name="db",
    root_agent=root_agent,
    resumability_config=ResumabilityConfig(
        is_resumable=True,
    )
)