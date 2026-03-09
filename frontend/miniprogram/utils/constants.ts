/**
 * 常量定义
 */

// 游戏状态
export enum GameStatus {
  WAITING = 'waiting',
  PLAYING = 'playing',
  FINISHED = 'finished',
}

// 游戏阶段
export enum GamePhase {
  DESCRIBING = 'describing',
  VOTING = 'voting',
  FINISHED = 'finished',
}

// 玩家角色
export enum PlayerRole {
  CIVILIAN = 'civilian',
  SPY = 'spy',
}

// WebSocket 事件
export enum WSEvent {
  // 客户端 -> 服务端
  JOIN_ROOM = 'join_room',
  LEAVE_ROOM = 'leave_room',
  START_GAME = 'start_game',
  VOTE = 'vote',
  
  // 服务端 -> 客户端
  PLAYER_JOINED = 'player_joined',
  PLAYER_LEFT = 'player_left',
  GAME_STARTED = 'game_started',
  GAME_STATUS = 'game_status',
  VOTE_START = 'vote_start',
  VOTE_RESULT = 'vote_result',
  GAME_FINISHED = 'game_finished',
  ERROR = 'error',
}

// 颜色主题
export const COLORS = {
  PRIMARY: '#667eea',
  SUCCESS: '#10b981',
  WARNING: '#f59e0b',
  DANGER: '#ef4444',
  INFO: '#3b82f6',
  TEXT: '#333333',
  TEXT_LIGHT: '#666666',
  TEXT_LIGHTER: '#999999',
  BG: '#F5F5F5',
  WHITE: '#FFFFFF',
  BORDER: '#E5E5E5',
}
