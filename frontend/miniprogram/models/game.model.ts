/**
 * 游戏模型
 */

import { PlayerInGame, PlayerRole } from './player.model'

/**
 * 游戏阶段
 */
export type GamePhase = 'describing' | 'voting' | 'finished'

/**
 * 游戏状态
 */
export interface Game {
  gameId: string
  roomId: string
  phase: GamePhase
  currentRound: number
  currentPlayer?: number
  countdown?: number
  word?: string
  role?: PlayerRole
  players: PlayerInGame[]
  winner?: PlayerRole
  words?: GameWords
}

/**
 * 游戏词语
 */
export interface GameWords {
  civilian: string
  undercover: string
}

/**
 * 投票结果
 */
export interface VoteResult {
  success: boolean
  voteCounts?: Record<string, number>
}
