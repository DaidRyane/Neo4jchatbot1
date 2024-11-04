import streamlit as st
from llm import llm, embeddings
from graph import graph

# Importation de la classe Neo4jVector pour la recherche vectorielle
from langchain_community.vectorstores.neo4j_vector import Neo4jVector

# Importation des chaînes de LangChain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain

# Importation du template de prompt pour le chatbot
from langchain_core.prompts import ChatPromptTemplate

# Configuration de Neo4jVector pour la recherche dans la base de données des cours
neo4jvector = Neo4jVector.from_existing_index(
    embeddings,                                  # Embeddings pour la recherche
    graph=graph,                                 # Connexion Neo4j
    index_name="Paragraph_embeddings",               # Nom de l'index pour les Paragraphs
    node_label="Paragraph",                      # Label du nœud pour la recherche
    text_node_property="text",                   # Propriété texte du nœud Paragraph
    embedding_node_property="embedding",         # Embedding pour la similarité
    retrieval_query="""                          
RETURN
    node.text AS text,
    score,
    {
        course: [ (c)-[:HAS_MODULE]->()-[:HAS_LESSON]->(l)-[:CONTAINS]->(node) | c.name ][0],
        module: [ (m)-[:HAS_LESSON]->(l)-[:CONTAINS]->(node) | m.name ][0],
        lesson: [ (l)-[:CONTAINS]->(node) | l.name ][0],
        topics: [ (node)-[:MENTIONS]->(t) | t.name ]
    } AS metadata
"""
)

# Création d'un retriever pour effectuer des recherches dans Neo4j
retriever = neo4jvector.as_retriever()

# Configuration des instructions du chatbot
instructions = (
    "sache que tout les queston dois etre récupérer a partir de la base de donné Utilise le contexte donné pour répondre à la question posée, et si utilisateur demande des image envoie les lien https corrige les faute d'orthograph et si tu trouve pas essaye plusieur combinaison de mot  "
    "Si tu ne connais pas la réponse, réponds simplement que tu ne sais pas."
    "Contexte : {context}"
)

# Création du prompt pour le chatbot
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", instructions),
        ("human", "{input}"),
    ]
)

# Création de la chaîne de traitement pour les réponses
question_answer_chain = create_stuff_documents_chain(llm, prompt)
course_retriever = create_retrieval_chain(
    retriever, 
    question_answer_chain
)

# Fonction pour obtenir des réponses basées sur les Paragraphs
def get_course_paragraph(input):
    return course_retriever.invoke({"input": input})

# Exécution de la fonction avec une question
# Exemple : print(get_course_paragraph("Quels sont les principaux sujets abordés dans le cours de chirurgie dentaire?"))
