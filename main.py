"""
Main entry point for the Story Writer system.

This is the orchestrator that will tie together all components:
- Memory management
- Chapter planning
- Chapter writing
- State updates
"""

import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent / "src"))


def main():
    """Main entry point."""
    print("=" * 60)
    print("Oda-Style Manga Story Engine (OSSE)")
    print("=" * 60)
    print()
    print("Welcome to the Story Writer!")
    print()
    print("Current Status: Phase 0 - Foundation Complete")
    print()
    print("Next Steps:")
    print("  1. Verify setup: python test_setup.py")
    print("  2. Set up .env with your API key")
    print("  3. Customize config/world_seed.yaml")
    print("  4. Build Phase 1 components:")
    print("     - Memory store (JSON)")
    print("     - Chapter planner")
    print("     - Chapter writer")
    print("     - State updater")
    print()
    print("Once Phase 1 is complete, this script will generate chapters!")
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
