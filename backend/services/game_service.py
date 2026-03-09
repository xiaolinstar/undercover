#!/usr/bin/env python3
"""
游戏服务类
实现游戏的核心业务逻辑
"""

import random
from datetime import datetime

from sqlalchemy.sql.expression import func

from backend.config.game_config import GameConfig
from backend.exceptions import (
    ClientException,
    DomainException,
    GameAlreadyStartedError,
    GameEndedError,
    GameNotStartedError,
    InsufficientPlayersError,
    InvalidPlayerIndexError,
    PlayerEliminatedError,
    RepositoryException,
    RoomFullError,
    RoomNotFoundError,
    RoomPermissionError,
    RoomStateError,
    UserAlreadyInRoomError,
    UserNotInRoomError,
)
from backend.extensions import db
from backend.fsm.game_state_machine import GameEvent, GameState, GameStateMachine
from backend.models.room import Room, RoomStatus
from backend.models.sql import GameRecord, User as SQLUser, WordPair
from backend.models.user import User
from backend.repositories.room_repository import RoomRepository
from backend.repositories.user_repository import UserRepository
from backend.services.push_service import PushService
from backend.utils.logger import log_business_event, log_exception, setup_logger

logger = setup_logger(__name__)


class GameService:
    """游戏服务类"""

    def __init__(
        self, 
        room_repo: RoomRepository, 
        user_repo: UserRepository, 
        push_service: PushService | None = None,
        notification_service = None  # 添加 notification_service 参数
    ):
        self.room_repo = room_repo
        self.user_repo = user_repo
        # self.word_generator = WordGenerator(GameConfig.WORD_PAIRS)
        self.fsm = GameStateMachine()
        self.push = push_service
        self.notification = notification_service  # 存储 notification_service
        self.push = push_service

    def create_room(self, user_id: str) -> tuple[bool, str]:
        """创建房间"""
        try:
            from backend.utils.snowflake import generate_snowflake_id
            
            # 使用雪花算法生成唯一的房间ID（主键）
            room_id = generate_snowflake_id()
            
            # 生成 4 位数字的房间短码（用户友好）
            room_code = self._generate_unique_room_code()

            # 创建房间对象
            room = Room(room_id=room_id, creator=user_id, room_code=room_code, players=[user_id])

            # 创建用户对象
            user = User(openid=user_id, nickname="玩家1", current_room=room_id)

            # 保存房间和用户信息
            self.room_repo.save(room)
            self.user_repo.save(user)

            if self.push and self.push.enabled():
                nickname = self.push.get_user_nickname(user_id)
                if nickname:
                    user.nickname = nickname
                    self.user_repo.save(user)
            else:
                logger.warning("推送服务未启用，无法获取用户昵称")

            log_business_event(logger, "房间创建成功", user_id=user_id, room_id=room_id)
            return True, room_id

        except RepositoryException as e:
            log_exception(logger, e, {"user_id": user_id})
            return False, "创建房间失败，请稍后重试"

        except Exception as e:
            log_exception(logger, e, {"user_id": user_id})
            return False, "创建房间时发生错误"

    def join_room(self, user_id: str, room_id: str) -> tuple[bool, str]:
        """加入房间"""
        try:
            # 获取用户信息
            user = self.user_repo.get(user_id)
            if user and user.has_joined_room():
                # 用户已经在其他房间中
                raise UserAlreadyInRoomError(user_id, user.current_room)

            # 检查房间是否存在
            room = self.room_repo.get(room_id)
            if not room:
                raise RoomNotFoundError(room_id)

            # 检查房间状态
            if room.status != RoomStatus.WAITING:
                raise RoomStateError(
                    message="游戏已经开始，无法加入房间",
                    error_code="ROOM-STATE-003",
                    details={"room_id": room_id, "status": room.status.value},
                )

            # 检查是否已在房间中
            if room.is_player(user_id):
                raise UserAlreadyInRoomError(user_id, room_id)

            # 检查房间人数
            if room.get_player_count() >= GameConfig.MAX_PLAYERS:
                raise RoomFullError(room_id, GameConfig.MAX_PLAYERS)

            # 加入房间
            room.players.append(user_id)

            # 创建或更新用户对象
            if not user:
                user = User(openid=user_id, nickname=f"玩家{room.get_player_count()}", current_room=room_id)
            else:
                user.current_room = room_id
                user.nickname = f"玩家{room.get_player_count()}"

            # 保存房间和用户信息
            self.room_repo.save(room)
            self.user_repo.save(user)

            if self.push and self.push.enabled():
                nickname = self.push.get_user_nickname(user_id)
                if nickname:
                    user.nickname = nickname
                    self.user_repo.save(user)

            # 发送 WebSocket 通知
            if self.notification:
                from backend.websocket.events import RoomEvent
                self.notification.notify_room(
                    room_id=room_id,
                    event=RoomEvent.PLAYER_JOINED.value,
                    data={
                        "player_count": room.get_player_count(),
                        "hint": f"{user.nickname} 加入了房间"
                    }
                )

            log_business_event(
                logger, "用户加入房间", user_id=user_id, room_id=room_id, player_count=room.get_player_count()
            )
            return True, f"成功加入房间，当前房间人数：{room.get_player_count()}"

        except (DomainException, ClientException) as e:
            logger.warning(f"用户/业务异常: {e.error_code} - {e.message}", extra={"details": e.details})
            return False, e.message

        except RepositoryException as e:
            log_exception(logger, e, {"user_id": user_id, "room_id": room_id})
            return False, "加入房间失败，请稍后重试"

        except Exception as e:
            log_exception(logger, e, {"user_id": user_id, "room_id": room_id})
            return False, "加入房间时发生错误"

    def start_game(self, room_id: str, user_id: str) -> tuple[bool, str]:
        """开始游戏"""
        try:
            # 获取用户信息
            user = self.user_repo.get(user_id)
            if not user or not user.has_joined_room():
                raise UserNotInRoomError(user_id)

            # 获取房间信息
            room = self.room_repo.get(room_id)
            if not room:
                raise RoomNotFoundError(room_id)

            # 检查是否为房主
            if not room.is_creator(user_id):
                raise RoomPermissionError(user_id, "开始游戏")

            # 检查房间人数
            if room.get_player_count() < GameConfig.MIN_PLAYERS:
                raise InsufficientPlayersError(room.get_player_count(), GameConfig.MIN_PLAYERS)

            # 检查房间状态
            if room.status == RoomStatus.PLAYING:
                raise GameAlreadyStartedError()
            elif room.status == RoomStatus.ENDED:
                raise GameEndedError()

            # 状态机校验
            can_start = self.fsm.can_transition(GameState.WAITING, GameEvent.START)
            if not can_start:
                raise RoomStateError(
                    message="当前状态无法开始游戏",
                    error_code="ROOM-STATE-003",
                    details={"room_id": room.room_id, "status": room.status.value},
                )

            # 根据人数确定卧底数量
            player_count = room.get_player_count()
            undercover_count = GameConfig.get_undercover_count(player_count)
            if undercover_count == 0:
                raise InsufficientPlayersError(player_count, GameConfig.MIN_PLAYERS)

            # 随机选择卧底
            room.undercovers = random.sample(room.players, undercover_count)

            # 随机选择词语对
            # word_pair = self.word_generator.get_random_word_pair()
            word_pair_obj = WordPair.query.order_by(func.rand()).first()
            if not word_pair_obj:
                # Fallback if DB is empty (should not happen in prod if seeded)
                word_pair = ("苹果", "香蕉")
                logger.warning("Database empty, using fallback word pair")
            else:
                word_pair = (word_pair_obj.word_civilian, word_pair_obj.word_undercover)

            # 分配词语
            room.words = {"civilian": word_pair[0], "undercover": word_pair[1]}

            # 更新房间状态
            next_state = self.fsm.next_state(GameState.WAITING, GameEvent.START)
            room.status = RoomStatus(next_state.value)
            room.current_round = 1

            # 保存房间信息
            self.room_repo.save(room)

            if self.push and self.push.enabled():
                for pid in room.players:
                    if pid in room.undercovers:
                        w = room.words["undercover"]
                    else:
                        w = room.words["civilian"]
                    self.push.send_text(pid, f"您的词语：{w}")

            # 发送 WebSocket 通知
            if self.notification:
                from backend.websocket.events import GameEvent as WSGameEvent
                self.notification.notify_room(
                    room_id=room.room_id,
                    event=WSGameEvent.STARTED.value,
                    data={
                        "player_count": player_count,
                        "undercover_count": undercover_count,
                        "hint": "游戏已开始，请查看您的词语"
                    }
                )

            log_business_event(
                logger,
                "游戏开始",
                user_id=user_id,
                room_id=room.room_id,
                player_count=player_count,
                undercover_count=undercover_count,
            )
            return True, "游戏开始成功"

        except (DomainException, ClientException) as e:
            logger.warning(f"用户/业务异常: {e.error_code} - {e.message}", extra={"details": e.details})
            return False, e.message

        except RepositoryException as e:
            log_exception(logger, e, {"user_id": user_id})
            return False, "开始游戏失败，请稍后重试"

        except Exception as e:
            log_exception(logger, e, {"user_id": user_id})
            return False, "开始游戏时发生错误"

    def show_word(self, user_id: str) -> tuple[bool, str]:
        """显示词语"""
        try:
            # 获取用户信息
            user = self.user_repo.get(user_id)
            if not user or not user.has_joined_room():
                raise UserNotInRoomError(user_id)

            # 获取房间信息
            room = self.room_repo.get(user.current_room)
            if not room:
                raise RoomNotFoundError(user.current_room)

            # 检查游戏状态
            if room.status != RoomStatus.PLAYING:
                raise GameNotStartedError()

            # 检查用户是否在房间中
            if not room.is_player(user_id):
                raise UserNotInRoomError(user_id)

            # 检查用户是否已被淘汰
            if room.is_eliminated(user_id):
                raise PlayerEliminatedError(user_id)

            # 根据用户身份返回对应词语
            if user_id in room.undercovers:
                word = room.words["undercover"]
            else:
                word = room.words["civilian"]

            return True, f"您的词语：{word}"

        except (DomainException, ClientException) as e:
            logger.warning(f"用户/业务异常: {e.error_code} - {e.message}", extra={"details": e.details})
            return False, e.message

        except RepositoryException as e:
            log_exception(logger, e, {"user_id": user_id})
            return False, "显示词语失败，请稍后重试"

        except Exception as e:
            log_exception(logger, e, {"user_id": user_id})
            return False, "显示词语时发生错误"

    def vote_player(self, user_id: str, target_index: int) -> tuple[bool, str]:
        """投票淘汰玩家（通过索引）"""
        try:
            # 获取用户信息
            user = self.user_repo.get(user_id)
            if not user or not user.has_joined_room():
                raise UserNotInRoomError(user_id)

            # 获取房间信息
            room = self.room_repo.get(user.current_room)
            if not room:
                raise RoomNotFoundError(user.current_room)

            # 检查游戏状态
            if room.status != RoomStatus.PLAYING:
                raise GameNotStartedError()

            # 检查是否为房主
            if not room.is_creator(user_id):
                raise RoomPermissionError(user_id, "投票")

            # 检查序号是否有效
            if target_index < 1 or target_index > room.get_player_count():
                raise InvalidPlayerIndexError(target_index, room.get_player_count())

            # 获取目标玩家
            target_player = room.players[target_index - 1]

            # 检查目标玩家是否已被淘汰
            if room.is_eliminated(target_player):
                raise PlayerEliminatedError(target_player)

            # 记录被淘汰的玩家
            room.eliminated.append(target_player)

            # 保存房间信息
            self.room_repo.save(room)

            # 状态机：投票事件保持在 PLAYING
            if not self.fsm.can_transition(GameState.PLAYING, GameEvent.VOTE):
                raise RoomStateError(
                    message="当前状态无法投票",
                    error_code="ROOM-STATE-003",
                    details={"room_id": room.room_id, "status": room.status.value},
                )

            # 发送 WebSocket 通知 - 投票提交
            if self.notification:
                from backend.websocket.events import VoteEvent
                target_user = self.user_repo.get(target_player)
                target_nickname = target_user.nickname if target_user else f"玩家{target_index}"
                self.notification.notify_room(
                    room_id=room.room_id,
                    event=VoteEvent.SUBMITTED.value,
                    data={
                        "target_index": target_index,
                        "eliminated_count": len(room.eliminated),
                        "hint": f"{target_nickname} 被投票淘汰"
                    }
                )

            # 检查游戏是否结束
            game_ended, result_message = self._check_game_end(room)

            log_business_event(
                logger,
                "投票淘汰",
                user_id=user_id,
                room_id=room.room_id,
                target_index=target_index,
                target_player=target_player,
                game_ended=game_ended,
            )

            if game_ended:
                if self.push and self.push.enabled():
                    self._push_room_status(room)
                return True, result_message
            if self.push and self.push.enabled():
                self._push_room_status(room)
            return True, "投票成功"

        except (DomainException, ClientException) as e:
            logger.warning(f"用户/业务异常: {e.error_code} - {e.message}", extra={"details": e.details})
            return False, e.message

        except RepositoryException as e:
            log_exception(logger, e, {"user_id": user_id})
            return False, "投票失败，请稍后重试"

        except Exception as e:
            log_exception(logger, e, {"user_id": user_id})
            return False, "投票时发生错误"

    def submit_vote(self, room_id: str, user_id: str, target_uid: str) -> tuple[bool, str]:
        """提交投票（通过房间ID和目标用户ID）"""
        try:
            # 获取房间信息
            room = self.room_repo.get(room_id)
            if not room:
                raise RoomNotFoundError(room_id)

            # 查找目标玩家的索引
            if target_uid not in room.players:
                return False, "目标玩家不在房间中"

            target_index = room.players.index(target_uid) + 1

            # 调用 vote_player 方法
            return self.vote_player(user_id, target_index)

        except (DomainException, ClientException) as e:
            logger.warning(f"用户/业务异常: {e.error_code} - {e.message}", extra={"details": e.details})
            return False, e.message

        except RepositoryException as e:
            log_exception(logger, e, {"user_id": user_id})
            return False, "投票失败，请稍后重试"

        except Exception as e:
            log_exception(logger, e, {"user_id": user_id})
            return False, "投票时发生错误"

    def get_player_word(self, room_id: str, user_id: str) -> dict:
        """获取玩家词语"""
        try:
            # 获取房间信息
            room = self.room_repo.get(room_id)
            if not room:
                raise RoomNotFoundError(room_id)

            # 检查用户是否在房间中
            if not room.is_player(user_id):
                raise UserNotInRoomError(user_id)

            # 检查游戏状态
            if room.status != RoomStatus.PLAYING:
                raise GameNotStartedError()

            # 检查用户是否已被淘汰
            if room.is_eliminated(user_id):
                raise PlayerEliminatedError(user_id)

            # 获取用户的词语和角色
            if not room.words:
                raise GameNotStartedError()

            # 判断用户角色
            if user_id in room.undercovers:
                word = room.words.get("undercover", "")
                role = 2  # 卧底
            else:
                word = room.words.get("civilian", "")
                role = 1  # 平民

            return {
                "word": word,
                "role": role
            }

        except (DomainException, ClientException) as e:
            logger.warning(f"用户/业务异常: {e.error_code} - {e.message}", extra={"details": e.details})
            raise

        except RepositoryException as e:
            log_exception(logger, e, {"user_id": user_id})
            raise

        except Exception as e:
            log_exception(logger, e, {"user_id": user_id})
            raise

    def show_status(self, user_id: str) -> tuple[bool, str]:
        """显示状态"""
        try:
            # 获取用户信息
            user = self.user_repo.get(user_id)
            if not user or not user.has_joined_room():
                raise UserNotInRoomError(user_id)

            # 获取房间信息
            room = self.room_repo.get(user.current_room)
            if not room:
                raise RoomNotFoundError(user.current_room)

            # 构建状态信息
            status_lines = []

            # 用户信息
            user_index = -1
            for i, player in enumerate(room.players):
                if player == user_id:
                    user_index = i + 1
                    break

            status_lines.append(f"您的信息：{user.nickname} (序号: {user_index})")
            status_lines.append("")

            # 房间信息
            status_lines.append(f"房间号：{room.room_id}")
            status_lines.append(f"房间状态：{room.status.value}")
            status_lines.append("房间成员：")

            # 玩家列表
            for i, player in enumerate(room.players):
                player_obj = self.user_repo.get(player)
                nickname = player_obj.nickname if player_obj else f"玩家{i + 1}"

                # 添加角色标识
                if player == room.creator:
                    nickname += "(房主)"
                if room.is_eliminated(player):
                    nickname += "(已淘汰)"

                status_lines.append(f"{i + 1}. {nickname}")

            # 游戏信息
            if room.status == RoomStatus.PLAYING:
                status_lines.append("")
                status_lines.append(f"当前轮次：第{room.current_round}轮")
                status_lines.append(f"已淘汰：{len(room.eliminated)}人")

                # 如果是房主，提示投票方式
                if room.is_creator(user_id):
                    status_lines.append("")
                    status_lines.append("您是房主，可通过't+序号'投票淘汰玩家")

            return True, "\n".join(status_lines)

        except (DomainException, ClientException) as e:
            logger.warning(f"用户/业务异常: {e.error_code} - {e.message}", extra={"details": e.details})
            return False, e.message

        except RepositoryException as e:
            log_exception(logger, e, {"user_id": user_id})
            return False, "显示状态失败，请稍后重试"

        except Exception as e:
            log_exception(logger, e, {"user_id": user_id})
            return False, "显示状态时发生错误"

    def _generate_unique_room_code(self) -> str:
        """生成唯一的房间短码（4位数字）"""
        while True:
            room_code = str(random.randint(1000, 9999))
            # 检查roomCode是否已存在
            if not self.room_repo.exists_by_code(room_code):
                return room_code

    def _check_game_end(self, room: Room) -> tuple[bool, str]:
        """检查游戏是否结束"""
        # 检查是否有卧底被淘汰
        eliminated_undercovers = set(room.undercovers) & set(room.eliminated)

        # 如果所有卧底都被淘汰，平民获胜
        if len(eliminated_undercovers) == len(room.undercovers):
            winner_team = "civilian"
            result_message = "游戏结束！平民获胜，成功找出了所有卧底！"
            self._finish_game(room, winner_team=winner_team)
            
            # 发送 WebSocket 通知 - 游戏结束
            if self.notification:
                from backend.websocket.events import GameEvent as WSGameEvent
                self.notification.notify_room(
                    room_id=room.room_id,
                    event=WSGameEvent.ENDED.value,
                    data={
                        "winner_team": winner_team,
                        "hint": result_message
                    }
                )
            
            return True, result_message

        # 检查剩余玩家数量
        remaining_players = room.get_remaining_players()

        # 如果剩余玩家少于3人，游戏结束
        if len(remaining_players) < 3:
            winner_team = "undercover"
            result_message = "游戏结束！卧底获胜！"
            self._finish_game(room, winner_team=winner_team)
            
            # 发送 WebSocket 通知 - 游戏结束
            if self.notification:
                from backend.websocket.events import GameEvent as WSGameEvent
                self.notification.notify_room(
                    room_id=room.room_id,
                    event=WSGameEvent.ENDED.value,
                    data={
                        "winner_team": winner_team,
                        "hint": result_message
                    }
                )
            
            return True, result_message

        # 检查卧底数量是否大于等于平民数量
        remaining_undercovers = [p for p in room.undercovers if p in remaining_players]
        remaining_civilians = [p for p in remaining_players if p not in room.undercovers]

        if len(remaining_undercovers) >= len(remaining_civilians):
            winner_team = "undercover"
            result_message = "游戏结束！卧底获胜！"
            self._finish_game(room, winner_team=winner_team)
            
            # 发送 WebSocket 通知 - 游戏结束
            if self.notification:
                from backend.websocket.events import GameEvent as WSGameEvent
                self.notification.notify_room(
                    room_id=room.room_id,
                    event=WSGameEvent.ENDED.value,
                    data={
                        "winner_team": winner_team,
                        "hint": result_message
                    }
                )
            
            return True, result_message

        return False, ""

    def _finish_game(self, room: Room, winner_team: str) -> None:
        """结束游戏逻辑：更新状态、保存记录、清理房间"""
        # 1. 更新房间状态
        next_state = self.fsm.next_state(GameState.PLAYING, GameEvent.END)
        room.status = RoomStatus(next_state.value)
        self.room_repo.save(room)

        # 2. 保存对局记录到 MySQL
        try:
            creator_sql = SQLUser.query.filter_by(openid=room.creator).first()
            record = GameRecord(
                room_id=room.room_id,
                creator_id=creator_sql.id if creator_sql else None,
                winner_team=winner_team,
                player_count=len(room.players),
                undercover_count=len(room.undercovers),
                civilian_word=room.words.get("civilian"),
                undercover_word=room.words.get("undercover"),
                ended_at=datetime.utcnow(),
            )
            db.session.add(record)

            # 更新参与者的胜率
            # 注意：目前的 User 系统是 Redis+SQL 混合。
            # 这里简单更新一下 MySQL 中的记录（如果有）
            for player_id in room.players:
                p_sql = SQLUser.query.filter_by(openid=player_id).first()
                if p_sql:
                    p_sql.total_games += 1
                    is_winner = (player_id in room.undercovers and winner_team == "undercover") or (
                        player_id not in room.undercovers and winner_team == "civilian"
                    )
                    if is_winner:
                        p_sql.wins += 1

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to save game record: {e}")

        # 3. 让所有玩家自动退出房间
        self._auto_leave_room(room)

    def _auto_leave_room(self, room: Room) -> None:
        """自动让玩家离开房间"""
        for player_id in room.players:
            user = self.user_repo.get(player_id)
            if user and user.current_room == room.room_id:
                user.leave_room()
                self.user_repo.save(user)

    def _push_room_status(self, room: Room) -> None:
        lines = [
            f"房间号：{room.room_id}",
            f"房间状态：{room.status.value}",
            "房间成员：",
        ]
        for i, player in enumerate(room.players):
            u = self.user_repo.get(player)
            n = u.nickname if u else f"玩家{i + 1}"
            if player == room.creator:
                n += "(房主)"
            if room.is_eliminated(player):
                n += "(已淘汰)"
            lines.append(f"{i + 1}. {n}")
        if room.status == RoomStatus.PLAYING:
            lines.append("")
            lines.append(f"当前轮次：第{room.current_round}轮")
            lines.append(f"已淘汰：{len(room.eliminated)}人")
        content = "\n".join(lines)
        for pid in room.players:
            if self.push and self.push.enabled():
                self.push.send_text(pid, content)
