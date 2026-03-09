/**
 * Mock 数据
 */

// Mock 用户数据
export const MOCK_USER = {
  userId: 'user_001',
  openid: 'mock_openid_001',
  nickname: '测试用户',
  avatar: 'https://mmbiz.qpic.cn/mmbiz/icTdbqWNOwNRna42FI242Lcia07jQodd2FJGIYQfG0LAJGFxM4FbnQP6yfMxBgJ0F3YRqJCJ1aPAK2dQagdusBZg/0',
  gamesPlayed: 10,
  gamesWon: 6,
  createdAt: '2024-01-01T00:00:00.000Z',
}

// Mock Token
export const MOCK_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoidXNlcl8wMDEiLCJleHAiOjE3NjA0ODA4ODF9.7QZ9c4h8f7g6e5d4c3b2a1"

// Mock 房间数据
export const MOCK_ROOMS: Record<string, any> = {
  '1234': {
    roomId: 'room_001',
    roomCode: '1234',
    ownerId: 'user_001',
    players: [
      {
        playerId: 'user_001',
        playerNumber: 1,
        nickname: '测试用户',
        avatar: MOCK_USER.avatar,
        isOwner: true,
        isAlive: true,
      },
    ],
    maxPlayers: 12,
    status: 'waiting',
    createdAt: new Date().toISOString(),
  },
}

// Mock 游戏数据
export const MOCK_GAME = {
  roomId: 'room_001',
  status: 'describing' as const,
  currentRound: 1,
  currentPlayer: 1,
  word: '苹果',
  role: 'civilian' as const,
  players: [
    {
      playerId: 'user_001',
      playerNumber: 1,
      nickname: '测试用户',
      avatar: MOCK_USER.avatar,
      isOwner: true,
      isAlive: true,
      role: 'civilian',
    },
    {
      playerId: 'user_002',
      playerNumber: 2,
      nickname: '玩家2',
      avatar: 'https://mmbiz.qpic.cn/mmbiz/icTdbqWNOwNRna42FI242Lcia07jQodd2FJGIYQfG0LAJGFxM4FbnQP6yfMxBgJ0F3YRqJCJ1aPAK2dQagdusBZg/0',
      isOwner: false,
      isAlive: true,
      role: 'undercover',
    },
    {
      playerId: 'user_003',
      playerNumber: 3,
      nickname: '玩家3',
      avatar: 'https://mmbiz.qpic.cn/mmbiz/icTdbqWNOwNRna42FI242Lcia07jQodd2FJGIYQfG0LAJGFxM4FbnQP6yfMxBgJ0F3YRqJCJ1aPAK2dQagdusBZg/0',
      isOwner: false,
      isAlive: true,
      role: 'civilian',
    },
  ],
  winner: undefined,
  spies: [2],
}

// Mock 词语对
export const MOCK_WORDS = [
  { civilian: '苹果', undercover: '橘子' },
  { civilian: '电脑', undercover: '笔记本' },
  { civilian: '手机', undercover: '平板' },
  { civilian: '咖啡', undercover: '奶茶' },
  { civilian: '篮球', undercover: '足球' },
]

// 生成随机房间号
export function generateRoomCode(): string {
  return String(Math.floor(1000 + Math.random() * 9000))
}

// 生成随机 UUID
export function generateUUID(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0
    const v = c === 'x' ? r : (r & 0x3 | 0x8)
    return v.toString(16)
  })
}
