from crewai import Crew
from Agents import researcher, analyst, writer
from Tasks import research_task, analysis_task, writing_task
from crewai import Process

crew = Crew(
    agents=[researcher, analyst, writer],
    tasks=[research_task, analysis_task, writing_task],
    process=Process.sequential
)
