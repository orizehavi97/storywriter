"""Vector store for semantic search of story memories."""

from pathlib import Path
from typing import Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from ..models import Chapter, PlotThread


class VectorMemoryStore:
    """Vector-based semantic search for story memories."""

    def __init__(self, data_dir: Path = Path("data/memory")):
        """
        Initialize vector store.

        Args:
            data_dir: Directory for storing vector database
        """
        self.data_dir = Path(data_dir)
        self.vector_dir = self.data_dir / "vectors"
        self.vector_dir.mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=str(self.vector_dir),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # Initialize embedding model
        print("[VECTOR] Loading embedding model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("[OK] Embedding model loaded")

        # Get or create collections
        self.chapters_collection = self.client.get_or_create_collection(
            name="chapters",
            metadata={"description": "Chapter summaries and key events"}
        )

        self.events_collection = self.client.get_or_create_collection(
            name="events",
            metadata={"description": "Individual story events"}
        )

        self.threads_collection = self.client.get_or_create_collection(
            name="threads",
            metadata={"description": "Plot threads and developments"}
        )

    def add_chapter(self, chapter: Chapter) -> None:
        """
        Add a chapter to the vector store.

        Args:
            chapter: Chapter to add
        """
        # Create embedding from summary and key events
        text_to_embed = f"{chapter.title}\n{chapter.summary}\n" + \
                       "\n".join(chapter.key_events)

        embedding = self.embedding_model.encode(text_to_embed).tolist()

        # Store in collection
        self.chapters_collection.add(
            ids=[chapter.chapter_id],
            embeddings=[embedding],
            documents=[text_to_embed],
            metadatas=[{
                "chapter_number": chapter.chapter_number,
                "arc_id": chapter.arc_id,
                "title": chapter.title,
                "cliffhanger_type": chapter.cliffhanger_type
            }]
        )

        # Add individual events
        for i, event in enumerate(chapter.key_events):
            event_id = f"{chapter.chapter_id}_event_{i}"
            event_embedding = self.embedding_model.encode(event).tolist()

            self.events_collection.add(
                ids=[event_id],
                embeddings=[event_embedding],
                documents=[event],
                metadatas=[{
                    "chapter_id": chapter.chapter_id,
                    "chapter_number": chapter.chapter_number,
                    "event_index": i
                }]
            )

        print(f"[VECTOR] Added chapter {chapter.chapter_id} with {len(chapter.key_events)} events")

    def add_thread(self, thread: PlotThread) -> None:
        """
        Add a plot thread to the vector store.

        Args:
            thread: Plot thread to add
        """
        text_to_embed = f"{thread.name}\n{thread.setup_description}"

        embedding = self.embedding_model.encode(text_to_embed).tolist()

        self.threads_collection.add(
            ids=[thread.thread_id],
            embeddings=[embedding],
            documents=[text_to_embed],
            metadatas=[{
                "thread_type": thread.thread_type,
                "status": thread.status,
                "importance": thread.importance
            }]
        )

    def search_chapters(
        self,
        query: str,
        n_results: int = 5,
        arc_id: Optional[str] = None
    ) -> list[dict]:
        """
        Semantic search for relevant chapters.

        Args:
            query: Search query
            n_results: Number of results to return
            arc_id: Optional arc filter

        Returns:
            List of relevant chapters with metadata
        """
        query_embedding = self.embedding_model.encode(query).tolist()

        where_filter = {"arc_id": arc_id} if arc_id else None

        results = self.chapters_collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_filter
        )

        return self._format_results(results)

    def search_events(
        self,
        query: str,
        n_results: int = 10
    ) -> list[dict]:
        """
        Semantic search for relevant events.

        Args:
            query: Search query
            n_results: Number of results to return

        Returns:
            List of relevant events with metadata
        """
        query_embedding = self.embedding_model.encode(query).tolist()

        results = self.events_collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )

        return self._format_results(results)

    def search_threads(
        self,
        query: str,
        n_results: int = 5,
        status: Optional[str] = None
    ) -> list[dict]:
        """
        Semantic search for relevant plot threads.

        Args:
            query: Search query
            n_results: Number of results to return
            status: Optional status filter (open, progressing, resolved)

        Returns:
            List of relevant threads with metadata
        """
        query_embedding = self.embedding_model.encode(query).tolist()

        where_filter = {"status": status} if status else None

        results = self.threads_collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_filter
        )

        return self._format_results(results)

    def _format_results(self, results: dict) -> list[dict]:
        """Format ChromaDB results into a cleaner structure."""
        formatted = []

        if not results['ids'] or not results['ids'][0]:
            return formatted

        for i in range(len(results['ids'][0])):
            formatted.append({
                'id': results['ids'][0][i],
                'document': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i] if 'distances' in results else None
            })

        return formatted

    def get_stats(self) -> dict:
        """Get statistics about the vector store."""
        return {
            'chapters': self.chapters_collection.count(),
            'events': self.events_collection.count(),
            'threads': self.threads_collection.count()
        }

    def reset(self) -> None:
        """Reset the vector store (delete all data)."""
        self.client.reset()
        print("[VECTOR] Vector store reset")

        # Recreate collections
        self.chapters_collection = self.client.get_or_create_collection("chapters")
        self.events_collection = self.client.get_or_create_collection("events")
        self.threads_collection = self.client.get_or_create_collection("threads")
