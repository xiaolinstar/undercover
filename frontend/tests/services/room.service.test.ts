/**
 * RoomService 房间服务测试
 */

import { RoomService } from '../../miniprogram/services/room.service'
import { request } from '../../miniprogram/utils/request'

// Mock 依赖
jest.mock('../../miniprogram/utils/request')
jest.mock('../../miniprogram/services/websocket.service', () => ({
  wsService: {
    joinRoom: jest.fn().mockResolvedValue(undefined),
    leaveRoom: jest.fn().mockResolvedValue(undefined),
  },
}))
jest.mock('../../miniprogram/config/api.config', () => ({
  API_CONFIG: {
    USE_MOCK: false,
    BASE_URL: 'https://test.com/api',
    TIMEOUT: 10000,
  },
  API_ENDPOINTS: {
    CREATE_ROOM: '/room/create',
    JOIN_ROOM: '/room/join',
    GET_ROOM: '/room/:roomId',
    LEAVE_ROOM: '/room/leave',
  },
}))

describe('RoomService 房间服务', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })
  
  describe('createRoom 方法', () => {
    it('应该调用创建房间 API', async () => {
      const mockRoom = {
        room_id: 'room_001',
        room_code: '1234',
        max_players: 12,
        owner_id: 'user_001',
        players: [],
        status: 'waiting',
        created_at: '2024-01-01',
      }
      ;(request.post as jest.Mock).mockResolvedValue(mockRoom)
      
      const result = await RoomService.createRoom()
      
      expect(request.post).toHaveBeenCalledWith('/room/create', {})
      expect(result.roomId).toBe('room_001')
      expect(result.roomCode).toBe('1234')
    })
    
    it('默认最大玩家数为 12', async () => {
      const mockRoom = {
        room_id: 'room_001',
        room_code: '1234',
        max_players: 12,
      }
      ;(request.post as jest.Mock).mockResolvedValue(mockRoom)
      
      await RoomService.createRoom()
      
      expect(request.post).toHaveBeenCalledWith('/room/create', { max_players: 12 })
    })
  })
  
  describe('joinRoom 方法', () => {
    it('应该调用加入房间 API', async () => {
      const mockRoom = {
        room_id: 'room_001',
        room_code: '1234',
        owner_id: 'user_001',
        players: [],
        status: 'waiting',
      }
      ;(request.post as jest.Mock).mockResolvedValue(mockRoom)
      
      const result = await RoomService.joinRoom('1234')
      
      expect(request.post).toHaveBeenCalledWith('/room/join', { room_code: '1234' })
      expect(result.roomId).toBe('room_001')
      expect(result.roomCode).toBe('1234')
    })
  })
  
  describe('getRoom 方法', () => {
    it('应该调用获取房间 API', async () => {
      const mockRoom = {
        room_id: 'room_001',
        room_code: '1234',
        owner_id: 'user_001',
        players: [],
        status: 'waiting',
        max_players: 12,
      }
      ;(request.get as jest.Mock).mockResolvedValue(mockRoom)
      
      const result = await RoomService.getRoom('room_001')
      
      expect(request.get).toHaveBeenCalledWith('/room/room_001')
      expect(result.roomId).toBe('room_001')
      expect(result.roomCode).toBe('1234')
    })
  })
  
  describe('leaveRoom 方法', () => {
    it('应该调用离开房间 API', async () => {
      ;(request.post as jest.Mock).mockResolvedValue(undefined)
      
      await RoomService.leaveRoom('room_001')
      
      expect(request.post).toHaveBeenCalledWith('/room/leave', { room_id: 'room_001' })
    })
  })
})
