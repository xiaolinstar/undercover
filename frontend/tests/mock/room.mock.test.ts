/**
 * MockRoomService 测试
 */

import { MockRoomService } from '../../miniprogram/mock/room.mock'

describe('MockRoomService 房间 Mock 服务', () => {
  beforeEach(() => {
    // 清空 Mock 数据
    jest.clearAllMocks()
  })
  
  describe('createRoom 方法', () => {
    it('应该创建房间并返回房间信息', async () => {
      const room = await MockRoomService.createRoom()
      
      expect(room).toHaveProperty('roomId')
      expect(room).toHaveProperty('roomCode')
      expect(room.maxPlayers).toBe(12) // 保持默认值
      expect(room.status).toBe('waiting')
      expect(room.players.length).toBe(1)
      expect(room.players[0].isOwner).toBe(true)
    })
    
    it('创建者应该是房主', async () => {
      const room = await MockRoomService.createRoom()
      
      expect(room.players[0].isOwner).toBe(true)
    })
  })
  
  describe('joinRoom 方法', () => {
    it('应该能加入现有房间', async () => {
      // 先创建一个房间
      const createdRoom = await MockRoomService.createRoom()
      
      // 加入房间
      const room = await MockRoomService.joinRoom(createdRoom.roomCode)
      
      expect(room.roomCode).toBe(createdRoom.roomCode)
      expect(room.players.length).toBeGreaterThan(1)
    })
    
    it('房间不存在时应该抛出错误', async () => {
      await expect(MockRoomService.joinRoom('9999')).rejects.toThrow('房间不存在')
    })
    
    it('房间已满时应该抛出错误', async () => {
      const createdRoom = await MockRoomService.createRoom()
      
      await expect(MockRoomService.joinRoom(createdRoom.roomCode)).rejects.toThrow('房间已满')
    })
  })
  
  describe('getRoom 方法', () => {
    it('应该能获取房间信息', async () => {
      const createdRoom = await MockRoomService.createRoom()
      
      const room = await MockRoomService.getRoom(createdRoom.roomId)
      
      expect(room.roomId).toBe(createdRoom.roomId)
    })
    
    it('房间不存在时应该抛出错误', async () => {
      await expect(MockRoomService.getRoom('non_exist_id')).rejects.toThrow('房间不存在')
    })
  })
  
  describe('leaveRoom 方法', () => {
    it('应该能成功离开房间', async () => {
      const createdRoom = await MockRoomService.createRoom()
      
      await expect(MockRoomService.leaveRoom(createdRoom.roomId)).resolves.not.toThrow()
    })
  })
})
