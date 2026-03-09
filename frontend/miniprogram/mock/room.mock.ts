/**
 * Mock 房间服务
 */

import { MOCK_ROOMS, MOCK_USER, generateUUID, generateRoomCode } from './data'

export class MockRoomService {
  /**
   * Mock 创建房间
   */
  static async createRoom(): Promise<any> {
    await this.delay(500)
    
    const roomId = generateUUID()
    const roomCode = generateRoomCode()
    
    const room = {
      roomId,
      roomCode,
      ownerId: MOCK_USER.userId,
      players: [
        {
          playerId: MOCK_USER.userId,
          playerNumber: 1,
          nickname: MOCK_USER.nickname,
          avatar: MOCK_USER.avatar,
          isOwner: true,
          isAlive: true,
        },
      ],
      maxPlayers: 12, // 保持默认值，但不限制
      status: 'waiting',
      createdAt: new Date().toISOString(),
    }
    
    // 保存到 Mock 数据
    MOCK_ROOMS[roomCode] = room
    
    return room
  }

  /**
   * Mock 加入房间
   */
  static async joinRoom(roomCode: string): Promise<any> {
    await this.delay(500)
    
    const room = MOCK_ROOMS[roomCode]
    
    if (!room) {
      throw new Error('房间不存在')
    }
    
    if (room.players.length >= room.maxPlayers) {
      throw new Error('房间已满')
    }
    
    if (room.status !== 'waiting') {
      throw new Error('游戏已开始')
    }
    
    // 添加新玩家
    const newPlayer = {
      playerId: generateUUID(),
      playerNumber: room.players.length + 1,
      nickname: `玩家${room.players.length + 1}`,
      avatar: MOCK_USER.avatar,
      isOwner: false,
      isAlive: true,
    }
    
    room.players.push(newPlayer)
    
    return room
  }

  /**
   * Mock 获取房间信息
   */
  static async getRoom(roomId: string): Promise<any> {
    await this.delay(300)
    
    // 查找房间
    for (const roomCode in MOCK_ROOMS) {
      if (MOCK_ROOMS[roomCode].roomId === roomId) {
        return MOCK_ROOMS[roomCode]
      }
    }
    
    throw new Error('房间不存在')
  }

  /**
   * Mock 离开房间
   */
  static async leaveRoom(_roomId: string): Promise<void> {
    await this.delay(300)
    
    // 模拟离开成功
  }

  /**
   * 延迟函数
   */
  private static delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms))
  }
}
