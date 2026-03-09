from datetime import datetime

from backend.extensions import db


class GameRecord(db.Model):
    """对局记录"""

    __tablename__ = "game_records"

    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.String(32), index=True)  # 当时的房间号
    creator_id = db.Column(db.Integer, db.ForeignKey("users.id"))  # 房主

    winner_team = db.Column(db.String(16))  # civilian / undercover
    player_count = db.Column(db.Integer)
    undercover_count = db.Column(db.Integer)
    duration_seconds = db.Column(db.Integer)  # 持续时长

    # 词语记录
    civilian_word = db.Column(db.String(32))
    undercover_word = db.Column(db.String(32))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime)

    # 关联
    creator = db.relationship("User", backref="created_games")
