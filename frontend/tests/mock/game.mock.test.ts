/**
 * MockGameService 测试
 */

import { MockGameService } from '../../miniprogram/mock/game.mock'

describe('MockGameService 游戏 Mock 服务', () => {
  describe('startGame 方法', () => {
    it('应该开始游戏并返回游戏状态', async () => {
      const roomId = 'test_room_001'
      
      const game = await MockGameService.startGame(roomId)
      
      expect(game).toHaveProperty('roomId')
      expect(game).toHaveProperty('status', 'describing')
      expect(game).toHaveProperty('currentRound', 1)
      expect(game).toHaveProperty('word')
      expect(game).toHaveProperty('role')
      expect(game).toHaveProperty('players')
    })
    
    it('应该分配词语和角色给玩家', async () => {
      const game = await MockGameService.startGame('test_room')
      
      expect(game.word).toBeTruthy()
      expect(['civilian', 'spy']).toContain(game.role)
      expect(game.players.length).toBeGreaterThan(0)
    })
    
    it('应该有卧底玩家', async () => {
      const game = await MockGameService.startGame('test_room')
      
      const spies = game.players.filter((p: any) => p.role === 'spy')
      expect(spies.length).toBeGreaterThan(0)
    })
  })
  
  describe('getGameStatus 方法', () => {
    it('应该返回游戏状态', async () => {
      const roomId = 'test_room_002'
      
      const game = await MockGameService.getGameStatus(roomId)
      
      expect(game).toHaveProperty('roomId')
      expect(game).toHaveProperty('status')
      expect(game).toHaveProperty('players')
    })
  })
  
  describe('vote 方法', () => {
    it('应该能投票并淘汰玩家', async () => {
      const roomId = 'test_room_003'
      await MockGameService.startGame(roomId)
      
      const targetPlayer = 2
      const result = await MockGameService.vote(roomId, targetPlayer)
      
      expect(result.eliminated).toBe(targetPlayer)
      expect(result).toHaveProperty('isSpy')
    })
    
    it('所有卧底被淘汰时平民胜利', async () => {
      const roomId = 'test_room_004'
      await MockGameService.startGame(roomId)
      
      // 获取卧底玩家序号
      const game = await MockGameService.getGameStatus(roomId)
      const spyPlayer = game.players.find((p: any) => p.role === 'spy')
      
      // 投票淘汰卧底
      const result = await MockGameService.vote(roomId, spyPlayer.playerNumber)
      
      expect(result.gameEnded).toBe(true)
      expect(result.winner).toBe('civilian')
    })
    
    it('玩家不存在时应该抛出错误', async () => {
      const roomId = 'test_room_005'
      await MockGameService.startGame(roomId)
      
      await expect(MockGameService.vote(roomId, 999)).rejects.toThrow('玩家不存在')
    })
  })
})
