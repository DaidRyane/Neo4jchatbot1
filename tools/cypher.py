import streamlit as st
from llm import llm
from graph import graph

# Import de la chaîne de questions-réponses Cypher
from langchain_community.chains.graph_qa.cypher import GraphCypherQAChain
from langchain.prompts.prompt import PromptTemplate

# Template pour générer des requêtes Cypher spécifiques à l'embryologie et aux cours médicaux
CYPHER_GENERATION_TEMPLATE = """ 
Avant tout chose sache que chaque question que utilisateur posera dois etre extraire a partir de la base de donné et si il demande des image envoie les lien https
Vous êtes un développeur expert en Neo4j chargé de traduire les questions des utilisateurs en requêtes Cypher pour répondre aux questions sur des cours de médecine, en particulier sur des sujets tels que les étapes de l'embryologie, la terminologie et des explications détaillées de cours.

Convertissez la question de l'utilisateur en requête Cypher en fonction du schéma fourni pour les cours de médecine, en vous concentrant sur la recherche des textes, paragraphes ou sujets les plus pertinents.

Utilisez uniquement les types de relations et les propriétés fournis. N'utilisez pas d'autres types de relations ou de propriétés non spécifiées. Si une question posée est nouvelle ou unique, adaptez votre réponse et créez une requête Cypher pour cette occasion.

Ajustements importants :
Pour la terminologie médicale spécifique ou la structure des cours, faites toujours référence aux nœuds `Course`, `Module`, `Lesson`, `Topic`, et `Paragraph` dans les requêtes, et utilisez les relations `MENTIONS` et `CONTAINS` en conséquence. Ne générez pas de réponses pour des questions qui ne sont pas liées au contexte éducatif.

Exemples de requêtes Cypher pour vous inspirer :

1. Pour trouver les paragraphes et repondre a des question pertinents liés à un sujet spécifique :

'''
   MATCH (p)-[]->(t{{name: {topic}}})
   RETURN p.text, t.name
   ORDER BY t.name
   LIMIT 3
'''
2. Pour trouver une explication détaillée d'un terme médical spécifique dans un paragraphe :
'''
MATCH (p)-[]->(t)
WHERE t.name CONTAINS "{terme}"
RETURN p.text AS explanation
ORDER BY t.name
LIMIT 3
'''

3. Pour trouver tous les paragraphes liés à un cours et module spécifiques en utilisant des embeddings :

'''
MATCH (c)-[]->(m)-[]->(l)-[]->(p)
WHERE c.name = {course} AND m.name = {module}
WITH p.embedding AS paragraphEmbedding
CALL db.index.vector.queryNodes('Paragraph-embeddings', 6, paragraphEmbedding)
YIELD node, score 
RETURN node.text AS related_text, score
ORDER BY score DESC
LIMIT 5;
'''
4. Pour filtrer les paragraphes par plusieurs sujets associés :

'''
MATCH (p)-[]->(t1{{name: "Neural Crest Cells"}})
MATCH (p)-[]->(t2{{name: "Skeletal Formation"}})
RETURN p.text AS relevant_paragraph
'''
5. Recherche contextuelle avancée de paragraphes sur l'embryologie avec similarité vectorielle dans Neo4j :

'''
MATCH (t:Topic)
WHERE t.name CONTAINS "embryologie"
  OR toLower(t.name) CONTAINS toLower("embryologie")
WITH collect(t.name) AS topicNames, collect(t) AS topics
MATCH (p:Paragraph)-[:MENTIONS]->(matchedTopic)
WHERE matchedTopic IN topics
WITH p.embedding AS paragraphEmbedding, p, topicNames
CALL db.index.vector.queryNodes('Paragraph-embeddings', 10, paragraphEmbedding)
YIELD node, score
WHERE score > 0.8
RETURN DISTINCT node.text AS paragraph_text, 
       topicNames AS matched_topics,
       score AS relevance_score
ORDER BY score DESC
LIMIT 5;
'''
Schéma : {schema}

Question : " a partir de la base de donné {question} " 
Condition : avant chaque requette corrige les faute d'orthograph et si ya pas d'accent """

# Configuration du prompt pour l'IA
cypher_prompt = PromptTemplate.from_template(CYPHER_GENERATION_TEMPLATE)

# Création de la chaîne de questions-réponses Cypher avec le prompt
cypher_qa = GraphCypherQAChain.from_llm(
    llm,
    graph=graph,
    verbose=True,
    cypher_prompt=cypher_prompt
)