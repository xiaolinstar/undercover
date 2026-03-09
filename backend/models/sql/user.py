from datetime import datetime

from backend.extensions import db


class User(db.Model):
    """用户模型 (MySQL)"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    openid = db.Column(db.String(64), unique=True, nullable=False, index=True)
    unionid = db.Column(db.String(64), unique=True, index=True)
    nickname = db.Column(db.String(64))
    avatar = db.Column(db.String(255))

    # Game stats
    total_games = db.Column(db.Integer, default=0)
    wins = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "openid": self.openid,
            "nickname": self.nickname,
            "avatar": self.avatar,
            "total_games": self.total_games,
            "wins": self.wins,
            "win_rate": self.wins / self.total_games if self.total_games > 0 else 0,
        }
