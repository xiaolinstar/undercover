/**
 * GameLogic 工具类测试
 */

import { GameLogic } from '../../miniprogram/utils/game-logic'
import { PlayerInGame } from '../../miniprogram/models/player.model'

describe('GameLogic 游戏逻辑工具类', () => {
  describe('checkGameEnd 方法', () => {
    it('卧底全部淘汰时平民胜利', () => {
      const players: PlayerInGame[] = [
        { playerId: '1', playerNumber: 1, nickname: '玩家1', avatar: '', isOwner: true, isReady: false, isAlive: true, hasVoted: false, role: 'civilian' },
        { playerId: '2', playerNumber: 2, nickname: '玩家2', avatar: '', isOwner: false, isReady: false, isAlive: false, hasVoted: false, role: 'undercover' },
        { playerId: '3', playerNumber: 3, nickname: '玩家3', avatar: '', isOwner: false, isReady: false, isAlive: true, hasVoted: false, role: 'civilian' },
      ]

      const result = GameLogic.checkGameEnd(players)
      
      expect(result.ended).toBe(true)
      expect(result.winner).toBe('civilian')
    })
    
    it('卧底人数 >= 平民人数时卧底胜利', () => {
      const players: PlayerInGame[] = [
        { playerId: '1', playerNumber: 1, nickname: '玩家1', avatar: '', isOwner: true, isReady: false, isAlive: false, hasVoted: false, role: 'civilian' },
        { playerId: '2', playerNumber: 2, nickname: '玩家2', avatar: '', isOwner: false, isReady: false, isAlive: true, hasVoted: false, role: 'undercover' },
        { playerId: '3', playerNumber: 3, nickname: '玩家3', avatar: '', isOwner: false, isReady: false, isAlive: true, hasVoted: false, role: 'undercover' },
      ]
      
      const result = GameLogic.checkGameEnd(players)
      
      expect(result.ended).toBe(true)
      expect(result.winner).toBe('undercover')
    })
    
    it('游戏未结束时返回 ended: false', () => {
      const players: PlayerInGame[] = [
        { playerId: '1', playerNumber: 1, nickname: '玩家1', avatar: '', isOwner: true, isReady: false, isAlive: true, hasVoted: false, role: 'civilian' },
        { playerId: '2', playerNumber: 2, nickname: '玩家2', avatar: '', isOwner: false, isReady: false, isAlive: true, hasVoted: false, role: 'undercover' },
        { playerId: '3', playerNumber: 3, nickname: '玩家3', avatar: '', isOwner: false, isReady: false, isAlive: true, hasVoted: false, role: 'civilian' },
      ]
      
      const result = GameLogic.checkGameEnd(players)
      
      expect(result.ended).toBe(false)
      expect(result.winner).toBeUndefined()
    })
    
    it('所有玩家存活时游戏未结束', () => {
      const players: PlayerInGame[] = [
        { playerId: '1', playerNumber: 1, nickname: '玩家1', avatar: '', isOwner: true, isReady: false, isAlive: true, hasVoted: false, role: 'civilian' },
        { playerId: '2', playerNumber: 2, nickname: '玩家2', avatar: '', isOwner: false, isReady: false, isAlive: true, hasVoted: false, role: 'civilian' },
        { playerId: '3', playerNumber: 3, nickname: '玩家3', avatar: '', isOwner: false, isReady: false, isAlive: true, hasVoted: false, role: 'undercover' },
      ]
      
      const result = GameLogic.checkGameEnd(players)
      
      expect(result.ended).toBe(false)
    })
  })
  
  describe('countVotes 方法', () => {
    it('应该正确统计票数', () => {
      const votes: Record<number, number> = {
        1: 2,
        2: 2,
        3: 2,
      }
      
      const result = GameLogic.countVotes(votes)
      
      expect(result.eliminated).toBe(2)
      expect(result.voteCounts[2]).toBe(3)
    })
    
    it('票数相同时返回第一个遍历到的最高票玩家', () => {
      // 设置玩家1和玩家2得票相同
      const votes: Record<number, number> = {
        1: 1,  // 投给玩家1
        2: 2,  // 投给玩家2
        3: 1,  // 投给玩家1
        4: 2,  // 投给玩家2
      }
      
      const result = GameLogic.countVotes(votes)
      
      // 票数相同时，返回第一个遍历到的最高票玩家（使用 > 而非 >=）
      // Object.entries 遍历顺序：先玩家1（2票），后玩家2（2票），所以返回1号
      expect(result.eliminated).toBe(1)
      expect(result.voteCounts[1]).toBe(2)
      expect(result.voteCounts[2]).toBe(2)
    })
    
    it('空投票应该返回 0', () => {
      const votes: Record<number, number> = {}
      
      const result = GameLogic.countVotes(votes)
      
      expect(result.eliminated).toBe(0)
      expect(result.voteCounts).toEqual({})
    })
  })
  
  describe('selectSpies 方法', () => {
    it('应该选择指定数量的卧底', () => {
      const playerCount = 6
      const spyCount = 2
      
      const spies = GameLogic.selectSpies(playerCount, spyCount)
      
      expect(spies.length).toBe(spyCount)
      expect(spies.every(s => s >= 1 && s <= playerCount)).toBe(true)
    })
    
    it('默认选择 1 个卧底', () => {
      const playerCount = 6
      
      const spies = GameLogic.selectSpies(playerCount)
      
      expect(spies.length).toBe(1)
    })
    
    it('卧底序号应该不重复', () => {
      const playerCount = 6
      const spyCount = 3
      
      const spies = GameLogic.selectSpies(playerCount, spyCount)
      const uniqueSpies = [...new Set(spies)]
      
      expect(uniqueSpies.length).toBe(spyCount)
    })
  })
  
  describe('assignRoles 方法', () => {
    it('应该正确分配角色', () => {
      const players: PlayerInGame[] = [
        { playerId: '1', playerNumber: 1, nickname: '玩家1', avatar: '', isOwner: true, isReady: false, isAlive: true, hasVoted: false },
        { playerId: '2', playerNumber: 2, nickname: '玩家2', avatar: '', isOwner: false, isReady: false, isAlive: true, hasVoted: false },
        { playerId: '3', playerNumber: 3, nickname: '玩家3', avatar: '', isOwner: false, isReady: false, isAlive: true, hasVoted: false },
      ]
      const wordPair = { civilian: '苹果', undercover: '橘子' }
      const spyIndices = [2]
      
      GameLogic.assignRoles(players, wordPair, spyIndices)
      
      expect(players[0].role).toBe('civilian')
      expect(players[1].role).toBe('undercover')
      expect(players[2].role).toBe('civilian')
    })
    
    it('应该支持多个卧底', () => {
      const players: PlayerInGame[] = [
        { playerId: '1', playerNumber: 1, nickname: '玩家1', avatar: '', isOwner: true, isReady: false, isAlive: true, hasVoted: false },
        { playerId: '2', playerNumber: 2, nickname: '玩家2', avatar: '', isOwner: false, isReady: false, isAlive: true, hasVoted: false },
        { playerId: '3', playerNumber: 3, nickname: '玩家3', avatar: '', isOwner: false, isReady: false, isAlive: true, hasVoted: false },
        { playerId: '4', playerNumber: 4, nickname: '玩家4', avatar: '', isOwner: false, isReady: false, isAlive: true, hasVoted: false },
      ]
      const wordPair = { civilian: '电脑', undercover: '笔记本' }
      const spyIndices = [2, 4]
      
      GameLogic.assignRoles(players, wordPair, spyIndices)
      
      expect(players[0].role).toBe('civilian')
      expect(players[1].role).toBe('undercover')
      expect(players[2].role).toBe('civilian')
      expect(players[3].role).toBe('undercover')
    })
  })
  
  describe('validateRoomCode 方法', () => {
    it('有效的房间号应该返回 true', () => {
      expect(GameLogic.validateRoomCode('1234')).toBe(true)
      expect(GameLogic.validateRoomCode('0000')).toBe(true)
      expect(GameLogic.validateRoomCode('9999')).toBe(true)
    })
    
    it('无效的房间号应该返回 false', () => {
      expect(GameLogic.validateRoomCode('123')).toBe(false)
      expect(GameLogic.validateRoomCode('12345')).toBe(false)
      expect(GameLogic.validateRoomCode('abcd')).toBe(false)
      expect(GameLogic.validateRoomCode('12a4')).toBe(false)
      expect(GameLogic.validateRoomCode('')).toBe(false)
    })
  })
  
  describe('validatePlayerCount 方法', () => {
    it('有效的玩家数量应该返回 true', () => {
      expect(GameLogic.validatePlayerCount(3)).toBe(true)
      expect(GameLogic.validatePlayerCount(6)).toBe(true)
      expect(GameLogic.validatePlayerCount(12)).toBe(true)
    })
    
    it('无效的玩家数量应该返回 false', () => {
      expect(GameLogic.validatePlayerCount(2)).toBe(false)
      expect(GameLogic.validatePlayerCount(13)).toBe(false)
      expect(GameLogic.validatePlayerCount(0)).toBe(false)
      expect(GameLogic.validatePlayerCount(-1)).toBe(false)
    })
    
    it('应该支持自定义范围', () => {
      expect(GameLogic.validatePlayerCount(5, 4, 8)).toBe(true)
      expect(GameLogic.validatePlayerCount(3, 4, 8)).toBe(false)
      expect(GameLogic.validatePlayerCount(9, 4, 8)).toBe(false)
    })
  })
  
  describe('calculateWinRate 方法', () => {
    it('应该正确计算胜率', () => {
      expect(GameLogic.calculateWinRate(10, 6)).toBe(60)
      expect(GameLogic.calculateWinRate(10, 5)).toBe(50)
      expect(GameLogic.calculateWinRate(10, 10)).toBe(100)
      expect(GameLogic.calculateWinRate(10, 0)).toBe(0)
    })
    
    it('游戏场次为 0 时应该返回 0', () => {
      expect(GameLogic.calculateWinRate(0, 0)).toBe(0)
    })
    
    it('应该四舍五入到整数', () => {
      expect(GameLogic.calculateWinRate(7, 3)).toBe(43) // 42.857... -> 43
      expect(GameLogic.calculateWinRate(7, 4)).toBe(57) // 57.142... -> 57
    })
  })
})
