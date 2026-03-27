#!/usr/bin/env python3
"""
导入词库脚本
"""

import os
import sys

# 将项目根目录添加到 python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app_factory import AppFactory
from backend.config.game_config import GameConfig
from backend.extensions import db
from backend.models.sql import WordPair


def import_words():
    app = AppFactory.create_app()

    with app.app_context():
        print("Starting word import...")

        # 1. Check if we want to clear old words or just append
        # For now, let's keep it simple: avoid duplicates

        count = 0
        skipped = 0

        for civilian_word, undercover_word in GameConfig.WORD_PAIRS:
            # Check if exists
            exists = WordPair.query.filter_by(word_civilian=civilian_word, word_undercover=undercover_word).first()

            if exists:
                print(f"Skipping existing pair: {civilian_word} - {undercover_word}")
                skipped += 1
                continue

            new_pair = WordPair(
                category="默认", word_civilian=civilian_word, word_undercover=undercover_word, difficulty=1
            )
            db.session.add(new_pair)
            count += 1

        try:
            db.session.commit()
            print(f"Import finished! Added {count} new pairs, skipped {skipped} existing pairs.")
        except Exception as e:
            db.session.rollback()
            print(f"Error during import: {e}")


if __name__ == "__main__":
    import_words()
