/**
 * GameService 游戏服务测试
 */

import { GameService } from '../../miniprogram/services/game.service'
import { request } from '../../miniprogram/utils/request'

// Mock 依赖
jest.mock('../../miniprogram/utils/request')
jest.mock('../../miniprogram/services/websocket.service', () => ({
  wsService: {
    vote: jest.fn().mockResolvedValue(undefined),
  },
}))
jest.mock('../../miniprogram/config/api.config', () => ({
  API_CONFIG: {
    USE_MOCK: false,
    BASE_URL: 'https://test.com/api',
    TIMEOUT: 10000,
  },
  API_ENDPOINTS: {
    START_GAME: '/game/start',
    GET_STATUS: '/game/status',
    VOTE: '/game/vote',
  },
}))

describe('GameService 游戏服务', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })
  
  describe('startGame 方法', () => {
    it('应该调用开始游戏 API', async () => {
      const mockGame = {
        gameId: 'game_001',
        roomId: 'room_001',
        word: '测试词',
        role: 'civilian',
        players: [],
      }
      ;(request.post as jest.Mock).mockResolvedValue(mockGame)
      
      const result = await GameService.startGame('room_001')
      
      expect(request.post).toHaveBeenCalledWith('/game/start', { room_id: 'room_001' })
      expect(result.gameId).toBe('game_001')
      expect(result.roomId).toBe('room_001')
      expect(result.phase).toBe('describing')
      expect(result.currentRound).toBe(1)
    })
  })
  
  describe('getGameStatus 方法', () => {
    it('应该调用获取游戏状态 API', async () => {
      const mockGame = {
        gameId: 'game_001',
        roomId: 'room_001',
        phase: 'describing',
        round: 1,
        currentPlayerNumber: 1,
        countdown: 60,
        players: [],
      }
      ;(request.get as jest.Mock).mockResolvedValue(mockGame)
      
      const result = await GameService.getGameStatus('room_001')
      
      expect(request.get).toHaveBeenCalledWith('/game/status', { room_id: 'room_001' })
      expect(result.gameId).toBe('game_001')
      expect(result.roomId).toBe('room_001')
      expect(result.phase).toBe('describing')
    })
  })
  
  describe('vote 方法', () => {
    it('应该通过 WebSocket 投票', async () => {
      const wsService = require('../../miniprogram/services/websocket.service').wsService
      
      const result = await GameService.vote('room_001', 'player_002')
      
      expect(wsService.vote).toHaveBeenCalledWith('player_002')
      expect(result).toEqual({ success: true })
    })
  })
})
