/**
 * 游戏服务接口定义
 */

import type { Game } from '../models/game.model'

/**
 * 投票参数
 */
export interface VoteParams {
  roomId: string
  targetPlayerId: string
}

/**
 * 游戏服务接口
 */
export interface IGameService {
  /**
   * 开始游戏
   * @param roomId 房间ID
   */
  startGame(roomId: string): Promise<Game>

  /**
   * 获取游戏状态
   * @param roomId 房间ID
   */
  getGameStatus(roomId: string): Promise<Game>

  /**
   * 投票
   * @param roomId 房间ID
   * @param targetPlayerId 目标玩家ID
   */
  vote(roomId: string, targetPlayerId: string): Promise<void>
}
