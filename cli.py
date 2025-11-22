"""Command-line interface for the AI Web Reader."""
import argparse
import sys
from config import settings
from scraper import WebScraper
from vector_store import VectorStore
from qa_engine import QAEngine


def setup_argparse():
    """Setup command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="AI Web Reader - Question answering from website content",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Ask a single question
  python cli.py ask "Quel est le sujet principal?"

  # Update content from website
  python cli.py update

  # Check system status
  python cli.py status

  # Interactive mode
  python cli.py interactive
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Ask command
    ask_parser = subparsers.add_parser('ask', help='Ask a question')
    ask_parser.add_argument('question', help='The question to ask')
    ask_parser.add_argument('--sources', type=int, default=5,
                           help='Number of sources to use (default: 5)')

    # Update command
    subparsers.add_parser('update', help='Update content from website')

    # Status command
    subparsers.add_parser('status', help='Show system status')

    # Interactive command
    subparsers.add_parser('interactive', help='Start interactive Q&A session')

    return parser


def initialize_components():
    """Initialize all system components."""
    print("Initialisation du système...")
    scraper = WebScraper(settings.target_url, verify_ssl=settings.verify_ssl)
    vector_store = VectorStore(settings.chroma_persist_directory)
    qa_engine = QAEngine(settings.anthropic_api_key, vector_store)
    return scraper, vector_store, qa_engine


def cmd_ask(args, qa_engine):
    """Handle the ask command."""
    print(f"\nQuestion: {args.question}\n")
    print("Recherche de réponses...")

    result = qa_engine.answer_question(args.question, n_sources=args.sources)

    print("\n" + "=" * 80)
    print(f"CONFIANCE: {result['confidence'].upper()}")
    print("=" * 80)

    print(f"\nRÉPONSE:")
    print("-" * 80)
    print(result['answer'])
    print("-" * 80)

    if result['sources']:
        print(f"\nSOURCES ({len(result['sources'])} sources):")
        for i, source in enumerate(result['sources'], 1):
            print(f"\n[{i}] {source['title']}")
            print(f"    URL: {source['url']}")
            if source.get('relevance_score'):
                score_pct = source['relevance_score'] * 100
                print(f"    Pertinence: {score_pct:.1f}%")
            print(f"    Extrait: {source['text'][:150]}...")

    print("\n")


def cmd_update(scraper, vector_store):
    """Handle the update command."""
    print("\nMise à jour du contenu...")
    print(f"URL cible: {settings.target_url}\n")

    chunks = scraper.scrape()

    if chunks is None:
        print("Erreur: Impossible de récupérer le contenu du site web")
        return

    if not chunks:
        print("Aucun changement détecté dans le contenu")
        return

    print(f"Extraction réussie: {len(chunks)} morceaux de texte")
    print("Mise à jour de la base de données vectorielle...")

    vector_store.update_content(chunks)

    print(f"Mise à jour terminée!")
    print(f"Total de documents dans la base: {vector_store.get_collection_size()}\n")


def cmd_status(vector_store):
    """Handle the status command."""
    print("\n" + "=" * 80)
    print("STATUT DU SYSTÈME")
    print("=" * 80)

    print(f"\nURL cible: {settings.target_url}")
    print(f"Fréquence de mise à jour: {settings.update_frequency} minutes")
    print(f"Répertoire ChromaDB: {settings.chroma_persist_directory}")
    print(f"Documents dans la base: {vector_store.get_collection_size()}")

    print("\nConfiguration:")
    print(f"  API Host: {settings.api_host}")
    print(f"  API Port: {settings.api_port}")
    print(f"  Clé API configurée: {'Oui' if settings.anthropic_api_key else 'Non'}")

    print("\n")


def cmd_interactive(qa_engine, scraper, vector_store):
    """Handle the interactive command."""
    print("\n" + "=" * 80)
    print("MODE INTERACTIF - AI WEB READER")
    print("=" * 80)
    print("\nCommandes disponibles:")
    print("  - Tapez votre question pour obtenir une réponse")
    print("  - 'update' pour mettre à jour le contenu")
    print("  - 'status' pour voir le statut")
    print("  - 'quit' ou 'exit' pour quitter")
    print("\n" + "=" * 80 + "\n")

    while True:
        try:
            question = input("\nQuestion> ").strip()

            if not question:
                continue

            if question.lower() in ['quit', 'exit', 'q']:
                print("\nAu revoir!\n")
                break

            if question.lower() == 'update':
                cmd_update(scraper, vector_store)
                continue

            if question.lower() == 'status':
                cmd_status(vector_store)
                continue

            # Ask question
            print("\nRecherche de réponses...")
            result = qa_engine.answer_question(question)

            print(f"\n[Confiance: {result['confidence']}]")
            print(f"\n{result['answer']}\n")

            if result['sources']:
                print(f"Sources: {len(result['sources'])} documents utilisés")

        except KeyboardInterrupt:
            print("\n\nInterruption détectée. Au revoir!\n")
            break
        except Exception as e:
            print(f"\nErreur: {e}\n")


def main():
    """Main CLI entry point."""
    parser = setup_argparse()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        # Initialize components
        scraper, vector_store, qa_engine = initialize_components()

        # Route to appropriate command
        if args.command == 'ask':
            cmd_ask(args, qa_engine)
        elif args.command == 'update':
            cmd_update(scraper, vector_store)
        elif args.command == 'status':
            cmd_status(vector_store)
        elif args.command == 'interactive':
            cmd_interactive(qa_engine, scraper, vector_store)

    except Exception as e:
        print(f"\nErreur fatale: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
