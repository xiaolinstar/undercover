import hashlib
import json
import os
import random
import time
import xml.etree.ElementTree as ET

import redis
import requests
from flask import Flask, request

# 导入消息配置
from messages import ROOM_MESSAGES, GAME_MESSAGES, USER_MESSAGES, VOTE_MESSAGES, HELP_MESSAGES, ERROR_MESSAGES

app = Flask(__name__)

# 微信公众号的token，可以从环境变量获取或者硬编码
WECHAT_TOKEN = os.environ.get('WECHAT_TOKEN', 'your_wechat_token_here')  # 请替换为实际的token
WECHAT_APP_ID = os.environ.get('WECHAT_APP_ID', 'your_wechat_app_id_here')  # 请替换为实际的AppID
WECHAT_APP_SECRET = os.environ.get('WECHAT_APP_SECRET', 'your_wechat_app_secret_here')  # 请替换为实际的AppSecret

# Redis连接
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
redis_client = redis.from_url(REDIS_URL)

# 游戏词汇库
WORDS = {
    "水果类": [
        ("苹果", "香蕉"),
        ("西瓜", "冬瓜"),
        ("草莓", "樱桃"),
        ("橙子", "橘子"),
        ("葡萄", "提子")
    ],
    "动物类": [
        ("老虎", "狮子"),
        ("大象", "犀牛"),
        ("猴子", "猩猩"),
        ("企鹅", "海豚"),
        ("熊猫", "树袋熊")
    ],
    "生活用品类": [
        ("牙刷", "梳子"),
        ("雨伞", "雨衣"),
        ("手机", "电脑"),
        ("钱包", "背包"),
        ("眼镜", "墨镜")
    ]
}




@app.route('/hello', methods=['GET'])
def hello_world():
    return 'Hello World!'


@app.route('/health', methods=['GET'])
def health_check():
    return 'OK', 200


@app.route('/menu', methods=['GET'])
def show_menu():
    """显示菜单内容"""
    menu_text = """谁是卧底游戏菜单：
1. 创建房间
2. 加入房间+房间号
3. 开始游戏
4. 查看状态
5. t+序号 (房主投票)
6. 帮助"""
    return menu_text


@app.route('/create_menu', methods=['POST'])
def create_custom_menu():
    """
    创建自定义菜单
    根据微信官方文档：https://developers.weixin.qq.com/doc/offiaccount/Custom_Menus/Creating_Custom-Defined_Menu.html
    """
    try:
        # 获取access_token
        access_token = get_access_token()
        if not access_token:
            return {"error": "Failed to get access token"}, 500
        
        # 读取菜单配置
        menu_config_path = os.path.join(os.path.dirname(__file__), 'menu_config.json')
        with open(menu_config_path, 'r', encoding='utf-8') as f:
            menu_data = json.load(f)
        
        # 调用微信API创建菜单
        url = f"https://api.weixin.qq.com/cgi-bin/menu/create?access_token={access_token}"
        response = requests.post(url, json=menu_data)
        
        result = response.json()
        if result.get('errcode') == 0:
            return {"message": "Menu created successfully"}, 200
        else:
            return {"error": f"Failed to create menu: {result}"}, 500
            
    except Exception as e:
        app.logger.error(f"Error creating custom menu: {e}")
        return {"error": str(e)}, 500


@app.route('/get_access_token', methods=['GET'])
def get_access_token_api():
    """
    获取access_token接口（用于调试）
    """
    try:
        access_token = get_access_token()
        if access_token:
            return {"access_token": access_token}, 200
        else:
            return {"error": "Failed to get access token"}, 500
    except Exception as e:
        return {"error": str(e)}, 500


def get_access_token():
    """
    获取微信access_token
    根据微信官方文档：https://developers.weixin.qq.com/doc/offiaccount/Basic_Information/Get_access_token.html
    """
    try:
        # 检查缓存中是否有有效的access_token
        cached_token = redis_client.get('wechat_access_token')
        if cached_token:
            return cached_token.decode('utf-8')
        
        # 请求新的access_token
        url = f"https://api.weixin.qq.com/cgi-bin/token"
        params = {
            'grant_type': 'client_credential',
            'appid': WECHAT_APP_ID,
            'secret': WECHAT_APP_SECRET
        }
        
        response = requests.get(url, params=params)
        result = response.json()
        
        if 'access_token' in result:
            access_token = result['access_token']
            expires_in = result.get('expires_in', 7200) - 60  # 提前60秒过期
            
            # 缓存access_token
            redis_client.setex('wechat_access_token', expires_in, access_token)
            
            return access_token
        else:
            app.logger.error(f"Failed to get access token: {result}")
            return None
            
    except Exception as e:
        app.logger.error(f"Error getting access token: {e}")
        return None


@app.route('/', methods=['GET'])
def wechat_verify():
    """
    处理微信公众号的signature检验
    根据微信文档：https://developers.weixin.qq.com/doc/subscription/guide/dev/push/
    """
    try:
        # 获取微信服务器发送的参数
        signature = request.args.get('signature')
        timestamp = request.args.get('timestamp')
        nonce = request.args.get('nonce')
        echostr = request.args.get('echostr')
        
        if not all([signature, timestamp, nonce, echostr]):
            return 'Missing parameters', 400
        
        # 将token、timestamp、nonce按字典序排序
        sorted_list = sorted([WECHAT_TOKEN, timestamp, nonce])
        
        # 将排序后的三个字符串拼接成一个字符串
        combined_str = ''.join(sorted_list)
        
        # 对拼接后的字符串进行sha1加密
        sha1 = hashlib.sha1()
        sha1.update(combined_str.encode('utf-8'))
        encrypted_str = sha1.hexdigest()
        
        # 将加密后的字符串与signature比较
        if encrypted_str == signature:
            return echostr  # 验证成功，返回echostr
        else:
            return 'Invalid signature', 403
    except Exception as e:
        app.logger.error(f'Wechat verification error: {e}')
        return 'Internal server error', 500


@app.route('/', methods=['POST'])
def wechat_response():
    """
    处理微信公众号的消息推送
    """
    try:
        # 解析XML消息
        xml_data = request.data
        root = ET.fromstring(xml_data)
        
        # 提取消息信息
        to_user = root.find('ToUserName').text
        from_user = root.find('FromUserName').text
        msg_type = root.find('MsgType').text

        # 初始化响应内容
        response_content = ""
        
        if msg_type == 'text':
            content = root.find('Content').text
            response_content = handle_text_message(from_user, content)
        elif msg_type == 'event':
            event = root.find('Event').text
            if event == 'subscribe':
                response_content = "欢迎关注！请输入'谁是卧底'查看游戏玩法和帮助信息"
            elif event == 'CLICK':
                event_key = root.find('EventKey').text
                if event_key == 'WHO_IS_UNDERCOVER':
                    response_content = GAME_INSTRUCTIONS
                else:
                    response_content = "暂不支持此菜单选项"
            else:
                response_content = "暂不支持此事件类型"
        else:
            response_content = "暂不支持此消息类型"
        
        # 构造响应XML
        response_xml = f"""
        <xml>
        <ToUserName><![CDATA[{from_user}]]></ToUserName>
        <FromUserName><![CDATA[{to_user}]]></FromUserName>
        <CreateTime>{int(time.time())}</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[{response_content}]]></Content>
        </xml>
        """
        
        return response_xml
    except Exception as e:
        app.logger.error(f'Wechat message processing error: {e}')
        return 'success'  # 微信服务器要求即使出错也要返回success


def handle_text_message(user_id, content):
    """
    处理文本消息
    """
    content = content.strip().lower()
    
    # 处理用户命令
    if content == '谁是卧底':
        return HELP_MESSAGES["INSTRUCTIONS"]
    elif content == '创建房间':
        return create_room(user_id)
    elif content.startswith('加入房间'):
        room_id = content[4:].strip()  # 去掉"加入房间"前缀
        return join_room(user_id, room_id)
    elif content == '开始游戏':
        return start_game(user_id)
    elif content == '查看状态':
        return show_status(user_id)
    elif content == '查看词语':
        return show_word(user_id)
    elif content.startswith('t'):
        # 房主投票，格式为 t+序号
        try:
            target_index = int(content[1:])
            return handle_vote_by_index(user_id, target_index)
        except ValueError:
            return ERROR_MESSAGES["VOTE_FORMAT_ERROR"]
    elif content == '帮助':
        return HELP_MESSAGES["INSTRUCTIONS"]
    else:
        return ERROR_MESSAGES["UNKNOWN_COMMAND"]


def create_room(user_id):
    """
    创建新房间
    """
    # 生成4位随机房间号
    room_id = str(random.randint(1000, 9999))
    
    # 确保房间号唯一
    while get_room(room_id):
        room_id = str(random.randint(1000, 9999))
    
    # 创建房间
    room_data = {
        'room_id': room_id,
        'creator': user_id,
        'players': [user_id],
        'status': 'waiting',  # waiting, playing, ended
        'words': None,
        'undercovers': [],  # 多个卧底
        'current_round': 1,
        'eliminated': []
    }
    
    # 保存房间信息
    save_room(room_id, room_data)
    
    # 保存用户信息
    user_data = {
        'openid': user_id,
        'nickname': f'玩家1',
        'current_room': room_id
    }
    save_user(user_id, user_data)
    
    return ROOM_MESSAGES["CREATE_SUCCESS"].format(room_id=room_id)


def join_room(user_id, room_id):
    """
    加入房间
    """
    # 检查房间是否存在
    room = get_room(room_id)
    if not room:
        return ROOM_MESSAGES["NOT_FOUND"]
    
    # 检查房间状态
    if room['status'] != 'waiting':
        return ROOM_MESSAGES["GAME_STARTED"]
    
    # 检查是否已在房间中
    if user_id in room['players']:
        return ROOM_MESSAGES["ALREADY_IN_ROOM"]
    
    # 检查房间人数
    if len(room['players']) >= 12:
        return ROOM_MESSAGES["ROOM_FULL"]
    
    # 加入房间
    room['players'].append(user_id)
    
    # 保存房间信息
    save_room(room_id, room)
    
    # 保存用户信息
    user_data = {
        'openid': user_id,
        'nickname': f'玩家{len(room["players"])}',
        'current_room': room_id
    }
    save_user(user_id, user_data)
    
    # 通知房间内其他人有新玩家加入
    notify_players(room_id, ROOM_MESSAGES["JOIN_NOTIFICATION"].format(player_count=len(room['players'])))
    
    return ROOM_MESSAGES["JOIN_SUCCESS"].format(room_id=room_id, player_count=len(room['players']))


def start_game(user_id):
    """
    开始游戏
    """
    # 获取用户信息
    user_data = get_user(user_id)
    if not user_data or not user_data.get('current_room'):
        return USER_MESSAGES["NOT_IN_ROOM"]
    
    room_id = user_data['current_room']
    room = get_room(room_id)
    
    # 检查是否为房主
    if room['creator'] != user_id:
        return ROOM_MESSAGES["NOT_OWNER"]
    
    # 检查房间人数
    if len(room['players']) < 3:
        return ROOM_MESSAGES["INSUFFICIENT_PLAYERS"]
    
    # 检查房间状态
    if room['status'] == 'playing':
        return ROOM_MESSAGES["GAME_ALREADY_STARTED"]
    elif room['status'] == 'ended':
        return ROOM_MESSAGES["GAME_ENDED"]
    
    # 根据人数确定卧底数量
    player_count = len(room['players'])
    if 3 <= player_count <= 5:
        undercover_count = 1
    elif 6 <= player_count <= 8:
        undercover_count = 2
    elif 9 <= player_count <= 12:
        undercover_count = 3
    else:
        return ROOM_MESSAGES["INVALID_PLAYER_COUNT"]
    
    # 随机选择卧底
    room['undercovers'] = random.sample(room['players'], undercover_count)
    
    # 随机选择词语类别和词语对
    category = random.choice(list(WORDS.keys()))
    word_pair = random.choice(WORDS[category])
    
    # 分配词语
    room['words'] = {
        'civilian': word_pair[0],
        'undercover': word_pair[1]
    }
    
    # 更新房间状态
    room['status'] = 'playing'
    
    # 保存房间信息
    save_room(room_id, room)
    
    # 通知所有玩家游戏开始和各自的词语
    for player in room['players']:
        if player in room['undercovers']:
            word = room['words']['undercover']
        else:
            word = room['words']['civilian']
        
        send_message(player, GAME_MESSAGES["START_NOTIFICATION"].format(word=word))
    
    # 特别提醒房主
    send_message(room['creator'], GAME_MESSAGES["OWNER_REMINDER"])
    
    return VOTE_MESSAGES["SUCCESS"]  # 对于发起者不需要回复


def handle_vote_by_index(user_id, target_index):
    """
    处理房主通过序号投票
    """
    # 获取用户信息
    user_data = get_user(user_id)
    if not user_data or not user_data.get('current_room'):
        return USER_MESSAGES["NOT_IN_ROOM"]
    
    room_id = user_data['current_room']
    room = get_room(room_id)
    
    # 检查游戏状态
    if room['status'] != 'playing':
        return VOTE_MESSAGES["GAME_NOT_PLAYING"]
    
    # 检查是否为房主
    if room['creator'] != user_id:
        return VOTE_MESSAGES["NOT_OWNER"]
    
    # 检查序号是否有效
    if target_index < 1 or target_index > len(room['players']):
        return VOTE_MESSAGES["INVALID_INDEX"]
    
    # 获取目标玩家
    target_player = room['players'][target_index - 1]
    
    # 检查目标玩家是否已被淘汰
    if target_player in room['eliminated']:
        return VOTE_MESSAGES["PLAYER_ELIMINATED"]
    
    # 记录被淘汰的玩家
    room['eliminated'].append(target_player)
    
    # 保存房间信息
    save_room(room_id, room)
    
    # 通知结果
    target_data = get_user(target_player)
    target_nickname = target_data['nickname'] if target_data else f'玩家{target_index}'
    notify_players(room_id, VOTE_MESSAGES["ELIMINATION_RESULT"].format(nickname=target_nickname))
    
    # 检查游戏是否结束
    check_game_end(room_id)
    
    return VOTE_MESSAGES["SUCCESS"]


def check_game_end(room_id):
    """
    检查游戏是否结束，如果结束则自动让玩家退出房间
    """
    room = get_room(room_id)
    
    # 检查是否有卧底被淘汰
    eliminated_undercovers = set(room['undercovers']) & set(room['eliminated'])
    
    # 如果所有卧底都被淘汰，平民获胜
    if len(eliminated_undercovers) == len(room['undercovers']):
        room['status'] = 'ended'
        save_room(room_id, room)
        notify_players(room_id, GAME_MESSAGES["CIVILIAN_WIN"])
        
        # 游戏结束后，让所有玩家自动退出房间
        for player_id in room['players']:
            user_data = get_user(player_id)
            if user_data and user_data.get('current_room') == room_id:
                user_data.pop('current_room', None)
                save_user(player_id, user_data)
        
        return
    
    # 检查剩余玩家数量
    remaining_players = [player for player in room['players'] if player not in room['eliminated']]
    
    # 如果剩余玩家少于3人，游戏结束
    if len(remaining_players) < 3:
        room['status'] = 'ended'
        save_room(room_id, room)
        notify_players(room_id, GAME_MESSAGES["UNDERCOVER_WIN"])
        
        # 游戏结束后，让所有玩家自动退出房间
        for player_id in room['players']:
            user_data = get_user(player_id)
            if user_data and user_data.get('current_room') == room_id:
                user_data.pop('current_room', None)
                save_user(player_id, user_data)
        
        return
    
    # 检查卧底数量是否大于等于平民数量
    remaining_undercovers = set(remaining_players) & set(room['undercovers'])
    remaining_civilians = set(remaining_players) - set(remaining_undercovers)
    
    if len(remaining_undercovers) >= len(remaining_civilians):
        room['status'] = 'ended'
        save_room(room_id, room)
        notify_players(room_id, GAME_MESSAGES["UNDERCOVER_WIN"])
        
        # 游戏结束后，让所有玩家自动退出房间
        for player_id in room['players']:
            user_data = get_user(player_id)
            if user_data and user_data.get('current_room') == room_id:
                user_data.pop('current_room', None)
                save_user(player_id, user_data)
        
        return
    
    # 游戏继续，进入下一轮
    room['current_round'] += 1
    save_room(room_id, room)
    
    # 通知进入下一轮
    notify_players(room_id, GAME_MESSAGES["ROUND_NOTIFICATION"].format(round_number=room['current_round']))


def show_status(user_id):
    """
    显示当前状态，包括用户的序号和昵称
    """
    # 获取用户信息
    user_data = get_user(user_id)
    if not user_data or not user_data.get('current_room'):
        return "您不在任何房间中"
    
    room_id = user_data['current_room']
    room = get_room(room_id)
    
    # 找到当前用户的序号
    user_index = -1
    for i, player in enumerate(room['players']):
        if player == user_id:
            user_index = i + 1
            break
    
    status_text = f"您的信息：{user_data['nickname']} (序号: {user_index})\n\n房间号：{room_id}\n房间状态：{room['status']}\n房间成员："
    
    for i, player in enumerate(room['players']):
        player_data = get_user(player)
        nickname = player_data['nickname'] if player_data else f'玩家{i+1}'
        if player == room['creator']:
            nickname += "(房主)"
        if player in room.get('eliminated', []):
            nickname += "(已淘汰)"
        status_text += f"\n{i+1}. {nickname}"
    
    if room['status'] == 'playing':
        status_text += f"\n\n当前轮次：第{room['current_round']}轮"
        status_text += f"\n已淘汰：{len(room.get('eliminated', []))}人"
        
        # 如果是房主，提示投票方式
        if room['creator'] == user_id:
            status_text += f"\n\n您是房主，可通过't+序号'投票淘汰玩家"
    
    return status_text


def show_word(user_id):
    """
    显示玩家的词语信息
    """
    # 获取用户信息
    user_data = get_user(user_id)
    if not user_data or not user_data.get('current_room'):
        return USER_MESSAGES["NOT_IN_ROOM"]
    
    room_id = user_data['current_room']
    room = get_room(room_id)
    
    # 检查游戏是否已开始
    if room['status'] != 'playing':
        return USER_MESSAGES["GAME_NOT_STARTED"]
    
    # 检查用户是否在房间中
    if user_id not in room['players']:
        return USER_MESSAGES["NOT_IN_CURRENT_ROOM"]
    
    # 获取用户的词语
    if user_id in room['undercovers']:
        word = room['words']['undercover']
    else:
        word = room['words']['civilian']
    
    return f"您的词语：{word}\n请根据您的词语进行描述，注意不要暴露自己的身份"





def notify_players(room_id, message, exclude=None):
    """
    通知房间内的所有玩家
    """
    room = get_room(room_id)
    for player in room['players']:
        if player != exclude:
            send_message(player, message)


def send_message(user_id, message):
    """
    发送消息给指定用户（通过微信客服消息接口）
    根据微信官方文档：https://developers.weixin.qq.com/doc/service/api/customer/message/api_sendcustommessage.html
    """
    try:
        # 获取access_token
        access_token = get_access_token()
        if not access_token:
            app.logger.error("Failed to get access token for sending message")
            # 如果无法获取access_token，回退到打印消息
            print(f"发送给 {user_id} 的消息: {message}")
            return False
        
        # 构造发送客服消息的URL
        url = f"https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={access_token}"
        
        # 构造消息数据
        message_data = {
            "touser": user_id,
            "msgtype": "text",
            "text": {
                "content": message
            }
        }
        
        # 发送POST请求
        response = requests.post(url, json=message_data)
        result = response.json()
        
        # 检查发送结果
        if result.get('errcode') == 0:
            return True
        else:
            app.logger.error(f"Failed to send message to {user_id}: {result}")
            return False
            
    except Exception as e:
        app.logger.error(f"Error sending message to {user_id}: {e}")
        # 如果发送失败，回退到打印消息
        print(f"发送给 {user_id} 的消息: {message}")
        return False


def get_room(room_id):
    """
    从Redis获取房间信息
    """
    try:
        room_data = redis_client.get(f"room:{room_id}")
        if room_data:
            return json.loads(room_data)
        return None
    except Exception as e:
        app.logger.error(f"Error getting room {room_id}: {e}")
        return None


def save_room(room_id, room_data):
    """
    将房间信息保存到Redis，设置2小时过期时间
    """
    try:
        redis_client.setex(f"room:{room_id}", 2*60*60, json.dumps(room_data))  # 2小时过期
    except Exception as e:
        app.logger.error(f"Error saving room {room_id}: {e}")


def get_user(user_id):
    """
    从Redis获取用户信息
    """
    try:
        user_data = redis_client.get(f"user:{user_id}")
        if user_data:
            return json.loads(user_data)
        return None
    except Exception as e:
        app.logger.error(f"Error getting user {user_id}: {e}")
        return None


def save_user(user_id, user_data):
    """
    将用户信息保存到Redis
    """
    try:
        redis_client.set(f"user:{user_id}", json.dumps(user_data))
    except Exception as e:
        app.logger.error(f"Error saving user {user_id}: {e}")


def get_all_users():
    """
    获取所有用户（用于生成用户昵称）
    """
    try:
        user_keys = redis_client.keys('user:*')
        users = []
        for key in user_keys:
            user_data = redis_client.get(key)
            if user_data:
                try:
                    user = json.loads(user_data)
                    users.append(user)
                except json.JSONDecodeError:
                    continue
        return users
    except Exception as e:
        app.logger.error(f"获取所有用户时出错: {e}")
        return []


if __name__ == '__main__':
    app.run()