from typing import Optional


class PushService:
    def __init__(self, client):
        self.client = client

    def enabled(self) -> bool:
        return self.client is not None

    def send_text(self, openid: str, content: str) -> bool:
        if not self.enabled():
            return False
        return bool(self.client.send_text(openid, content))

    def get_user_nickname(self, openid: str) -> str:
        if not self.enabled():
            return ""
        return self.client.get_user_nickname(openid)

