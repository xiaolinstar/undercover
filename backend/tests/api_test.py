import uuid
from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.usefixtures("app")
class TestApiIntegration:
    """API 集成测试类"""

    @patch("src.services.auth_service.requests.get")
    def test_full_game_flow(self, mock_get, client):
        """测试完整的游戏流程"""

        base_openid = str(uuid.uuid4())

        def mock_side_effect(*args, **kwargs):
            resp = MagicMock()
            params = kwargs.get("params", {})
            code = params.get("js_code")
            print(f"DEBUG: login code={code}")

            if code and "mock_code_1" in code:
                openid = f"{base_openid}_1"
            elif code and "mock_code_2" in code:
                openid = f"{base_openid}_2"
            elif code and "mock_code_3" in code:
                openid = f"{base_openid}_3"
            else:
                openid = "unknown"

            print(f"DEBUG: returning openid={openid}")
            resp.json.return_value = {"openid": openid, "session_key": "xxx"}
            return resp

        mock_get.side_effect = mock_side_effect

        print("\n=== 开始全流程测试 ===")

        print("1. 模拟用户1登录...")

        resp = client.post("/api/v1/auth/login", json={"code": "mock_code_1"})
        assert resp.status_code == 200
        data = resp.json
        token1 = data["data"]["token"]
        headers1 = {"Authorization": f"Bearer {token1}"}
        print("   用户1登录成功")

        print("2. 用户1创建房间...")
        resp = client.post("/api/v1/room/create", json={}, headers=headers1)
        assert resp.status_code == 200
        room_id = resp.json["data"]["room_id"]
        print(f"   房间创建成功，房间号: {room_id}")

        print("3. 模拟其他用户加入...")
        users = []
        for i in range(2, 4):
            resp = client.post("/api/v1/auth/login", json={"code": f"mock_code_{i}"})
            assert resp.status_code == 200
            token = resp.json["data"]["token"]
            headers = {"Authorization": f"Bearer {token}"}
            users.append(headers)

            resp = client.post("/api/v1/room/join", json={"room_id": room_id}, headers=headers)
            assert resp.status_code == 200
            print(f"   用户{i}加入房间")

        headers2 = users[0]
        headers3 = users[1]

        print("4. 获取房间状态...")
        resp = client.get(f"/api/v1/room/{room_id}", headers=headers1)
        assert resp.status_code == 200
        data = resp.json["data"]
        assert data["player_count"] == 3
        assert data["status"] == "waiting"
        print(f"   当前房间人数: {data['player_count']}, 状态: {data['status']}")

        print("5. 开始游戏...")
        resp = client.post("/api/v1/game/start", json={"room_id": room_id, "user_id": "mock_openid_test_code_1"}, headers=headers1)
        if resp.status_code != 200:
            print(f"Failed to start game: {resp.json}")
        assert resp.status_code == 200
        print("   游戏开始成功")

        print("6. 获取词语...")
        resp = client.get(f"/api/v1/game/word?room_id={room_id}", headers=headers1)
        assert resp.status_code == 200
        word1 = resp.json["data"]["word"]
        print(f"   用户1词语: {word1}")

        resp = client.get(f"/api/v1/game/word?room_id={room_id}", headers=headers2)
        word2 = resp.json["data"]["word"]
        print(f"   用户2词语: {word2}")

        resp = client.get(f"/api/v1/game/word?room_id={room_id}", headers=headers3)
        word3 = resp.json["data"]["word"]
        print(f"   用户3词语: {word3}")

        print("7. 投票...")
        resp = client.post(f"/api/v1/game/vote", json={"room_id": room_id, "target_uid": "mock_openid_test_code_2"}, headers=headers1)
        assert resp.status_code == 200
        print("   用户1投票给用户2成功")

        resp = client.get(f"/api/v1/room/{room_id}", headers=headers1)
        eliminated = [p for p in resp.json["data"]["players"] if p["is_eliminated"]]
        print(f"   当前被淘汰人数: {len(eliminated)}")

        print("=== 测试完成 ===")
