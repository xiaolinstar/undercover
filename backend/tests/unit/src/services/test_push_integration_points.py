from unittest.mock import Mock, patch

from backend.repositories.room_repository import RoomRepository
from backend.repositories.user_repository import UserRepository
from backend.services.game_service import GameService


class DummyRepo:
    def __init__(self):
        self.rooms = {}
        self.users = {}

    def exists(self, rid):
        return rid in self.rooms

    def save_room(self, room):
        self.rooms[room.room_id] = room
        return True


class MockPush:
    def __init__(self):
        self.calls = []

    def enabled(self):
        return True

    def send_text(self, openid, content):
        self.calls.append((openid, content))
        return True

    def get_user_nickname(self, openid):
        return "昵称" + openid[-1]


def test_join_room_fill_nickname(monkeypatch):
    import fakeredis

    r = fakeredis.FakeRedis(decode_responses=False)
    room_repo = RoomRepository(r)
    user_repo = UserRepository(r)
    push = MockPush()
    svc = GameService(room_repo, user_repo, push)
    ok, rid = svc.create_room("u1")
    assert ok
    ok, msg = svc.join_room("u2", rid)
    u2 = user_repo.get("u2")
    assert u2.nickname.startswith("昵称")


def test_start_game_push_words(monkeypatch):
    import fakeredis

    r = fakeredis.FakeRedis(decode_responses=False)
    room_repo = RoomRepository(r)
    user_repo = UserRepository(r)
    push = MockPush()
    svc = GameService(room_repo, user_repo, push)
    ok, rid = svc.create_room("u1")
    svc.join_room("u2", rid)
    svc.join_room("u3", rid)
    with patch("src.services.game_service.WordPair") as mock_word_pair:
        mock_obj = Mock()
        mock_obj.word_civilian = "苹果"
        mock_obj.word_undercover = "香蕉"
        mock_word_pair.query.order_by.return_value.first.return_value = mock_obj
        ok, res = svc.start_game(rid, "u1")
    assert ok
    assert any("您的词语" in c for _, c in push.calls)


def test_vote_push_status(monkeypatch):
    import fakeredis

    r = fakeredis.FakeRedis(decode_responses=False)
    room_repo = RoomRepository(r)
    user_repo = UserRepository(r)
    push = MockPush()
    svc = GameService(room_repo, user_repo, push)
    ok, rid = svc.create_room("u1")
    svc.join_room("u2", rid)
    svc.join_room("u3", rid)
    with patch("src.services.game_service.WordPair") as mock_word_pair:
        mock_obj = Mock()
        mock_obj.word_civilian = "苹果"
        mock_obj.word_undercover = "香蕉"
        mock_word_pair.query.order_by.return_value.first.return_value = mock_obj
        svc.start_game(rid, "u1")
    push.calls.clear()

    with (
        patch("src.services.game_service.SQLUser") as mock_sql_user,
        patch("src.services.game_service.GameRecord"),
        patch("src.services.game_service.db"),
    ):
        mock_sql_user.query.filter_by.return_value.first.return_value = Mock(id=1, total_games=0, wins=0)
        svc.vote_player("u1", 2)
    assert any("房间状态" in c for _, c in push.calls)
