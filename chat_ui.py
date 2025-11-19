"""Streamlit chat interface for AI Web Reader."""
import streamlit as st
import os
from datetime import datetime
from pathlib import Path

# Must be the first Streamlit command
st.set_page_config(
    page_title="AI Web Reader Chat",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

from config import Settings
from scraper import WebScraper
from vector_store import VectorStore
from qa_engine import QAEngine
from updater import ContentUpdater


# Custom CSS for better styling
def load_css():
    """Load custom CSS styles."""
    st.markdown("""
    <style>
    /* Main chat container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    /* User message styling */
    .user-message {
        background-color: #E3F2FD;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #2196F3;
    }

    /* Assistant message styling */
    .assistant-message {
        background-color: #F5F5F5;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #4CAF50;
    }

    /* Source box styling */
    .source-box {
        background-color: #FFF9C4;
        padding: 0.8rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 3px solid #FBC02D;
        font-size: 0.9rem;
    }

    /* Confidence badge */
    .confidence-high {
        background-color: #4CAF50;
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: bold;
    }

    .confidence-medium {
        background-color: #FF9800;
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: bold;
    }

    .confidence-low {
        background-color: #F44336;
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: bold;
    }

    /* Status indicator */
    .status-online {
        color: #4CAF50;
        font-weight: bold;
    }

    .status-offline {
        color: #F44336;
        font-weight: bold;
    }

    /* Header styling */
    .chat-header {
        background: linear-gradient(90deg, #2196F3 0%, #4CAF50 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        text-align: center;
    }

    /* Sidebar styling */
    .sidebar .sidebar-content {
        background-color: #FAFAFA;
    }

    /* Timestamp styling */
    .timestamp {
        color: #888;
        font-size: 0.75rem;
        font-style: italic;
    }
    </style>
    """, unsafe_allow_html=True)


@st.cache_resource
def initialize_system():
    """Initialize the AI Web Reader system (cached)."""
    try:
        # Load settings from environment or defaults
        if Path(".env").exists():
            settings = Settings()
        else:
            # Use session state for configuration if no .env file
            settings = Settings(
                anthropic_api_key=st.session_state.get('api_key', os.getenv('ANTHROPIC_API_KEY', '')),
                target_url=st.session_state.get('target_url', 'https://docs.anthropic.com'),
                update_frequency=st.session_state.get('update_frequency', 60),
                chroma_persist_directory='./chroma_db'
            )

        scraper = WebScraper(settings.target_url)
        vector_store = VectorStore(settings.chroma_persist_directory)
        qa_engine = QAEngine(settings.anthropic_api_key, vector_store)
        updater = ContentUpdater(scraper, vector_store, settings.update_frequency)

        return scraper, vector_store, qa_engine, updater, settings
    except Exception as e:
        st.error(f"Erreur d'initialisation: {e}")
        return None, None, None, None, None


def initialize_session_state():
    """Initialize session state variables."""
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    if 'system_initialized' not in st.session_state:
        st.session_state.system_initialized = False

    if 'api_key' not in st.session_state:
        st.session_state.api_key = os.getenv('ANTHROPIC_API_KEY', '')

    if 'target_url' not in st.session_state:
        st.session_state.target_url = os.getenv('TARGET_URL', 'https://docs.anthropic.com')

    if 'update_frequency' not in st.session_state:
        st.session_state.update_frequency = int(os.getenv('UPDATE_FREQUENCY', 60))

    if 'show_sources' not in st.session_state:
        st.session_state.show_sources = True


def render_sidebar(scraper, vector_store, updater, settings):
    """Render the sidebar with configuration and status."""
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")

        # API Key input
        api_key = st.text_input(
            "Clé API Anthropic",
            value=st.session_state.api_key,
            type="password",
            help="Votre clé API Anthropic pour utiliser Claude"
        )
        if api_key != st.session_state.api_key:
            st.session_state.api_key = api_key
            st.cache_resource.clear()

        # Target URL input
        target_url = st.text_input(
            "URL cible",
            value=st.session_state.target_url,
            help="L'URL du site web à analyser"
        )
        if target_url != st.session_state.target_url:
            st.session_state.target_url = target_url
            st.cache_resource.clear()

        # Show sources toggle
        st.session_state.show_sources = st.checkbox(
            "Afficher les sources",
            value=st.session_state.show_sources,
            help="Afficher les sources utilisées pour chaque réponse"
        )

        st.markdown("---")

        # System status
        st.markdown("### 📊 Statut du système")

        if vector_store:
            collection_size = vector_store.get_collection_size()

            if collection_size > 0:
                st.markdown('<span class="status-online">● En ligne</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="status-offline">● Hors ligne (pas de données)</span>', unsafe_allow_html=True)

            st.metric("Documents indexés", collection_size)

            if settings:
                st.info(f"🌐 **URL:** {settings.target_url}")

        st.markdown("---")

        # Actions
        st.markdown("### 🔧 Actions")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔄 Mettre à jour", use_container_width=True):
                with st.spinner("Mise à jour en cours..."):
                    if scraper and vector_store:
                        chunks = scraper.scrape()
                        if chunks:
                            vector_store.update_content(chunks)
                            st.success(f"✅ {len(chunks)} chunks indexés!")
                            st.rerun()
                        elif chunks is not None:
                            st.info("Aucun changement détecté")
                        else:
                            st.error("Erreur lors du scraping")

        with col2:
            if st.button("🗑️ Effacer chat", use_container_width=True):
                st.session_state.messages = []
                st.rerun()

        # Initial loading
        if vector_store and vector_store.get_collection_size() == 0:
            st.warning("⚠️ Aucune donnée chargée. Cliquez sur 'Mettre à jour' pour indexer le site.")

        st.markdown("---")

        # Info
        st.markdown("### ℹ️ À propos")
        st.markdown("""
        **AI Web Reader** utilise:
        - Claude AI pour les réponses
        - RAG pour éviter les hallucinations
        - Citations de sources obligatoires

        Toutes les réponses sont basées **uniquement** sur le contenu du site web indexé.
        """)


def render_message(message):
    """Render a single chat message."""
    role = message["role"]
    content = message["content"]
    timestamp = message.get("timestamp", "")

    if role == "user":
        st.markdown(f"""
        <div class="user-message">
            <strong>👤 Vous</strong>
            <span class="timestamp">{timestamp}</span>
            <p>{content}</p>
        </div>
        """, unsafe_allow_html=True)

    elif role == "assistant":
        confidence = message.get("confidence", "medium")
        sources = message.get("sources", [])

        # Confidence badge
        confidence_class = f"confidence-{confidence}"
        confidence_text = {
            "high": "HAUTE",
            "medium": "MOYENNE",
            "low": "FAIBLE",
            "none": "AUCUNE"
        }.get(confidence, "INCONNUE")

        st.markdown(f"""
        <div class="assistant-message">
            <strong>🤖 Assistant</strong>
            <span class="{confidence_class}">Confiance: {confidence_text}</span>
            <span class="timestamp">{timestamp}</span>
            <p>{content}</p>
        </div>
        """, unsafe_allow_html=True)

        # Show sources if enabled
        if st.session_state.show_sources and sources:
            with st.expander(f"📚 Sources ({len(sources)} documents)", expanded=False):
                for i, source in enumerate(sources, 1):
                    st.markdown(f"""
                    <div class="source-box">
                        <strong>Source {i}</strong><br>
                        <strong>Titre:</strong> {source.get('title', 'N/A')}<br>
                        <strong>URL:</strong> <a href="{source.get('url', '#')}" target="_blank">{source.get('url', 'N/A')}</a><br>
                        {f"<strong>Pertinence:</strong> {source.get('relevance_score', 0)*100:.1f}%<br>" if source.get('relevance_score') else ''}
                        <strong>Extrait:</strong> {source.get('text', 'N/A')[:200]}...
                    </div>
                    """, unsafe_allow_html=True)


def main():
    """Main application function."""
    # Load custom CSS
    load_css()

    # Initialize session state
    initialize_session_state()

    # Initialize system components
    scraper, vector_store, qa_engine, updater, settings = initialize_system()

    # Render header
    st.markdown("""
    <div class="chat-header">
        <h1>🤖 AI Web Reader Chat</h1>
        <p>Posez des questions sur le contenu du site web indexé</p>
    </div>
    """, unsafe_allow_html=True)

    # Render sidebar
    render_sidebar(scraper, vector_store, updater, settings)

    # Main chat area
    st.markdown("### 💬 Conversation")

    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            render_message(message)

    # Chat input
    if prompt := st.chat_input("Posez votre question ici..."):
        if not st.session_state.api_key:
            st.error("⚠️ Veuillez configurer votre clé API Anthropic dans la barre latérale")
            return

        if not qa_engine:
            st.error("⚠️ Le système n'est pas correctement initialisé")
            return

        if vector_store and vector_store.get_collection_size() == 0:
            st.error("⚠️ Aucune donnée indexée. Cliquez sur 'Mettre à jour' dans la barre latérale")
            return

        # Add user message
        timestamp = datetime.now().strftime("%H:%M:%S")
        user_message = {
            "role": "user",
            "content": prompt,
            "timestamp": timestamp
        }
        st.session_state.messages.append(user_message)

        # Get AI response
        with st.spinner("🤔 Réflexion en cours..."):
            try:
                result = qa_engine.answer_question(prompt, n_sources=5)

                assistant_message = {
                    "role": "assistant",
                    "content": result["answer"],
                    "confidence": result.get("confidence", "medium"),
                    "sources": result.get("sources", []),
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                }
                st.session_state.messages.append(assistant_message)

            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")
                error_message = {
                    "role": "assistant",
                    "content": f"Désolé, une erreur s'est produite: {str(e)}",
                    "confidence": "none",
                    "sources": [],
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                }
                st.session_state.messages.append(error_message)

        # Rerun to show new messages
        st.rerun()

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #888; font-size: 0.9rem;">
        Propulsé par Claude AI & ChromaDB |
        Réponses basées uniquement sur le contenu indexé |
        Anti-hallucination activé ✅
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
