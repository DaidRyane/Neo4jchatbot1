import streamlit as st
from utils import write_message
from agent import generate_response
from datetime import datetime

# Configuration de la page
st.set_page_config(
    page_title="Assistant de Cours",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialisation des variables de session
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": """👋 Bonjour! Je suis votre assistant pédagogique personnel.
            Je peux vous aider à :

            📚 Trouver des informations dans vos cours
            📝 Répondre à vos questions sur le contenu
            🔍 Rechercher des sujets spécifiques

            Comment puis-je vous aider aujourd'hui ?"""
        },
    ]

if "current_course" not in st.session_state:
    st.session_state.current_course = None

if "conversations" not in st.session_state:
    st.session_state.conversations = []

if "current_conversation" not in st.session_state:
    st.session_state.current_conversation = {
        "id": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "title": "Nouvelle conversation",
        "messages": st.session_state.messages.copy()
    }

def generate_conversation_title(messages):
    """
    Génère un titre pour la conversation basé sur le premier message utilisateur
    """
    user_messages = [m for m in messages if m["role"] == "user"]
    if user_messages:
        title = user_messages[0]["content"][:50] + "..." if len(user_messages[0]["content"]) > 50 else user_messages[0]["content"]
        return title
    return "Nouvelle conversation"

def save_current_conversation():
    """
    Sauvegarde la conversation courante dans l'historique
    """
    if st.session_state.current_conversation:
        # Mise à jour du titre si nécessaire
        if st.session_state.current_conversation["title"] == "Nouvelle conversation":
            st.session_state.current_conversation["title"] = generate_conversation_title(st.session_state.messages)
        
        # Mise à jour des messages
        st.session_state.current_conversation["messages"] = st.session_state.messages.copy()
        
        # Vérifie si la conversation existe déjà dans l'historique
        existing_conv_index = next((i for i, conv in enumerate(st.session_state.conversations) 
                                if conv["id"] == st.session_state.current_conversation["id"]), None)
        
        if existing_conv_index is not None:
            st.session_state.conversations[existing_conv_index] = st.session_state.current_conversation.copy()
        else:
            st.session_state.conversations.append(st.session_state.current_conversation.copy())

def create_new_conversation():
    """
    Crée une nouvelle conversation
    """
    save_current_conversation()
    st.session_state.messages = [st.session_state.messages[0]]  # Garde le message d'accueil
    st.session_state.current_conversation = {
        "id": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "title": "Nouvelle conversation",
        "messages": st.session_state.messages.copy()
    }

def load_conversation(conv_id):
    """
    Charge une conversation depuis l'historique
    """
    conv = next((c for c in st.session_state.conversations if c["id"] == conv_id), None)
    if conv:
        st.session_state.messages = conv["messages"].copy()
        st.session_state.current_conversation = conv.copy()

def handle_submit(message):
    """
    Gère la soumission d'un message et génère une réponse
    """
    with st.spinner('Recherche dans la base de connaissances... 🔍'):
        try:
            # Génération de la réponse
            response = generate_response(message)
            
            # Ajout de la réponse au chat
            write_message('assistant', response)
            
            # Sauvegarde automatique de la conversation
            save_current_conversation()
            
        except Exception as e:
            error_message = (
                "Désolé, j'ai rencontré une erreur lors de la recherche. "
                "Pourriez-vous reformuler votre question ? "
                f"(Erreur: {str(e)})"
            )
            write_message('assistant', error_message)

# Sidebar pour l'historique et les fonctionnalités
with st.sidebar:
    st.markdown("### 🗄️ Navigation")
    
    # Bouton pour nouvelle conversation
    if st.button("📝 Nouvelle conversation"):
        create_new_conversation()
        st.rerun()
    
    # Affichage de l'historique des conversations
    st.markdown("### 💬 Historique des conversations")
    for conv in reversed(st.session_state.conversations):
        if st.button(f"🗨️ {conv['title']}", key=conv['id']):
            load_conversation(conv['id'])
            st.rerun()
    
    st.markdown("---")
    
    # Bouton pour effacer l'historique
    if st.button("🗑️ Effacer l'historique"):
        st.session_state.conversations = []
        st.session_state.messages = [st.session_state.messages[0]]
        st.session_state.current_conversation = {
            "id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "title": "Nouvelle conversation",
            "messages": st.session_state.messages.copy()
        }
        st.rerun()
    
    st.markdown("---")
    
    # Suggestions de questions
    st.markdown("### 💡 Suggestions de questions")
    example_questions = [
        "A partir de la base de donnée explique le rôle des cellules neurale dans la squellettogenèse faciaux ?",
        "A partir de la base de donnée peut tu me suggérer des image https du sujet précédant" ,
        "A partir de la base de donnée quelle est l'origine des bourgeons facieux ?",
        "A partir de la base de donnée quelle est la relation entre les bourgeons facieux et l'embryologie ?"
    ]
    
    for question in example_questions:
        if st.button(question, key=question):
            write_message('user', question)
            handle_submit(question)
    
    st.markdown("---")
    st.markdown("""
    ### ℹ️ À propos
    Cet assistant utilise l'IA pour vous aider à naviguer
    dans votre contenu de cours. Il a accès à tous les
    modules, leçons et sujets de votre base de données.
    """)

# Interface principale
st.title("📚 Assistant de Cours")

# Affichage des messages
for message in st.session_state.messages:
    write_message(message['role'], message['content'], save=False)

# Zone de saisie utilisateur
if prompt := st.chat_input("Posez votre question ici..."):
    write_message('user', prompt)
    handle_submit(prompt)

# Footer
st.markdown("---")
st.markdown(
    """
    💡 Conseil : Posez des questions précises pour obtenir les meilleures réponses,éviter les fautes d'orthorgraphs et pour instant assistant na pas une memoire long donc faut lui dire a partir de la question précédant 
    """,
    unsafe_allow_html=True
)
