"""Example client for interacting with the AI Web Reader API."""
import requests
import json
from typing import Optional


class WebReaderClient:
    """Client for the AI Web Reader API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize the client.

        Args:
            base_url: Base URL of the API
        """
        self.base_url = base_url

    def ask(self, question: str, n_sources: int = 5) -> dict:
        """Ask a question about the website content.

        Args:
            question: The question to ask
            n_sources: Number of sources to retrieve

        Returns:
            Dictionary with answer, sources, and confidence
        """
        response = requests.post(
            f"{self.base_url}/ask",
            json={"question": question, "n_sources": n_sources}
        )
        response.raise_for_status()
        return response.json()

    def ask_streaming(self, question: str, n_sources: int = 5):
        """Ask a question with streaming response.

        Args:
            question: The question to ask
            n_sources: Number of sources to retrieve

        Yields:
            Chunks of the response
        """
        response = requests.post(
            f"{self.base_url}/ask/stream",
            json={"question": question, "n_sources": n_sources},
            stream=True
        )
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                yield json.loads(line)

    def get_status(self) -> dict:
        """Get the system status.

        Returns:
            Dictionary with system status information
        """
        response = requests.get(f"{self.base_url}/status")
        response.raise_for_status()
        return response.json()

    def force_update(self) -> dict:
        """Force an immediate content update.

        Returns:
            Dictionary with update status
        """
        response = requests.post(f"{self.base_url}/update")
        response.raise_for_status()
        return response.json()

    def health_check(self) -> dict:
        """Check the health of the system.

        Returns:
            Dictionary with health status
        """
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()


def display_answer(result: dict):
    """Display a formatted answer.

    Args:
        result: Result dictionary from the ask endpoint
    """
    print("\n" + "=" * 80)
    print(f"QUESTION: {result['question']}")
    print("=" * 80)

    print(f"\nCONFIANCE: {result['confidence'].upper()}")

    print(f"\nRÉPONSE:")
    print("-" * 80)
    print(result['answer'])
    print("-" * 80)

    if result['sources']:
        print(f"\nSOURCES ({len(result['sources'])} sources utilisées):")
        for i, source in enumerate(result['sources'], 1):
            print(f"\n[Source {i}]")
            print(f"  Titre: {source['title']}")
            print(f"  URL: {source['url']}")
            if source.get('relevance_score'):
                print(f"  Score de pertinence: {source['relevance_score']:.2f}")
            print(f"  Extrait: {source['text']}")

    print("\n" + "=" * 80 + "\n")


def example_basic_usage():
    """Example of basic usage."""
    print("=== EXEMPLE 1: Utilisation basique ===\n")

    client = WebReaderClient()

    # Check system status
    print("Vérification du statut du système...")
    status = client.get_status()
    print(f"Statut: {status['status']}")
    print(f"URL cible: {status['target_url']}")
    print(f"Nombre de documents: {status['collection_size']}")
    print(f"Dernière mise à jour: {status['last_update']}\n")

    # Ask a question
    print("Pose d'une question...")
    result = client.ask("Quel est le sujet principal du site?")
    display_answer(result)


def example_streaming():
    """Example of streaming response."""
    print("=== EXEMPLE 2: Réponse en streaming ===\n")

    client = WebReaderClient()

    question = "Expliquez le contenu principal du site"
    print(f"Question: {question}\n")

    print("Réponse (streaming):")
    print("-" * 80)

    sources_displayed = False

    for chunk in client.ask_streaming(question):
        if chunk['type'] == 'sources':
            if not sources_displayed:
                print("\n\n[Sources chargées]")
                for i, source in enumerate(chunk['content'], 1):
                    print(f"  {i}. {source['title']} ({source['url']})")
                print("\nRéponse: ", end='', flush=True)
                sources_displayed = True

        elif chunk['type'] == 'answer_chunk':
            print(chunk['content'], end='', flush=True)

        elif chunk['type'] == 'error':
            print(f"\nErreur: {chunk['content']}")

    print("\n" + "-" * 80 + "\n")


def example_multiple_questions():
    """Example of asking multiple questions."""
    print("=== EXEMPLE 3: Questions multiples ===\n")

    client = WebReaderClient()

    questions = [
        "Quel est le sujet principal?",
        "Y a-t-il des informations de contact?",
        "Quelles sont les principales fonctionnalités mentionnées?"
    ]

    for i, question in enumerate(questions, 1):
        print(f"\nQuestion {i}/{len(questions)}: {question}")
        result = client.ask(question, n_sources=3)

        print(f"Confiance: {result['confidence']}")
        print(f"Réponse: {result['answer'][:200]}...")

        if i < len(questions):
            print("\n" + "-" * 40)


def example_force_update():
    """Example of forcing a content update."""
    print("=== EXEMPLE 4: Mise à jour forcée ===\n")

    client = WebReaderClient()

    print("Statut avant mise à jour:")
    status_before = client.get_status()
    print(f"  Nombre de mises à jour: {status_before['update_count']}")
    print(f"  Dernière mise à jour: {status_before['last_update']}\n")

    print("Déclenchement d'une mise à jour...")
    update_result = client.force_update()
    print(f"  Résultat: {update_result['message']}\n")

    import time
    time.sleep(2)  # Wait for update to complete

    print("Statut après mise à jour:")
    status_after = client.get_status()
    print(f"  Nombre de mises à jour: {status_after['update_count']}")
    print(f"  Dernière mise à jour: {status_after['last_update']}\n")


def main():
    """Run all examples."""
    try:
        # Check if the API is running
        client = WebReaderClient()
        client.health_check()

        print("\n" + "=" * 80)
        print("EXEMPLES D'UTILISATION DE L'AI WEB READER")
        print("=" * 80 + "\n")

        # Run examples
        example_basic_usage()
        input("Appuyez sur Entrée pour continuer vers l'exemple suivant...")

        example_streaming()
        input("Appuyez sur Entrée pour continuer vers l'exemple suivant...")

        example_multiple_questions()
        input("Appuyez sur Entrée pour continuer vers l'exemple suivant...")

        example_force_update()

        print("\n" + "=" * 80)
        print("EXEMPLES TERMINÉS")
        print("=" * 80 + "\n")

    except requests.exceptions.ConnectionError:
        print("\nERREUR: Impossible de se connecter à l'API.")
        print("Assurez-vous que l'application est démarrée avec: python main.py\n")
    except Exception as e:
        print(f"\nERREUR: {e}\n")


if __name__ == "__main__":
    main()
