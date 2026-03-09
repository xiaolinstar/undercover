from backend.extensions import db


class WordPair(db.Model):
    """词语对"""

    __tablename__ = "word_pairs"

    id = db.Column(db.Integer, primary_key=True)

    category = db.Column(db.String(32), index=True)  # 如: 生活、职场

    word_civilian = db.Column(db.String(32), nullable=False)
    word_undercover = db.Column(db.String(32), nullable=False)

    difficulty = db.Column(db.Integer, default=1)  # 1-3?

    is_deleted = db.Column(db.Boolean, default=False)

    __table_args__ = (db.UniqueConstraint("word_civilian", "word_undercover", name="unique_pair"),)
