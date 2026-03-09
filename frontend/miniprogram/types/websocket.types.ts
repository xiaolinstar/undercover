/**
 * WebSocket 连接状态
 */
export enum WSStatus {
  CONNECTING = 'connecting',
  CONNECTED = 'connected',
  DISCONNECTED = 'disconnected',
  RECONNECTING = 'reconnecting',
}

/**
 * WebSocket 事件类型
 */
export enum WSEventType {
  // 连接事件
  CONNECTED = 'connected',
  DISCONNECTED = 'disconnected',
  RECONNECTING = 'reconnecting',
  ERROR = 'error',
  SUBSCRIBED = 'subscribed',
  SUBSCRIBE_ERROR = 'subscribe_error',
  PONG = 'pong',
  SERVER_SHUTDOWN = 'server_shutdown',
  SYSTEM = 'system',

  // 房间事件
  PLAYER_JOINED = 'room.player_joined',
  PLAYER_LEFT = 'room.player_left',
  PLAYER_READY = 'room.player_ready',
  DISBANDED = 'room.disbanded',
  ROOM_UPDATE = 'room_update',

  // 游戏事件
  GAME_STARTED = 'game.started',
  GAME_PHASE_CHANGED = 'game.phase_changed',
  PLAYER_ELIMINATED = 'game.player_eliminated',
  GAME_ENDED = 'game.ended',

  // 投票事件
  VOTE_SUBMITTED = 'vote.submitted',
  VOTE_COMPLETED = 'vote.completed',

  // 消息事件
  PLAYER_MESSAGE = 'player_message',
  SYSTEM_MESSAGE = 'system_message',
}

/**
 * WebSocket 消息基础结构
 */
export interface WSMessage<T> {
  type: WSEventType
  data: T
  timestamp: number
}

/**
 * 玩家加入事件数据
 */
export interface PlayerJoinData {
  roomId: string
  player: PlayerInRoom
}

/**
 * 玩家离开事件数据
 */
export interface PlayerLeaveData {
  roomId: string
  playerId: string
}

/**
 * 房间更新事件数据
 */
export interface RoomUpdateData {
  roomId: string
  players: PlayerInRoom[]
  status: RoomStatus
}

/**
 * 游戏开始事件数据
 */
export interface GameStartData {
  roomId: string
  gameId: string
  word: string
  role: PlayerRole
  players: PlayerInGame[]
}

/**
 * 游戏阶段变化事件数据
 */
export interface GamePhaseChangeData {
  roomId: string
  gameId: string
  phase: GamePhase
  round: number
  currentPlayerNumber?: number
  countdown?: number
}

/**
 * 玩家投票事件数据
 */
export interface PlayerVoteData {
  roomId: string
  gameId: string
  voterId: string
  targetId: string
  voteCounts: Record<string, number>
}

/**
 * 游戏结束事件数据
 */
export interface GameEndData {
  roomId: string
  gameId: string
  winner: PlayerRole
  players: PlayerInGame[]
  words: GameWords
}

/**
 * 玩家消息事件数据
 */
export interface PlayerMessageData {
  roomId: string
  playerId: string
  message: string
  timestamp: number
}

/**
 * 系统消息事件数据
 */
export interface SystemMessageData {
  roomId: string
  message: string
  type: SystemMessageType
  timestamp: number
}

/**
 * WebSocket 事件监听器
 */
export type WSEventListener<T> = (data: T) => void

// ============ 辅助类型 ============

/**
 * 房间内玩家信息
 */
export interface PlayerInRoom {
  playerId: string
  nickname: string
  avatar: string
  playerNumber: number
  isOwner: boolean
  isReady: boolean
}

/**
 * 游戏中玩家信息
 */
export interface PlayerInGame extends PlayerInRoom {
  isAlive: boolean
  hasVoted: boolean
  word?: string
  role?: PlayerRole
}

/**
 * 玩家角色
 */
export type PlayerRole = 'civilian' | 'undercover'

/**
 * 房间状态
 */
export type RoomStatus = 'waiting' | 'playing' | 'finished'

/**
 * 游戏阶段
 */
export type GamePhase = 'describing' | 'voting' | 'finished'

/**
 * 游戏词语
 */
export interface GameWords {
  civilian: string
  undercover: string
}

/**
 * 系统消息类型
 */
export type SystemMessageType = 'info' | 'warning' | 'error'
