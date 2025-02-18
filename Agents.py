from os import getenv
from crewai import Agent, LLM
from dotenv import load_dotenv

load_dotenv()

model = LLM(
    model = "gemini/gemini-2.0-flash",
    temperature = 0.7,
    api_key = getenv("GOOGLE_API_KEY")
)

researcher = Agent(
    role="AI Research Expert",
    goal="Gather insights about {topic} based on existing knowledge.",
    backstory="A highly skilled AI researcher specializing in analyzing trends.",
    tools=[],
    allow_delegation=False,
    llm=model
)

analyst = Agent(
    role="Data Analysis Specialist",
    goal="Analyze and extract key trends from {topic} research.",
    backstory="A data scientist with expertise in identifying patterns.",
    tools=[],
    allow_delegation=False,
    llm=model
)

writer = Agent(
    role="Report Writer",
    goal="Summarize AI advancements in an engaging and structured format.",
    backstory="A skilled writer who transforms complex AI trends into digestible insights.",
    tools=[],  # No external tools used
    allow_delegation=False,
    llm=model
)

