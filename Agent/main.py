from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_tool_calling_agent
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
import os
from tools import (
    lebenslauf_tool,
    search_jobs_tool,
    generate_anschreiben_tool
)

load_dotenv()

class AnschreibenResponse(BaseModel):
    stelle_titel: str
    anschreiben: str
    tools_used: list[str]

llm_google = ChatGoogleGenerativeAI(api_key=os.getenv("GOOGLE_API_KEY"), model="gemini-2.5-flash")
parser = PydanticOutputParser(pydantic_object=AnschreibenResponse)


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            Du bist ein Bewerbungs-Assistent für den PyJobAgent. Workflow:
            1. Rufe `lebenslauf` mit dem vom User gegebenen Pfad auf, um den CV-Text zu extrahieren.
            2. Rufe `search_jobs` auf, um die passende Stellenausschreibung zu erhalten.
            3. Rufe `generate_anschreiben` mit dem CV-Text und der Stellenbeschreibung auf, um das Anschreiben zu erzeugen.
            4. Optional: Rufe `save_text_to_file` auf, um das Ergebnis zu speichern.

            Gib das Endergebnis exakt in diesem Format aus, ohne weiteren Text:
            {format_instructions}
            """,
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
).partial(format_instructions=parser.get_format_instructions())

tools = [lebenslauf_tool, search_jobs_tool, generate_anschreiben_tool]

agent = create_tool_calling_agent(
    llm=llm_google,
    prompt=prompt,
    tools=tools,
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
)
cv_path = input("Sende bitte mir den Pfad von deinem CV: ")
query = (
    f"Mein CV liegt unter diesem Pfad: {cv_path}. "
    "Bitte führe den kompletten Workflow aus: extrahiere den CV, hole die Stellenausschreibung "
    "und generiere das Anschreiben. Gib am Ende das Ergebnis im geforderten JSON-Format zurück."
)
raw_response = agent_executor.invoke({"query": query, "chat_history": []})
print("\n=== RAW OUTPUT ===")
print(raw_response["output"])

try:
    response_google = parser.parse(raw_response["output"])
    print("\n=== PARSED ===")
    print(response_google)
except Exception as e:
    print(f"\n[Parser-Fehler] {e}")
