from crewai import Task
from Agents import researcher, analyst, writer

research_task = Task(
    description="Research and summarize the latest advancements based on prior knowledge on the {topic}.",
    expected_output="A structured list of key advancements in the past year.",
    agent=researcher
)

analysis_task = Task(
    description="Analyze the research findings and extract meaningful insights about the trends.",
    expected_output="A concise summary of the top 3-5 trends with supporting details.",
    agent=analyst
)

writing_task = Task(
    description="Write a structured and engaging report based on research and analysis.",
    expected_output="A well-formatted report (minimum 500 words) summarizing advancements.",
    agent=writer
)