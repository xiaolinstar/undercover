/**
 * 玩家模型
 */

/**
 * 玩家角色
 */
export type PlayerRole = 'civilian' | 'undercover'

/**
 * 玩家状态
 */
export type PlayerStatus = 'waiting' | 'ready' | 'playing' | 'dead'

/**
 * 玩家基础信息
 */
export interface Player {
  playerId: string
  playerNumber: number
  nickname: string
  avatar: string
  isOwner: boolean
  isReady: boolean
}

/**
 * 游戏中玩家信息（扩展）
 */
export interface PlayerInGame extends Player {
  isAlive: boolean
  hasVoted: boolean
  role?: PlayerRole
  word?: string
}
