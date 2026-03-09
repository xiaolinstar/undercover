/**
 * WebSocket 服务
 * 实现 IWebSocketService 接口
 */

import { wsManager } from '../utils/websocket'
import { WSEventType } from '../types/websocket.types'
import { storage, STORAGE_KEYS } from '../utils/storage'
import type { IWebSocketService } from '../types/websocket.interface'
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
} from '../types/websocket.types'

// ============ WebSocket 服务实现 ============

/**
 * WebSocket 服务类
 * 实现 IWebSocketService 接口
 */
export class WebSocketService implements IWebSocketService {
  private currentRoomId: string = ''

  /**
   * 检查是否已连接（使用底层管理器的状态）
   */
  private get isConnected(): boolean {
    return wsManager.isConnected()
  }

  /**
   * 初始化 WebSocket 连接
   */
  async connect(): Promise<void> {
    // 使用底层管理器的状态检查
    if (wsManager.isConnected()) {
      console.log('[WebSocketService] 已连接，跳过')
      return
    }

    const token = storage.get<string>(STORAGE_KEYS.TOKEN)
    console.log('[WebSocketService] Token:', token ? '***' : '未找到')

    if (!token) {
      console.warn('[WebSocketService] 未找到 token，跳过 WebSocket 连接')
      return
    }

    try {
      console.log('[WebSocketService] 正在连接, roomId:', this.currentRoomId)
      
      // 注册全局事件处理（在连接前注册，避免错过认证响应）
      this.registerGlobalHandlers()
      
      await wsManager.connect({
        token: token,
        roomId: this.currentRoomId,
      })

      console.log('[WebSocketService] 连接成功')
    } catch (error) {
      console.error('[WebSocketService] 连接失败:', error)
      throw error
    }
  }

  /**
   * 断开连接
   */
  disconnect(): void {
    try {
      wsManager.disconnect()
    } catch (error) {
      console.warn('[WebSocketService] 断开连接失败:', error)
    }
    this.currentRoomId = ''
  }

  /**
   * 加入房间
   */
  async joinRoom(roomId: string): Promise<void> {
    if (!roomId) {
      console.warn('[WebSocketService] roomId 为空，跳过 WebSocket 加入')
      return
    }
    
    // 验证roomId不是"underfind"
    if (roomId === 'underfind') {
      console.warn('[WebSocketService] roomId 为 underfind，跳过 WebSocket 加入')
      return
    }

    this.currentRoomId = roomId

    if (!this.isConnected) {
      await this.connect()
    }
  }

  /**
   * 离开房间
   */
  async leaveRoom(): Promise<void> {
    if (!this.currentRoomId) {
      return
    }

    if (this.isConnected) {
      try {
        await wsManager.send(WSEventType.PLAYER_LEFT, {
          roomId: this.currentRoomId,
        })
      } catch (error) {
        console.warn('[WebSocketService] 发送离开消息失败:', error)
      }
    }

    this.currentRoomId = ''
  }

  // ============ 事件监听方法 ============

  /**
   * 监听玩家加入
   */
  onPlayerJoin(listener: WSEventListener<PlayerJoinData>): void {
    wsManager.on(WSEventType.PLAYER_JOINED, listener)
  }

  /**
   * 监听玩家离开
   */
  onPlayerLeave(listener: WSEventListener<PlayerLeaveData>): void {
    wsManager.on(WSEventType.PLAYER_LEFT, listener)
  }

  /**
   * 监听房间更新
   */
  onRoomUpdate(listener: WSEventListener<RoomUpdateData>): void {
    wsManager.on(WSEventType.ROOM_UPDATE, listener)
  }

  /**
   * 监听游戏开始
   */
  onGameStart(listener: WSEventListener<GameStartData>): void {
    wsManager.on(WSEventType.GAME_STARTED, listener)
  }

  /**
   * 监听游戏阶段变化
   */
  onGamePhaseChange(listener: WSEventListener<GamePhaseChangeData>): void {
    wsManager.on(WSEventType.GAME_PHASE_CHANGED, listener)
  }

  /**
   * 监听玩家投票
   */
  onPlayerVote(listener: WSEventListener<PlayerVoteData>): void {
    wsManager.on(WSEventType.VOTE_SUBMITTED, listener)
  }

  /**
   * 监听游戏结束
   */
  onGameEnd(listener: WSEventListener<GameEndData>): void {
    wsManager.on(WSEventType.GAME_ENDED, listener)
  }

  /**
   * 监听玩家消息
   */
  onPlayerMessage(listener: WSEventListener<PlayerMessageData>): void {
    wsManager.on(WSEventType.PLAYER_MESSAGE, listener)
  }

  /**
   * 监听系统消息
   */
  onSystemMessage(listener: WSEventListener<SystemMessageData>): void {
    wsManager.on(WSEventType.SYSTEM_MESSAGE, listener)
  }

  // ============ 消息发送方法 ============

  /**
   * 发送玩家消息
   */
  async sendPlayerMessage(message: string): Promise<void> {
    if (!this.currentRoomId) {
      throw new Error('未加入房间')
    }

    if (!this.isConnected) {
      throw new Error('WebSocket 未连接')
    }

    await wsManager.send(WSEventType.PLAYER_MESSAGE, {
      roomId: this.currentRoomId,
      message: message,
      timestamp: Date.now(),
    })
  }

  /**
   * 投票
   */
  async vote(targetPlayerId: string): Promise<void> {
    if (!this.currentRoomId) {
      throw new Error('未加入房间')
    }

    if (!this.isConnected) {
      throw new Error('WebSocket 未连接')
    }

    await wsManager.send(WSEventType.VOTE_SUBMITTED, {
      roomId: this.currentRoomId,
      targetId: targetPlayerId,
    })
  }

  // ============ 状态查询方法 ============

  /**
   * 获取当前房间 ID
   */
  getCurrentRoomId(): string {
    return this.currentRoomId
  }

  /**
   * 检查是否已连接
   */
  checkConnection(): boolean {
    return wsManager.isConnected()
  }

  // ============ 私有方法 ============

  /**
   * 注册全局事件处理器
   */
  private registerGlobalHandlers(): void {
    // 错误处理
    wsManager.on(WSEventType.ERROR, function(error: unknown) {
      console.error('[WebSocketService] 连接错误:', error)
    })

    // 断线重连提示
    wsManager.on(WSEventType.RECONNECTING, function(data: unknown) {
      console.log('[WebSocketService] 正在重连:', data)
    })

    // 重连成功提示
    wsManager.on(WSEventType.CONNECTED, function() {
      console.log('[WebSocketService] 连接成功')
    })

    // 订阅成功
    wsManager.on(WSEventType.SUBSCRIBED, function(data: unknown) {
      console.log('[WebSocketService] 订阅成功:', data)
    })

    // 订阅失败
    wsManager.on(WSEventType.SUBSCRIBE_ERROR, function(data: unknown) {
      console.error('[WebSocketService] 订阅失败:', data)
    })

    // 心跳响应
    wsManager.on(WSEventType.PONG, function(data: unknown) {
      console.log('[WebSocketService] 心跳响应:', data)
    })

    // 服务器关闭
    wsManager.on(WSEventType.SERVER_SHUTDOWN, function(data: unknown) {
      console.warn('[WebSocketService] 服务器关闭:', data)
      // 显示服务器关闭提示
      wx.showToast({
        title: '服务器正在维护，请稍后再试',
        icon: 'none',
        duration: 3000
      })
      // 断开连接
      wsManager.disconnect()
    })

    // 系统消息
    wsManager.on(WSEventType.SYSTEM, function(data: unknown) {
      console.log('[WebSocketService] 系统消息:', data)
      // 显示系统消息提示
      if (typeof data === 'object' && data !== null && 'message' in data) {
        wx.showToast({
          title: String(data.message),
          icon: 'none',
          duration: 3000
        })
      }
    })
  }
}

// 导出单例
export const wsService = new WebSocketService()
