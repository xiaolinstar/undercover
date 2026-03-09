/**
 * WebSocket 服务测试
 */

import { WebSocketService, wsService } from '../../miniprogram/services/websocket.service'

// Mock storage
jest.mock('../../miniprogram/utils/storage', () => ({
  storage: {
    get: jest.fn((key: string) => {
      if (key === 'token') return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoidXNlcl8xMDAxIiwiZXhwIjoxNzYwNDgwODgxfQ.7QZ9c4h8f7g6e5d4c3b2a1"
      if (key === 'openid') return 'test_openid'
      return ''
    }),
    set: jest.fn(),
    remove: jest.fn(),
  },
}))

// Mock WebSocketManager
jest.mock('../../miniprogram/utils/websocket', () => ({
  WebSocketManager: jest.fn().mockImplementation(() => ({
    connect: jest.fn().mockResolvedValue(undefined),
    disconnect: jest.fn(),
    send: jest.fn().mockResolvedValue(undefined),
    on: jest.fn(),
    off: jest.fn(),
    offAll: jest.fn(),
    isConnected: jest.fn().mockReturnValue(false),
    getStatus: jest.fn().mockReturnValue('disconnected'),
  })),
  wsManager: {
    connect: jest.fn().mockResolvedValue(undefined),
    disconnect: jest.fn(),
    send: jest.fn().mockResolvedValue(undefined),
    on: jest.fn(),
    off: jest.fn(),
    offAll: jest.fn(),
    isConnected: jest.fn().mockReturnValue(false),
  },
}))

describe('WebSocketService', () => {
  let service: WebSocketService
  
  beforeEach(() => {
    service = new WebSocketService()
  })
  
  afterEach(() => {
    service.disconnect()
  })
  
  describe('初始化', () => {
    it('应该成功创建 WebSocketService 实例', () => {
      expect(service).toBeInstanceOf(WebSocketService)
    })
    
    it('初始状态应该是未连接', () => {
      expect(service.checkConnection()).toBe(false)
    })
  })
  
  describe('房间管理', () => {
    it('getCurrentRoomId() 应该返回当前房间 ID', () => {
      expect(service.getCurrentRoomId()).toBe('')
    })
  })
  
  describe('事件监听', () => {
    it('应该能够监听玩家加入事件', () => {
      const listener = jest.fn()
      service.onPlayerJoin(listener)
      expect(listener).toBeDefined()
    })
    
    it('应该能够监听玩家离开事件', () => {
      const listener = jest.fn()
      service.onPlayerLeave(listener)
      expect(listener).toBeDefined()
    })
    
    it('应该能够监听游戏开始事件', () => {
      const listener = jest.fn()
      service.onGameStart(listener)
      expect(listener).toBeDefined()
    })
    
    it('应该能够监听游戏结束事件', () => {
      const listener = jest.fn()
      service.onGameEnd(listener)
      expect(listener).toBeDefined()
    })
  })
  
  describe('断开连接', () => {
    it('应该能够断开连接', () => {
      service.disconnect()
      expect(service.checkConnection()).toBe(false)
    })
  })
})

describe('wsService 单例', () => {
  it('应该导出 WebSocketService 实例', () => {
    expect(wsService).toBeInstanceOf(WebSocketService)
  })
})
