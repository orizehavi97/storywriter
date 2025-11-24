"""Smart retrieval system combining recency and relevance."""

from typing import Optional
import random

from ..models import StoryMemory, Chapter
from .vector_store import VectorMemoryStore


class SmartRetriever:
    """
    Smart retrieval combining multiple strategies:
    - Recency: Recent chapters
    - Relevance: Semantic similarity
    - Surprise: Random callbacks for variety
    """

    def __init__(self, vector_store: VectorMemoryStore):
        """
        Initialize smart retriever.

        Args:
            vector_store: Vector store for semantic search
        """
        self.vector_store = vector_store

    def retrieve_for_planning(
        self,
        memory: StoryMemory,
        current_arc_id: Optional[str] = None,
        n_recent: int = 3,
        n_relevant: int = 5,
        n_surprise: int = 2
    ) -> dict:
        """
        Retrieve relevant memories for chapter planning.

        Args:
            memory: Current story memory
            current_arc_id: Current arc ID
            n_recent: Number of recent chapters
            n_relevant: Number of semantically relevant items
            n_surprise: Number of surprise callbacks

        Returns:
            Dictionary with categorized retrieved memories
        """
        print(f"\n[RETRIEVAL] Gathering context for planning...")

        retrieval = {
            "recent_chapters": [],
            "relevant_chapters": [],
            "relevant_events": [],
            "surprise_callbacks": [],
            "active_threads": []
        }

        # 1. Recent chapters (recency)
        recent = memory.get_recent_chapters(n=n_recent)
        retrieval["recent_chapters"] = [
            {
                "chapter_id": ch.chapter_id,
                "chapter_number": ch.chapter_number,
                "title": ch.title,
                "summary": ch.summary,
                "cliffhanger": ch.cliffhanger
            }
            for ch in recent
        ]

        print(f"[RETRIEVAL] - {len(recent)} recent chapters")

        # 2. Relevant chapters (semantic similarity)
        if len(memory.chapters) > n_recent:
            # Build query from recent context
            if recent:
                query = f"{recent[0].summary} {' '.join(recent[0].key_events[:3])}"
            else:
                query = f"{memory.saga_goal} {memory.world_name}"

            relevant_results = self.vector_store.search_chapters(
                query=query,
                n_results=n_relevant,
                arc_id=current_arc_id
            )

            retrieval["relevant_chapters"] = [
                {
                    "chapter_id": result['id'],
                    "chapter_number": result['metadata']['chapter_number'],
                    "title": result['metadata']['title'],
                    "summary": result['document'],
                    "relevance": 1 - result['distance'] if result['distance'] else 1.0
                }
                for result in relevant_results
                # Filter out recent chapters we already have
                if result['id'] not in [ch.chapter_id for ch in recent]
            ]

            print(f"[RETRIEVAL] - {len(retrieval['relevant_chapters'])} relevant chapters")

            # 3. Relevant events (fine-grained semantic)
            event_results = self.vector_store.search_events(
                query=query,
                n_results=n_relevant * 2
            )

            retrieval["relevant_events"] = [
                {
                    "event": result['document'],
                    "chapter_id": result['metadata']['chapter_id'],
                    "chapter_number": result['metadata']['chapter_number'],
                    "relevance": 1 - result['distance'] if result['distance'] else 1.0
                }
                for result in event_results[:n_relevant]
            ]

            print(f"[RETRIEVAL] - {len(retrieval['relevant_events'])} relevant events")

        # 4. Surprise callbacks (random old chapters for variety)
        old_chapters = [
            ch for ch in memory.chapters.values()
            if ch.chapter_number < (memory.current_chapter_number - n_recent - 5)
        ]

        if old_chapters and n_surprise > 0:
            surprise_chapters = random.sample(
                old_chapters,
                min(n_surprise, len(old_chapters))
            )

            retrieval["surprise_callbacks"] = [
                {
                    "chapter_id": ch.chapter_id,
                    "chapter_number": ch.chapter_number,
                    "title": ch.title,
                    "key_event": random.choice(ch.key_events) if ch.key_events else "",
                    "note": "Consider subtle callback"
                }
                for ch in surprise_chapters
            ]

            print(f"[RETRIEVAL] - {len(surprise_chapters)} surprise callback opportunities")

        # 5. Active plot threads
        active_threads = [
            t for t in memory.plot_threads.values()
            if t.status in ["open", "progressing"]
        ]

        retrieval["active_threads"] = [
            {
                "thread_id": t.thread_id,
                "name": t.name,
                "type": t.thread_type,
                "importance": t.importance,
                "status": t.status
            }
            for t in sorted(active_threads, key=lambda x: x.importance, reverse=True)[:5]
        ]

        print(f"[RETRIEVAL] - {len(retrieval['active_threads'])} active threads")
        print(f"[OK] Context retrieved")

        return retrieval

    def search_character_history(
        self,
        character_name: str,
        n_results: int = 5
    ) -> list[dict]:
        """
        Search for past events involving a specific character.

        Args:
            character_name: Name of the character
            n_results: Number of results

        Returns:
            List of relevant events
        """
        query = f"{character_name} character development moment action"
        return self.vector_store.search_events(query=query, n_results=n_results)

    def find_similar_situations(
        self,
        situation_description: str,
        n_results: int = 3
    ) -> list[dict]:
        """
        Find past chapters/events with similar situations.

        Args:
            situation_description: Description of current situation
            n_results: Number of results

        Returns:
            List of similar past situations
        """
        return self.vector_store.search_events(
            query=situation_description,
            n_results=n_results
        )

    def get_thread_history(
        self,
        thread_name: str,
        memory: StoryMemory
    ) -> list[dict]:
        """
        Get the full history of a plot thread.

        Args:
            thread_name: Name of the thread
            memory: Story memory

        Returns:
            List of developments in chronological order
        """
        # Find the thread
        thread = None
        for t in memory.plot_threads.values():
            if t.name == thread_name:
                thread = t
                break

        if not thread:
            return []

        # Get all developments
        developments = [
            {
                "chapter_id": dev["chapter_id"],
                "description": dev["description"],
                "chapter": memory.chapters.get(dev["chapter_id"])
            }
            for dev in thread.developments
        ]

        return developments
