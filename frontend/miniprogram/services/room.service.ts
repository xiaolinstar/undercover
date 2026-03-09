/**
 * 房间服务
 * 实现 IRoomService 接口
 */

import { request } from '../utils/request'
import { API_ENDPOINTS, API_CONFIG } from '../config/api.config'
import { MockRoomService } from '../mock/room.mock'
import { Room } from '../models/room.model'
import { Player } from '../models/player.model'
import { wsService } from './websocket.service'
import type { IRoomService } from '../types/room.interface'
import type { RoomResponse, ApiResponse } from '../types/api.types'

// ============ 服务端数据类型定义 ============

/**
 * 验证并转换房间状态
 */
function parseRoomStatus(status: string): 'waiting' | 'playing' | 'finished' {
  const validStatuses: Array<'waiting' | 'playing' | 'finished'> = ['waiting', 'playing', 'finished']
  return validStatuses.includes(status as 'waiting' | 'playing' | 'finished') 
    ? (status as 'waiting' | 'playing' | 'finished') 
    : 'waiting'
}

/**
 * 处理服务端返回的房间数据
 */
function processRoomData(response: unknown): Room {
  // 空值检查
  if (!response) {
    console.error('[RoomService] 服务端返回数据为空')
    throw new Error('服务端返回数据为空')
  }

  // 打印完整响应用于调试
  console.log('[RoomService] 服务端完整响应:', JSON.stringify(response, null, 2))

  // 处理可能的嵌套结构
  let rawData: unknown
  
  const responseObj = response as Record<string, unknown>
  
  if (responseObj.data && typeof responseObj.data === 'object') {
    // 情况1: 嵌套在 data 字段中
    rawData = responseObj.data
    console.log('[RoomService] 检测到嵌套结构 (data 字段)')
  } else if (responseObj.room && typeof responseObj.room === 'object') {
    // 情况2: 嵌套在 room 字段中
    rawData = responseObj.room
    console.log('[RoomService] 检测到嵌套结构 (room 字段)')
  } else {
    // 情况3: 直接返回房间数据
    rawData = response
    console.log('[RoomService] 检测到直接数据结构')
  }

  // 使用 Record 类型安全访问字段
  const data = rawData as Record<string, unknown>

  // 兼容 snake_case 和 camelCase 格式
  const roomId = String(data.roomId || data.room_id || '')
  const roomCode = String(data.roomCode || data.room_code || '')
  const ownerId = String(data.ownerId || data.owner_id || '')
  const maxPlayers = Number(data.maxPlayers || data.max_players) || 12
  const status = String(data.status || 'waiting')
  const createdAt = String(data.createdAt || data.created_at || '')

  // 处理 players 数据
  const playersRaw = data.players
  const players: Player[] = Array.isArray(playersRaw) ? playersRaw.map(p => {
    const playerData = p as Record<string, unknown>
    return {
      playerId: String(playerData.playerId || playerData.player_id || ''),
      nickname: String(playerData.nickname || ''),
      avatar: String(playerData.avatar || playerData.avatar_url || ''),
      isOwner: Boolean(playerData.isOwner || playerData.is_owner),
      isReady: Boolean(playerData.isReady || playerData.is_ready),
      playerNumber: Number(playerData.playerNumber || playerData.player_number) || 0,
    }
  }) : []

  // 验证必要字段
  if (!roomId) {
    console.error('[RoomService] roomId 为空，原始数据:', JSON.stringify(data))
    throw new Error('房间数据无效：缺少 roomId')
  }
  
  // 验证roomId不是"underfind"
  if (roomId === 'underfind') {
    console.error('[RoomService] roomId 为 underfind，原始数据:', JSON.stringify(data))
    throw new Error('房间数据无效：roomId 错误')
  }

  const roomData: Room = {
    roomId,
    roomCode,
    ownerId,
    players,
    maxPlayers,
    status: parseRoomStatus(status),
    createdAt,
  }

  console.log('[RoomService] 处理后的房间数据:', JSON.stringify(roomData, null, 2))
  console.log('[RoomService] 最终结果 - roomId:', roomData.roomId, 'roomCode:', roomData.roomCode)

  return roomData
}

// ============ 房间服务实现 ============

/**
 * 房间服务类
 * 实现 IRoomService 接口
 * 使用静态方法保持向后兼容
 */
export class RoomService implements IRoomService {
  /**
   * 创建房间
   */
  static async createRoom(): Promise<Room> {
    // Mock 模式
    if (API_CONFIG.USE_MOCK) {
      return await MockRoomService.createRoom()
    }

    // 真实 API 模式
    console.log('[RoomService] 创建房间')

    const response = await request.post<ApiResponse<RoomResponse>>(
      API_ENDPOINTS.CREATE_ROOM,
      {}
    )

    const room = processRoomData(response)

    // 验证必要字段
    if (!room.roomId) {
      console.error('[RoomService] 创建房间失败: roomId 为空')
      throw new Error('创建房间失败：缺少房间ID')
    }

    // 尝试加入 WebSocket 房间，但不阻塞主流程
    try {
      await wsService.joinRoom(room.roomId)
    } catch (wsError) {
      console.warn('[RoomService] WebSocket 连接失败，但房间已创建:', wsError)
    }

    return room
  }

  /**
   * 加入房间
   * @param roomCode 4位房间号（用户输入）
   */
  static async joinRoom(roomCode: string): Promise<Room> {
    // Mock 模式
    if (API_CONFIG.USE_MOCK) {
      return await MockRoomService.joinRoom(roomCode)
    }

    // 真实 API 模式
    console.log('[RoomService] 加入房间, room_code:', roomCode)

    const response = await request.post<ApiResponse<RoomResponse>>(
      API_ENDPOINTS.JOIN_ROOM,
      { room_code: roomCode }
    )

    const room = processRoomData(response)

    // 验证必要字段
    if (!room.roomId) {
      console.error('[RoomService] 加入房间失败: roomId 为空')
      throw new Error('加入房间失败：缺少房间ID')
    }

    // 尝试加入 WebSocket 房间，但不阻塞主流程
    try {
      await wsService.joinRoom(room.roomId)
    } catch (wsError) {
      console.warn('[RoomService] WebSocket 连接失败，但已加入房间:', wsError)
    }

    return room
  }

  /**
   * 获取房间信息
   * @param roomId 房间唯一标识
   */
  static async getRoom(roomId: string): Promise<Room> {
    // Mock 模式
    if (API_CONFIG.USE_MOCK) {
      return await MockRoomService.getRoom(roomId)
    }

    // 真实 API 模式
    console.log('[RoomService] 获取房间信息, roomId:', roomId)

    const response = await request.get<ApiResponse<RoomResponse>>(
      API_ENDPOINTS.GET_ROOM.replace(':roomId', roomId)
    )

    return processRoomData(response)
  }

  /**
   * 离开房间
   * @param roomId 房间唯一标识
   */
  static async leaveRoom(roomId: string): Promise<void> {
    // Mock 模式
    if (API_CONFIG.USE_MOCK) {
      return await MockRoomService.leaveRoom(roomId)
    }

    // 真实 API 模式
    console.log('[RoomService] 离开房间, room_id:', roomId)

    await request.post<void>(
      API_ENDPOINTS.LEAVE_ROOM,
      { room_id: roomId }
    )

    // 尝试离开 WebSocket 房间
    try {
      await wsService.leaveRoom()
    } catch (wsError) {
      console.warn('[RoomService] WebSocket 断开失败:', wsError)
    }
  }

  // ============ 实例方法（实现接口） ============

  async createRoom(): Promise<Room> {
    return RoomService.createRoom()
  }

  async joinRoom(roomCode: string): Promise<Room> {
    return RoomService.joinRoom(roomCode)
  }

  async getRoom(roomId: string): Promise<Room> {
    return RoomService.getRoom(roomId)
  }

  async leaveRoom(roomId: string): Promise<void> {
    return RoomService.leaveRoom(roomId)
  }
}
