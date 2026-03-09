/**
 * 房间模型
 */

import { Player } from './player.model'

export interface Room {
  roomId: string
  roomCode: string // 房间标识短号：4位
  ownerId: string
  players: Player[]
  maxPlayers: number
  status: 'waiting' | 'playing' | 'finished'
  createdAt: string
}
