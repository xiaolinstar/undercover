/**
 * 类型定义统一导出
 */

// API 响应类型
export type {
  ApiResponse,
  LoginResponse,
  UserStatsResponse,
  CreateRoomResponse,
  JoinRoomResponse,
  RoomResponse,
  PlayerResponse,
  GameStartResponse,
  GameStatusResponse,
} from './api.types'

// 服务接口
export type { IAuthService } from './auth.interface'
export type { IRoomService } from './room.interface'
export type { IWebSocketService } from './websocket.interface'
export type { IGameService, VoteParams } from './game.interface'

// WebSocket 事件类型
export {
  WSStatus,
  WSEventType,
} from './websocket.types'

export type {
  WSMessage,
  PlayerJoinData,
  PlayerLeaveData,
  RoomUpdateData,
  GameStartData,
  GamePhaseChangeData,
  PlayerVoteData,
  GameEndData,
  PlayerMessageData,
  SystemMessageData,
  WSEventListener,
} from './websocket.types'
