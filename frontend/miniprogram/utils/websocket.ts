/**
 * WebSocket 工具类
 * 提供连接管理、心跳检测、断线重连、消息队列等功能
 */

import { API_CONFIG } from '../config/api.config'
import {
  WSStatus,
  WSEventType,
  WSMessage,
  WSEventListener,
} from '../types/websocket.types'

/**
 * WebSocket 配置
 */
interface WSConfig {
  // WebSocket 地址
  url: string
  // 心跳间隔（毫秒）
  heartbeatInterval: number
  // 重连间隔（毫秒）
  reconnectInterval: number
  // 最大重连次数
  maxReconnectAttempts: number
  // 消息队列最大长度
  maxMessageQueueSize: number
}

/**
 * WebSocket 工具类
 */
export class WebSocketManager {
  private socket: WechatMiniprogram.SocketTask | null
  private config: WSConfig
  private status: WSStatus
  private reconnectAttempts: number
  private heartbeatTimer: NodeJS.Timeout | null
  private reconnectTimer: NodeJS.Timeout | null
  private messageQueue: WSMessage<unknown>[]
  private eventListeners: Map<WSEventType, Set<WSEventListener<unknown>>>
  private authParams: { token?: string; roomId?: string }
  
  constructor(config?: Partial<WSConfig>) {
    this.socket = null
    this.status = WSStatus.DISCONNECTED
    this.reconnectAttempts = 0
    this.heartbeatTimer = null
    this.reconnectTimer = null
    this.messageQueue = []
    this.eventListeners = new Map()
    this.authParams = {}
    this.config = {
      url: (config && config.url) || API_CONFIG.WS_URL,
      heartbeatInterval: (config && config.heartbeatInterval) || 30000, // 30秒
      reconnectInterval: (config && config.reconnectInterval) || 3000, // 3秒
      maxReconnectAttempts: (config && config.maxReconnectAttempts) || 5,
      maxMessageQueueSize: (config && config.maxMessageQueueSize) || 100,
      ...config,
    }
  }
  
  /**
   * 连接 WebSocket
   */
  connect(params?: { token?: string; roomId?: string }): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.status === WSStatus.CONNECTED || this.status === WSStatus.CONNECTING) {
        resolve()
        return
      }
      
      this.setStatus(WSStatus.CONNECTING)
      
      // 保存认证参数，用于连接后发送认证消息
      this.authParams = params || {}
      
      // 构建 WebSocket URL（不包含敏感信息）
      let connectUrl = this.config.url
      
      // 只添加非敏感的roomId参数
      if (params && params.roomId) {
        connectUrl += (connectUrl.includes('?') ? '&' : '?') + `roomId=${params.roomId}`
      }
      
      // 打印调试信息（不暴露Token）
      console.log('[WebSocket] 连接 URL:', connectUrl)
      console.log('[WebSocket] 认证参数:', params ? 'token=' + (params.token ? '***' : 'null') : 'null')
      
      // 创建 WebSocket 连接
      this.socket = wx.connectSocket({
        url: connectUrl,
        success: () => {
          console.log('[WebSocket] 连接中...')
        },
        fail: (error) => {
          console.error('[WebSocket] 连接失败:', error)
          this.setStatus(WSStatus.DISCONNECTED)
          reject(error)
        },
      })
      
      // 监听连接打开
      this.socket.onOpen(() => {
        console.log('[WebSocket] 连接已打开')
        this.setStatus(WSStatus.CONNECTED)
        this.reconnectAttempts = 0
        
        // 连接成功后发送认证消息
        if (this.authParams.token) {
          this.sendAuthMessage()
        }
        
        this.startHeartbeat()
        this.flushMessageQueue()
        resolve()
      })
      
      // 监听消息
      this.socket.onMessage((res) => {
        this.handleMessage(res.data)
      })
      
      // 监听错误
      this.socket.onError((error) => {
        console.error('[WebSocket] 连接错误:', error)
        this.setStatus(WSStatus.DISCONNECTED)
        this.emit(WSEventType.ERROR, error)
      })
      
      // 监听关闭
      this.socket.onClose(() => {
        console.log('[WebSocket] 连接关闭')
        this.handleDisconnect()
      })
    })
  }
  
  /**
   * 发送认证消息
   */
  private sendAuthMessage(): void {
    if (!this.socket || !this.authParams.token) {
      return
    }
    
    // 验证roomId不是"underfind"
    const roomId = this.authParams.roomId === 'underfind' ? '' : this.authParams.roomId || ''
    
    const authMessage = {
      type: 'auth',
      data: {
        token: this.authParams.token,
        roomId: roomId,
      },
      timestamp: Date.now(),
    }
    
    console.log('[WebSocket] 发送认证消息')
    console.log('[WebSocket] 认证数据:', { 
      hasToken: !!this.authParams.token, 
      roomId: roomId || 'null' 
    })
    
    this.socket.send({
      data: JSON.stringify(authMessage),
      success: () => {
        console.log('[WebSocket] 认证消息发送成功')
      },
      fail: (error) => {
        console.error('[WebSocket] 认证消息发送失败:', error)
      },
    })
  }
  
  /**
   * 断开连接
   */
  disconnect(): void {
    this.stopHeartbeat()
    this.stopReconnect()
    
    if (this.socket) {
      this.socket.close({
        success: () => {
          console.log('[WebSocket] 已断开连接')
        },
      })
      this.socket = null
    }
    
    this.setStatus(WSStatus.DISCONNECTED)
  }
  
  /**
   * 发送消息
   */
  send<T = any>(type: WSEventType, data: T): Promise<void> {
    return new Promise((resolve, reject) => {
      const message: WSMessage<T> = {
        type,
        data,
        timestamp: Date.now(),
      }
      
      if (this.status !== WSStatus.CONNECTED || !this.socket) {
        // 加入消息队列
        this.enqueueMessage(message)
        resolve()
        return
      }
      
      this.socket.send({
        data: JSON.stringify(message),
        success: () => {
          resolve()
        },
        fail: (error) => {
          console.error('[WebSocket] 发送消息失败:', error)
          // 发送失败，加入队列
          this.enqueueMessage(message)
          reject(error)
        },
      })
    })
  }
  
  /**
   * 添加事件监听器
   */
  on<T = unknown>(event: WSEventType, listener: WSEventListener<T>): void {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, new Set())
    }
    this.eventListeners.get(event)!.add(listener as WSEventListener<unknown>)
  }
  
  /**
   * 移除事件监听器
   */
  off<T = unknown>(event: WSEventType, listener: WSEventListener<T>): void {
    const listeners = this.eventListeners.get(event)
    if (listeners) {
      listeners.delete(listener as WSEventListener<unknown>)
    }
  }
  
  /**
   * 移除所有事件监听器
   */
  offAll(event?: WSEventType): void {
    if (event) {
      this.eventListeners.delete(event)
    } else {
      this.eventListeners.clear()
    }
  }
  
  /**
   * 获取连接状态
   */
  getStatus(): WSStatus {
    return this.status
  }
  
  /**
   * 是否已连接
   */
  isConnected(): boolean {
    return this.status === WSStatus.CONNECTED
  }
  
  // ============ 私有方法 ============
  
  /**
   * 设置状态
   */
  private setStatus(status: WSStatus): void {
    this.status = status
    this.emit(WSEventType.DISCONNECTED, { status })
  }
  
  /**
   * 处理消息
   */
  private handleMessage(data: string | ArrayBuffer): void {
    try {
      const message: WSMessage<unknown> = JSON.parse(data as string)
      // 检查消息类型是否在WSEventType中
      const eventType = message.type as WSEventType
      if (Object.values(WSEventType).includes(eventType)) {
        this.emit(eventType, message.data)
      } else {
        console.warn('[WebSocket] 未知的消息类型:', message.type)
      }
    } catch (error) {
      console.error('[WebSocket] 解析消息失败:', error)
    }
  }
  
  /**
   * 处理断开连接
   */
  private handleDisconnect(): void {
    this.stopHeartbeat()
    this.setStatus(WSStatus.DISCONNECTED)
    this.emit(WSEventType.DISCONNECTED, {})
    
    // 自动重连
    if (this.reconnectAttempts < this.config.maxReconnectAttempts) {
      this.reconnect()
    }
  }
  
  /**
   * 开始心跳检测
   */
  private startHeartbeat(): void {
    this.stopHeartbeat()
    
    this.heartbeatTimer = setInterval(() => {
      if (this.status === WSStatus.CONNECTED && this.socket) {
        // 发送简单的ping消息，避免使用服务器不认识的pong类型
        const pingMessage = {
          type: 'ping',
          data: {
            timestamp: Date.now(),
          },
          timestamp: Date.now(),
        }
        
        this.socket.send({
          data: JSON.stringify(pingMessage),
          fail: (error) => {
            console.error('[WebSocket] 心跳检测失败:', error)
          },
        })
      }
    }, this.config.heartbeatInterval)
  }
  
  /**
   * 停止心跳检测
   */
  private stopHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer)
      this.heartbeatTimer = null
    }
  }
  
  /**
   * 重连
   */
  private reconnect(): void {
    this.setStatus(WSStatus.RECONNECTING)
    this.emit(WSEventType.RECONNECTING, {
      attempt: this.reconnectAttempts + 1,
      maxAttempts: this.config.maxReconnectAttempts,
    })
    
    this.stopReconnect()
    
    this.reconnectTimer = setTimeout(() => {
      this.reconnectAttempts++
      console.log(`[WebSocket] 第 ${this.reconnectAttempts} 次重连...`)
      
      this.connect().catch((error) => {
        console.error('[WebSocket] 重连失败:', error)
      })
    }, this.config.reconnectInterval)
  }
  
  /**
   * 停止重连
   */
  private stopReconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
  }
  
  /**
   * 消息入队
   */
  private enqueueMessage(message: WSMessage<unknown>): void {
    if (this.messageQueue.length >= this.config.maxMessageQueueSize) {
      this.messageQueue.shift()
    }
    this.messageQueue.push(message)
  }
  
  /**
   * 刷新消息队列
   */
  private flushMessageQueue(): void {
    while (this.messageQueue.length > 0) {
      const message = this.messageQueue.shift()
      if (message && this.socket) {
        this.socket.send({
          data: JSON.stringify(message),
          fail: (error) => {
            console.error('[WebSocket] 发送队列消息失败:', error)
          },
        })
      }
    }
  }
  
  /**
   * 触发事件
   */
  private emit<T = any>(event: WSEventType, data: T): void {
    const listeners = this.eventListeners.get(event)
    if (listeners) {
      listeners.forEach((listener) => {
        try {
          listener(data)
        } catch (error) {
          console.error('[WebSocket] 事件监听器执行错误:', error)
        }
      })
    }
  }
}

// 导出单例
export const wsManager = new WebSocketManager()
