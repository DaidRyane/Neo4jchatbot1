import streamlit as st
import logging
from utils import write_message
from agent import generate_response
from datetime import datetime

# Configuration du logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Configuration de la page Streamlit

st.set_page_config(page_title="Assistant de Cours", page_icon="📚", layout="wide", initial_sidebar_state="expanded")

def initialize_session_state():
    """Initialise les variables de session si elles n'existent pas déjà."""
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "👋 Bonjour! Je suis votre assistant pédagogique personnel."}
        ]
        logger.info("Initialisation des messages par défaut.")

    if "conversations" not in st.session_state:
        st.session_state.conversations = []
        logger.info("Initialisation de l'historique des conversations.")

    # Création de la première conversation par défaut si elle n'existe pas encore
    if "current_conversation" not in st.session_state:
        st.session_state.current_conversation = {
            "id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "title": "Nouvelle conversation",
            "messages": st.session_state.messages.copy()
        }
        logger.info("Création d'une première conversation par défaut.")

initialize_session_state()

def create_new_conversation():
    """Crée une nouvelle conversation et met à jour l'état de la session."""
    new_conversation = {
        "id": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "title": "Nouvelle conversation",
        "messages": st.session_state.messages.copy()
    }
    st.session_state.current_conversation = new_conversation
    logger.info("Nouvelle conversation créée avec ID: %s", new_conversation["id"])


def generate_conversation_title(messages):
    """Génère un titre basé sur le premier message de l'utilisateur."""
    user_messages = [m for m in messages if m["role"] == "user"]
    if user_messages:
        title = user_messages[0]["content"][:50] + "..." if len(user_messages[0]["content"]) > 50 else user_messages[0]["content"]
        logger.info("Titre de la conversation généré: %s", title)
        return title
    return "Nouvelle conversation"

def save_current_conversation():
    """Sauvegarde la conversation actuelle dans l'historique."""
    conv = st.session_state.current_conversation
    if conv["title"] == "Nouvelle conversation":
        conv["title"] = generate_conversation_title(st.session_state.messages)
    
    conv["messages"] = st.session_state.messages.copy()
    # Vérifie si la conversation existe déjà
    existing_conv_index = next((i for i, c in enumerate(st.session_state.conversations) if c["id"] == conv["id"]), None)
    if existing_conv_index is not None:
        st.session_state.conversations[existing_conv_index] = conv.copy()
        logger.info("Mise à jour de la conversation existante avec ID: %s", conv["id"])
    else:
        st.session_state.conversations.append(conv.copy())
        logger.info("Ajout de la nouvelle conversation dans l'historique avec ID: %s", conv["id"])

def load_conversation(conv_id):
    """Charge une conversation depuis l'historique en utilisant son ID."""
    conv = next((c for c in st.session_state.conversations if c["id"] == conv_id), None)
    if conv:
        st.session_state.messages = conv["messages"].copy()
        st.session_state.current_conversation = conv.copy()
        logger.info("Chargement de la conversation avec ID: %s", conv_id)
    else:
        logger.error("Conversation avec ID %s non trouvée.", conv_id)


def handle_submit(message):
    """Gère la soumission d'un message utilisateur et génère une réponse."""
    with st.spinner('Recherche dans la base de connaissances... 🔍'):
        try:
            # Génération de la réponse de l'assistant
            response = generate_response(message)
            write_message('assistant', response)
            logger.info("Réponse générée avec succès pour le message de l'utilisateur.")
            # Sauvegarde automatique de la conversation après la réponse
            save_current_conversation()
        except Exception as e:
            error_message = (
                "Désolé, j'ai rencontré une erreur lors de la recherche. "
                "Pourriez-vous reformuler votre question ? "
                f"(Erreur: {str(e)})"
            )
            write_message('assistant', error_message)
            logger.error("Erreur lors de la génération de réponse: %s", e)

# Interface utilisateur : barre latérale
with st.sidebar:
    st.page_link("http://www.google.com", label="Google pour des recherche externe ", icon="🌎")
    st.markdown("### 🗄️ Navigation")
    
    # Nouvelle conversation
    if st.button("📝 Nouvelle conversation"):
        st.session_state.current_conversation = create_new_conversation()
        st.session_state.messages = [st.session_state.messages[0]]  # Garde le message d'accueil
        st.rerun()
    
    # Affichage de l'historique des conversations
    st.markdown("### 💬 Historique des conversations")
    for conv in reversed(st.session_state.conversations):
        if st.button(f"🗨️ {conv['title']}", key=conv['id']):
            load_conversation(conv['id'])
            st.rerun()

    # Effacer l'historique
    if st.button("🗑️ Effacer l'historique"):
        st.session_state.conversations = []
        st.session_state.messages = [st.session_state.messages[0]]
        st.session_state.current_conversation = create_new_conversation()
        logger.info("Historique des conversations effacé.")
        st.rerun()

    st.markdown("---")
    st.markdown("### ℹ️ À propos")
    st.markdown("""
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
st.markdown("""💡 Conseil : Commencé par la phrase suivante : A partir de la base de donnée ... ,
                Posez des questions précises pour obtenir les meilleures réponses et évité les fautes d'orthorgraphs""", unsafe_allow_html=True)
