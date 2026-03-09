/**
 * 游戏服务
 * 实现 IGameService 接口
 */

import { request } from '../utils/request'
import { API_ENDPOINTS, API_CONFIG } from '../config/api.config'
import { MockGameService } from '../mock/game.mock'
import { Game, VoteResult } from '../models/game.model'
import { PlayerRole } from '../models/player.model'
import type { IGameService } from '../types/game.interface'
import type { GameStartResponse, GameStatusResponse, ApiResponse } from '../types/api.types'
import { wsService } from './websocket.service'

// ============ 数据处理函数 ============

/**
 * 验证并转换游戏阶段
 */
function parseGamePhase(phase: string): 'describing' | 'voting' | 'finished' {
  const validPhases: readonly string[] = ['describing', 'voting', 'finished']
  return validPhases.includes(phase)
    ? (phase as 'describing' | 'voting' | 'finished')
    : 'describing'
}

/**
 * 验证并转换玩家角色
 */
function parsePlayerRole(role: string): PlayerRole {
  return role === 'undercover' ? 'undercover' : 'civilian'
}

/**
 * 处理游戏开始响应
 */
function processGameStartResponse(response: unknown): Game {
  if (!response) {
    throw new Error('游戏开始响应为空')
  }

  const rawData = (response as { data?: unknown }).data || response
  const data = rawData as GameStartResponse

  return {
    gameId: data.gameId,
    roomId: data.roomId,
    phase: 'describing',
    currentRound: 1,
    word: data.word,
    role: parsePlayerRole(data.role),
    players: data.players.map((p: any) => ({
      playerId: p.id || p.playerId,
      playerNumber: p.number || p.playerNumber,
      nickname: p.nickname,
      avatar: p.avatar,
      isOwner: p.isOwner || false,
      isReady: p.isReady || false,
      isAlive: p.isAlive ?? true,
      hasVoted: p.hasVoted ?? false,
      role: p.role ? parsePlayerRole(p.role) : undefined,
    })),
  }
}

/**
 * 处理游戏状态响应
 */
function processGameStatusResponse(response: unknown): Game {
  if (!response) {
    throw new Error('游戏状态响应为空')
  }

  const rawData = (response as { data?: unknown }).data || response
  const data = rawData as GameStatusResponse

  return {
    gameId: data.gameId,
    roomId: data.roomId,
    phase: parseGamePhase(data.phase),
    currentRound: data.round,
    currentPlayer: data.currentPlayerNumber,
    countdown: data.countdown,
    players: data.players.map((p: any) => ({
      playerId: p.id || p.playerId,
      playerNumber: p.number || p.playerNumber,
      nickname: p.nickname,
      avatar: p.avatar,
      isOwner: p.isOwner || false,
      isReady: p.isReady || false,
      isAlive: p.isAlive ?? true,
      hasVoted: p.hasVoted ?? false,
      role: p.role ? parsePlayerRole(p.role) : undefined,
    })),
  }
}

// ============ 游戏服务实现 ============

/**
 * 游戏服务类
 * 实现 IGameService 接口
 */
export class GameService implements IGameService {
  /**
   * 开始游戏
   * @param roomId 房间ID
   */
  static async startGame(roomId: string): Promise<Game> {
    // Mock 模式
    if (API_CONFIG.USE_MOCK) {
      return await MockGameService.startGame(roomId)
    }

    // 真实 API 模式
    const response = await request.post<ApiResponse<GameStartResponse>>(
      API_ENDPOINTS.START_GAME,
      { room_id: roomId }
    )

    return processGameStartResponse(response)
  }

  /**
   * 获取游戏状态
   * @param roomId 房间ID
   */
  static async getGameStatus(roomId: string): Promise<Game> {
    // Mock 模式
    if (API_CONFIG.USE_MOCK) {
      return await MockGameService.getGameStatus(roomId)
    }

    // 真实 API 模式
    const response = await request.get<ApiResponse<GameStatusResponse>>(
      API_ENDPOINTS.GET_STATUS,
      { room_id: roomId }
    )

    return processGameStatusResponse(response)
  }

  /**
   * 投票
   * @param roomId 房间ID
   * @param targetPlayerId 目标玩家ID
   */
  static async vote(roomId: string, targetPlayerId: string): Promise<VoteResult> {
    // Mock 模式
    if (API_CONFIG.USE_MOCK) {
      // Mock 模式下，targetPlayerId 是玩家序号，需要转换为数字
      return await MockGameService.vote(roomId, parseInt(targetPlayerId))
    }

    // 真实 API 模式 - 通过 WebSocket 投票
    await wsService.vote(targetPlayerId)

    return { success: true }
  }

  // ============ 实例方法（实现接口） ============

  async startGame(roomId: string): Promise<Game> {
    return GameService.startGame(roomId)
  }

  async getGameStatus(roomId: string): Promise<Game> {
    return GameService.getGameStatus(roomId)
  }

  async vote(roomId: string, targetPlayerId: string): Promise<void> {
    await GameService.vote(roomId, targetPlayerId)
  }
}

// ============ 类型导出 ============

export type { VoteResult }
