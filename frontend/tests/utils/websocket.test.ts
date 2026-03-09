/**
 * WebSocket 工具类测试
 */

import { WebSocketManager } from '../../miniprogram/utils/websocket'
import { WSStatus, WSEventType } from '../../miniprogram/types/websocket.types'
import { mockWx } from '../setup'

describe('WebSocketManager', () => {
  let ws: WebSocketManager
  let mockSocket: any
  
  beforeEach(() => {
    // 重置 mock
    jest.clearAllMocks()
    
    // 创建模拟 socket
    mockSocket = {
      onOpen: jest.fn((callback) => { mockSocket._onOpenCallback = callback }),
      onClose: jest.fn((callback) => { mockSocket._onCloseCallback = callback }),
      onError: jest.fn((callback) => { mockSocket._onErrorCallback = callback }),
      onMessage: jest.fn((callback) => { mockSocket._onMessageCallback = callback }),
      send: jest.fn((options) => {
        if (options.success) options.success()
      }),
      close: jest.fn((options) => {
        if (options && options.success) options.success()
      }),
    }
    
    // 设置 wx.connectSocket 返回模拟 socket
    ;(mockWx.connectSocket as jest.Mock).mockImplementation((options) => {
      if (options && options.success) {
        setTimeout(() => options.success(), 0)
      }
      return mockSocket
    })
    
    ws = new WebSocketManager({
      url: 'wss://test.com/ws',
      heartbeatInterval: 5000,
      reconnectInterval: 1000,
      maxReconnectAttempts: 3,
    })
  })
  
  afterEach(() => {
    ws.disconnect()
    jest.useRealTimers()
  })
  
  describe('连接管理', () => {
    it('应该成功创建 WebSocket 实例', () => {
      expect(ws).toBeInstanceOf(WebSocketManager)
    })
    
    it('初始状态应该是 DISCONNECTED', () => {
      expect(ws.getStatus()).toBe(WSStatus.DISCONNECTED)
    })
    
    it('isConnected() 应该返回 false（未连接）', () => {
      expect(ws.isConnected()).toBe(false)
    })
    
    it('应该成功连接 WebSocket', async () => {
      const connectPromise = ws.connect()
      
      // 模拟连接成功
      mockSocket._onOpenCallback()
      
      await connectPromise
      
      expect(ws.getStatus()).toBe(WSStatus.CONNECTED)
      expect(ws.isConnected()).toBe(true)
    })
    
    it('带参数连接应该构建正确的 URL', async () => {
      const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoidXNlcl8xMDAxIiwiZXhwIjoxNzYwNDgwODgxfQ.7QZ9c4h8f7g6e5d4c3b2a1"
      const connectPromise = ws.connect({ token: token, roomId: 'room_001' })
      
      mockSocket._onOpenCallback()
      
      await connectPromise
      
      expect(mockWx.connectSocket).toHaveBeenCalledWith(
        expect.objectContaining({
          url: `wss://test.com/ws?token=${token}&roomId=room_001`,
        })
      )
    })
    
    it('连接失败应该设置状态为 DISCONNECTED', async () => {
      ;(mockWx.connectSocket as jest.Mock).mockImplementation((options) => {
        if (options && options.fail) {
          setTimeout(() => options.fail({ errMsg: 'Connection failed' }), 0)
        }
        return mockSocket
      })
      
      await expect(ws.connect()).rejects.toEqual({ errMsg: 'Connection failed' })
      expect(ws.getStatus()).toBe(WSStatus.DISCONNECTED)
    })
    
    it('重复连接应该直接返回', async () => {
      // 第一次连接
      const connectPromise1 = ws.connect()
      mockSocket._onOpenCallback()
      await connectPromise1
      
      // 第二次连接应该直接返回
      await ws.connect()
      
      expect(mockWx.connectSocket).toHaveBeenCalledTimes(1)
    })
  })
  
  describe('事件监听', () => {
    it('应该能够添加事件监听器', () => {
      const listener = jest.fn()
      ws.on(WSEventType.CONNECTED, listener)
      
      // 触发事件
      ;(ws as any).emit(WSEventType.CONNECTED, { status: WSStatus.CONNECTED })
      
      expect(listener).toHaveBeenCalled()
    })
    
    it('应该能够移除事件监听器', () => {
      const listener = jest.fn()
      ws.on(WSEventType.CONNECTED, listener)
      ws.off(WSEventType.CONNECTED, listener)
      
      ;(ws as any).emit(WSEventType.CONNECTED, { status: WSStatus.CONNECTED })
      
      expect(listener).not.toHaveBeenCalled()
    })
    
    it('应该能够移除所有事件监听器', () => {
      const listener1 = jest.fn()
      const listener2 = jest.fn()
      
      ws.on(WSEventType.CONNECTED, listener1)
      ws.on(WSEventType.DISCONNECTED, listener2)
      
      ws.offAll()
      
      ;(ws as any).emit(WSEventType.CONNECTED, {})
      ;(ws as any).emit(WSEventType.DISCONNECTED, {})
      
      expect(listener1).not.toHaveBeenCalled()
      expect(listener2).not.toHaveBeenCalled()
    })
    
    it('应该能够移除特定事件的所有监听器', () => {
      const listener1 = jest.fn()
      const listener2 = jest.fn()
      
      ws.on(WSEventType.CONNECTED, listener1)
      ws.on(WSEventType.DISCONNECTED, listener2)
      
      ws.offAll(WSEventType.CONNECTED)
      
      ;(ws as any).emit(WSEventType.CONNECTED, {})
      ;(ws as any).emit(WSEventType.DISCONNECTED, {})
      
      expect(listener1).not.toHaveBeenCalled()
      expect(listener2).toHaveBeenCalled()
    })
    
    it('事件监听器执行错误应该被捕获', () => {
      const errorListener = jest.fn(() => {
        throw new Error('Listener error')
      })
      
      ws.on(WSEventType.CONNECTED, errorListener)
      
      // 不应该抛出错误
      expect(() => {
        ;(ws as any).emit(WSEventType.CONNECTED, {})
      }).not.toThrow()
    })
  })
  
  describe('消息发送', () => {
    it('未连接时发送消息应该加入队列', async () => {
      await ws.send(WSEventType.PLAYER_MESSAGE, { message: 'test' })
      
      // 消息应该被加入队列，发送操作不抛出错误
      expect(mockSocket.send).not.toHaveBeenCalled()
    })
    
    it('连接状态下发送消息应该成功', async () => {
      // 先连接
      const connectPromise = ws.connect()
      mockSocket._onOpenCallback()
      await connectPromise
      
      // 发送消息
      await ws.send(WSEventType.PLAYER_MESSAGE, { message: 'test' })
      
      expect(mockSocket.send).toHaveBeenCalled()
    })
    
    it('发送失败应该将消息加入队列', async () => {
      // 模拟发送失败
      mockSocket.send = jest.fn((options) => {
        if (options.fail) {
          options.fail({ errMsg: 'Send failed' })
        }
      })
      
      // 先连接
      const connectPromise = ws.connect()
      mockSocket._onOpenCallback()
      await connectPromise
      
      // 发送消息应该失败
      await expect(ws.send(WSEventType.PLAYER_MESSAGE, { message: 'test' }))
        .rejects.toEqual({ errMsg: 'Send failed' })
    })
  })
  
  describe('消息接收', () => {
    it('应该正确解析并触发消息事件', async () => {
      const listener = jest.fn()
      ws.on(WSEventType.PLAYER_MESSAGE, listener)
      
      // 连接
      const connectPromise = ws.connect()
      mockSocket._onOpenCallback()
      await connectPromise
      
      // 模拟接收消息
      const message = JSON.stringify({
        type: WSEventType.PLAYER_MESSAGE,
        data: { message: 'hello' },
        timestamp: Date.now(),
      })
      mockSocket._onMessageCallback({ data: message })
      
      expect(listener).toHaveBeenCalledWith({ message: 'hello' })
    })
    
    it('解析无效消息应该捕获错误', async () => {
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation()
      
      // 连接
      const connectPromise = ws.connect()
      mockSocket._onOpenCallback()
      await connectPromise
      
      // 模拟接收无效消息
      mockSocket._onMessageCallback({ data: 'invalid json' })
      
      expect(consoleSpy).toHaveBeenCalled()
      consoleSpy.mockRestore()
    })
  })
  
  describe('断开连接', () => {
    it('应该能够断开连接', () => {
      ws.disconnect()
      expect(ws.getStatus()).toBe(WSStatus.DISCONNECTED)
    })
    
    it('断开连接后 isConnected() 应该返回 false', () => {
      ws.disconnect()
      expect(ws.isConnected()).toBe(false)
    })
    
    it('连接状态下断开连接应该关闭 socket', async () => {
      const connectPromise = ws.connect()
      mockSocket._onOpenCallback()
      await connectPromise
      
      ws.disconnect()
      
      expect(mockSocket.close).toHaveBeenCalled()
      expect(ws.getStatus()).toBe(WSStatus.DISCONNECTED)
    })
    
    it('连接关闭时应该触发断开连接处理', async () => {
      jest.useFakeTimers()
      
      const disconnectListener = jest.fn()
      ws.on(WSEventType.DISCONNECTED, disconnectListener)
      
      // 连接
      const connectPromise = ws.connect()
      mockSocket._onOpenCallback()
      await connectPromise
      
      // 模拟连接关闭
      mockSocket._onCloseCallback()
      
      expect(disconnectListener).toHaveBeenCalled()
    })
    
    it('连接错误时应该触发 ERROR 事件', async () => {
      const errorListener = jest.fn()
      ws.on(WSEventType.ERROR, errorListener)
      
      // 连接
      const connectPromise = ws.connect()
      mockSocket._onOpenCallback()
      await connectPromise
      
      // 模拟错误
      mockSocket._onErrorCallback({ errMsg: 'Connection error' })
      
      expect(errorListener).toHaveBeenCalled()
    })
  })
  
  describe('断线重连', () => {
    it('连接关闭时应该触发重连', async () => {
      jest.useFakeTimers()
      
      const reconnectListener = jest.fn()
      ws.on(WSEventType.RECONNECTING, reconnectListener)
      
      // 连接
      const connectPromise = ws.connect()
      mockSocket._onOpenCallback()
      await connectPromise
      
      // 模拟连接关闭
      mockSocket._onCloseCallback()
      
      // 触发重连定时器
      jest.advanceTimersByTime(1000)
      
      expect(reconnectListener).toHaveBeenCalled()
    })
  })
  
  describe('消息队列', () => {
    it('消息队列超过最大长度时应该移除最早的消息', async () => {
      const smallQueueWs = new WebSocketManager({
        url: 'wss://test.com/ws',
        maxMessageQueueSize: 2,
      })
      
      // 发送多条消息（未连接）
      await smallQueueWs.send(WSEventType.PLAYER_MESSAGE, { message: 'msg1' })
      await smallQueueWs.send(WSEventType.PLAYER_MESSAGE, { message: 'msg2' })
      await smallQueueWs.send(WSEventType.PLAYER_MESSAGE, { message: 'msg3' })
      
      // 连接后应该只发送后两条消息
      const connectPromise = smallQueueWs.connect()
      mockSocket._onOpenCallback()
      await connectPromise
      
      // 第一条消息应该被移除
      expect(mockSocket.send).toHaveBeenCalledTimes(2)
      
      smallQueueWs.disconnect()
    })
    
    it('连接成功后应该发送队列中的消息', async () => {
      // 先发送消息（未连接）
      await ws.send(WSEventType.PLAYER_MESSAGE, { message: 'queued_msg' })
      
      // 连接
      const connectPromise = ws.connect()
      mockSocket._onOpenCallback()
      await connectPromise
      
      // 队列消息应该被发送
      expect(mockSocket.send).toHaveBeenCalled()
    })
  })
})
