#!/usr/bin/env python3
"""
Quick test script to verify game delete functionality.
Run this after starting the Flask app to test the delete route.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.models import Game, GameNight
from app.services import GameService
from datetime import date


def test_delete():
    """Test game delete functionality."""
    app = create_app('development')

    with app.app_context():
        print("Testing Game Delete Functionality")
        print("=" * 50)

        # Create a test game night
        game_night = GameNight(
            name="Test Night",
            date=date.today(),
            is_active=True
        )
        db.session.add(game_night)
        db.session.commit()
        print(f"✓ Created test game night: {game_night.name}")

        # Create a test game
        game_data = {
            'name': 'Test Game to Delete',
            'type': 'trivia',
            'sequence_number': 999,
            'point_scheme': 1,
            'metric_type': 'score',
            'scoring_direction': 'higher_better',
            'public_input': False
        }

        game = GameService.create_game(game_data, game_night_id=game_night.id)
        game_id = game.id
        print(f"✓ Created test game: {game.name} (ID: {game_id})")

        # Verify game exists
        found_game = Game.query.get(game_id)
        assert found_game is not None, "Game should exist"
        print(f"✓ Verified game exists in database")

        # Delete the game
        print(f"\nDeleting game {game_id}...")
        GameService.delete_game(game_id)
        print(f"✓ GameService.delete_game() called successfully")

        # Verify game is deleted
        deleted_game = Game.query.get(game_id)
        assert deleted_game is None, "Game should be deleted"
        print(f"✓ Verified game is deleted from database")

        # Cleanup
        db.session.delete(game_night)
        db.session.commit()
        print(f"✓ Cleaned up test game night")

        print("\n" + "=" * 50)
        print("✓ ALL TESTS PASSED - Game delete functionality works!")
        print("=" * 50)

        return True


if __name__ == '__main__':
    try:
        test_delete()
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
