/**
 * 常量定义测试
 */

import { GameStatus, GamePhase, PlayerRole, WSEvent, COLORS } from '../../miniprogram/utils/constants'

describe('常量定义', () => {
  describe('GameStatus 枚举', () => {
    it('应该包含所有游戏状态', () => {
      expect(GameStatus.WAITING).toBe('waiting')
      expect(GameStatus.PLAYING).toBe('playing')
      expect(GameStatus.FINISHED).toBe('finished')
    })
  })
  
  describe('GamePhase 枚举', () => {
    it('应该包含所有游戏阶段', () => {
      expect(GamePhase.DESCRIBING).toBe('describing')
      expect(GamePhase.VOTING).toBe('voting')
      expect(GamePhase.FINISHED).toBe('finished')
    })
  })
  
  describe('PlayerRole 枚举', () => {
    it('应该包含所有玩家角色', () => {
      expect(PlayerRole.CIVILIAN).toBe('civilian')
      expect(PlayerRole.SPY).toBe('spy')
    })
  })
  
  describe('WSEvent 枚举', () => {
    it('应该包含所有客户端事件', () => {
      expect(WSEvent.JOIN_ROOM).toBe('join_room')
      expect(WSEvent.LEAVE_ROOM).toBe('leave_room')
      expect(WSEvent.START_GAME).toBe('start_game')
      expect(WSEvent.VOTE).toBe('vote')
    })
    
    it('应该包含所有服务端事件', () => {
      expect(WSEvent.PLAYER_JOINED).toBe('player_joined')
      expect(WSEvent.PLAYER_LEFT).toBe('player_left')
      expect(WSEvent.GAME_STARTED).toBe('game_started')
      expect(WSEvent.GAME_STATUS).toBe('game_status')
      expect(WSEvent.VOTE_START).toBe('vote_start')
      expect(WSEvent.VOTE_RESULT).toBe('vote_result')
      expect(WSEvent.GAME_FINISHED).toBe('game_finished')
      expect(WSEvent.ERROR).toBe('error')
    })
  })
  
  describe('COLORS 常量', () => {
    it('应该包含所有颜色定义', () => {
      expect(COLORS.PRIMARY).toBeTruthy()
      expect(COLORS.SUCCESS).toBeTruthy()
      expect(COLORS.WARNING).toBeTruthy()
      expect(COLORS.DANGER).toBeTruthy()
      expect(COLORS.INFO).toBeTruthy()
      expect(COLORS.TEXT).toBeTruthy()
      expect(COLORS.BG).toBeTruthy()
      expect(COLORS.WHITE).toBeTruthy()
    })
    
    it('颜色值应该是有效的颜色代码', () => {
      const colorPattern = /^#[0-9A-Fa-f]{6}$/
      
      expect(COLORS.PRIMARY).toMatch(colorPattern)
      expect(COLORS.SUCCESS).toMatch(colorPattern)
      expect(COLORS.WARNING).toMatch(colorPattern)
      expect(COLORS.DANGER).toMatch(colorPattern)
    })
  })
})
