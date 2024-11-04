from llm import llm
from graph import graph
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.tools import Tool
from langchain_community.chat_message_histories import Neo4jChatMessageHistory
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain import hub
from utils import get_session_id
from tools.cypher import cypher_qa
from tools.vector import get_course_paragraph

# Création du template de prompt pour les messages du chatbot
chat_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a teacher providing information about course content. Do not answer any questions using your pre-trained knowledge, only use the information provided in the context."),
        ("human", "{input}"),
    ]
)

# Création de l'outil pour répondre aux questions générales et de cours
course_chat = chat_prompt | llm | StrOutputParser()

tools = [
    Tool.from_function(
        name="General Chat",
        description="For general chat about the course not covered by other tools",
        func=course_chat.invoke,
    ),
    Tool.from_function(
        name="Course Plot Search",  
        description=" Quand tu veux avoir des réponses basées sur la recherche dans la base de donné",
        func=get_course_paragraph,
    ), 
    Tool.from_function(
        name="Course Information",
        description=" répond a des question simple sur un cours via des requette cypher  present dans la base de donné ",
        func=cypher_qa.invoke
    ),

]

# Fonction pour récupérer l'historique des messages avec une session Neo4j
def get_memory(session_id):
    return Neo4jChatMessageHistory(session_id=session_id, graph=graph)

# Chargement du modèle d'agent
agent_prompt = hub.pull("hwchase17/react-chat")

# Création de l'agent réactif
agent = create_react_agent(llm, tools, agent_prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True
)

# Création de l'agent de conversation avec historique des messages
chat_agent = RunnableWithMessageHistory(
    agent_executor,
    get_memory,
    input_messages_key="input",
    history_messages_key="chat_history",
)

# Fonction pour générer une réponse
def generate_response(user_input):
    """
    Appelle l'agent de conversation et renvoie une réponse
    pour l'interface utilisateur.
    """
    response = chat_agent.invoke(
        {"input": user_input},
        {"configurable": {"session_id": get_session_id()}}
    )
    return response['output']