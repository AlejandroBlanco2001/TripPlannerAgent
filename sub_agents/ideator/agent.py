from google.adk.agents import Agent
from tools.scrapper import user_persona
from sub_agents.ideator.prompt import ideator_agent_instruction
from google.genai import types

ideator_agent = Agent(
    model="gemini-2.5-flash",
    name="ideator_agent",
    description="A ideator agent that can ideate on the user's trip.",
    static_instruction=ideator_agent_instruction,
    tools=[
        user_persona,
    ],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.2,
        max_output_tokens=500,
    ),
)