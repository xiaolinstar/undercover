/**
 * API 配置
 */

export const API_CONFIG = {
  // 是否启用 Mock 模式
  USE_MOCK: false,
  
  // 服务端 API 地址
  BASE_URL: 'http://localhost:5001/api/v1',
  
  // WebSocket 地址
  WS_URL: 'ws://localhost:5001/ws',
  
  // 请求超时时间
  TIMEOUT: 10000,
}

export const API_ENDPOINTS = {
  // 认证相关
  LOGIN: '/auth/login',
  LOGOUT: '/auth/logout',
  UPDATE_USERINFO: '/auth/update-userinfo',
  GET_USER_STATS: '/auth/user-stats',
  
  // 房间相关
  CREATE_ROOM: '/room/create',     // 参数: max_players
  JOIN_ROOM: '/room/join',         // 参数: room_code (4位数字)
  GET_ROOM: '/room/:roomId',       // 路径参数: roomId (UUID)
  LEAVE_ROOM: '/room/leave',       // 参数: room_id
  
  // 游戏相关
  START_GAME: '/game/start',       // 参数: room_id
  GET_STATUS: '/game/status',      // 参数: room_id
  VOTE: '/game/vote',              // 参数: room_id, target_player_id
}

export const GAME_CONFIG = {
  MAX_PLAYERS: 12,
  MIN_PLAYERS: 3,
  VOTE_TIME: 30,
  DESCRIBE_TIME: 60,
}
