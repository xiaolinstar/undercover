/**
 * 用户模型
 */

export interface User {
  userId: string
  openid: string
  nickname: string
  avatar: string
  gamesPlayed: number
  gamesWon: number
  createdAt: string
}
