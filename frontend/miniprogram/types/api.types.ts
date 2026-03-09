/**
 * API 响应类型定义
 */

/**
 * API 基础响应结构
 */
export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

/**
 * 登录响应
 */
export interface LoginResponse {
  token: string
  user: UserResponse
}

/**
 * 用户信息响应
 */
export interface UserResponse {
  id: string
  openid: string
  nickname: string
  avatar_url: string
  total_games: number
  wins: number
}

/**
 * 用户统计信息响应
 */
export interface UserStatsResponse {
  userId: string
  openid: string
  nickname: string
  avatar: string
  gamesPlayed: number
  gamesWon: number
  createdAt: string
}

/**
 * 创建房间响应
 */
export interface CreateRoomResponse {
  roomId: string
  roomCode: string
  ownerId: string
  players: PlayerResponse[]
  maxPlayers: number
  status: string
  createdAt: string
}

/**
 * 加入房间响应
 */
export interface JoinRoomResponse {
  roomId: string
  roomCode: string
  ownerId: string
  players: PlayerResponse[]
  maxPlayers: number
  status: string
  createdAt: string
}

/**
 * 房间信息响应
 */
export interface RoomResponse {
  roomId: string
  roomCode: string
  ownerId: string
  players: PlayerResponse[]
  maxPlayers: number
  status: string
  createdAt: string
}

/**
 * 玩家信息响应
 */
export interface PlayerResponse {
  playerId: string
  nickname: string
  avatar: string
  isOwner: boolean
  isReady: boolean
  playerNumber: number
}

/**
 * 游戏开始响应
 */
export interface GameStartResponse {
  gameId: string
  roomId: string
  word: string
  role: 'civilian' | 'undercover'
  players: PlayerResponse[]
}

/**
 * 游戏状态响应
 */
export interface GameStatusResponse {
  gameId: string
  roomId: string
  phase: 'describing' | 'voting' | 'finished'
  round: number
  currentPlayerNumber: number
  countdown: number
  players: PlayerResponse[]
}
