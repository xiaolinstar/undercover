import time
import requests


class WeChatClient:
    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self._token = None
        self._expires_at = 0

    def _get_token(self) -> str:
        now = int(time.time())
        if self._token and now < self._expires_at - 60:
            return self._token
        url = (
            "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential"
            f"&appid={self.app_id}&secret={self.app_secret}"
        )
        try:
            r = requests.get(url, timeout=5)
            data = r.json()
            token = data.get("access_token")
            expires_in = int(data.get("expires_in", 0))
            if token and expires_in:
                self._token = token
                self._expires_at = now + expires_in
                return token
        except Exception:
            pass
        return ""

    def send_text(self, openid: str, content: str) -> bool:
        token = self._get_token()
        if not token:
            return False
        url = f"https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={token}"
        payload = {"touser": openid, "msgtype": "text", "text": {"content": content}}
        try:
            r = requests.post(url, json=payload, timeout=5)
            data = r.json()
            return data.get("errcode", 0) == 0
        except Exception:
            return False

    def get_user_nickname(self, openid: str) -> str:
        token = self._get_token()
        if not token:
            return ""
        url = (
            "https://api.weixin.qq.com/cgi-bin/user/info"
            f"?access_token={token}&openid={openid}&lang=zh_CN"
        )
        try:
            r = requests.get(url, timeout=5)
            data = r.json()
            return str(data.get("nickname", ""))
        except Exception:
            return ""

