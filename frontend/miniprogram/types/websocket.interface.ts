/**
 * WebSocket 服务接口定义
 */

import type {
  PlayerJoinData,
  PlayerLeaveData,
  RoomUpdateData,
  GameStartData,
  GamePhaseChangeData,
  PlayerVoteData,
  GameEndData,
  PlayerMessageData,
  SystemMessageData,
  WSEventListener,
} from './websocket.types'

/**
 * WebSocket 服务接口
 */
export interface IWebSocketService {
  /**
   * 初始化 WebSocket 连接
   */
  connect(): Promise<void>

  /**
   * 断开连接
   */
  disconnect(): void

  /**
   * 加入房间
   */
  joinRoom(roomId: string): Promise<void>

  /**
   * 离开房间
   */
  leaveRoom(): Promise<void>

  /**
   * 监听玩家加入
   */
  onPlayerJoin(listener: WSEventListener<PlayerJoinData>): void

  /**
   * 监听玩家离开
   */
  onPlayerLeave(listener: WSEventListener<PlayerLeaveData>): void

  /**
   * 监听房间更新
   */
  onRoomUpdate(listener: WSEventListener<RoomUpdateData>): void

  /**
   * 监听游戏开始
   */
  onGameStart(listener: WSEventListener<GameStartData>): void

  /**
   * 监听游戏阶段变化
   */
  onGamePhaseChange(listener: WSEventListener<GamePhaseChangeData>): void

  /**
   * 监听玩家投票
   */
  onPlayerVote(listener: WSEventListener<PlayerVoteData>): void

  /**
   * 监听游戏结束
   */
  onGameEnd(listener: WSEventListener<GameEndData>): void

  /**
   * 监听玩家消息
   */
  onPlayerMessage(listener: WSEventListener<PlayerMessageData>): void

  /**
   * 监听系统消息
   */
  onSystemMessage(listener: WSEventListener<SystemMessageData>): void

  /**
   * 发送玩家消息
   */
  sendPlayerMessage(message: string): Promise<void>

  /**
   * 投票
   */
  vote(targetPlayerId: string): Promise<void>

  /**
   * 获取当前房间 ID
   */
  getCurrentRoomId(): string

  /**
   * 检查是否已连接
   */
  checkConnection(): boolean
}
