/**
 * 游戏逻辑工具类
 */

import { PlayerInGame, PlayerRole } from '../models/player.model'

export class GameLogic {
  /**
   * 判断游戏是否结束
   */
  static checkGameEnd(players: PlayerInGame[]): {
    ended: boolean
    winner?: PlayerRole
  } {
    const alivePlayers = players.filter(p => p.isAlive)
    const aliveUndercovers = alivePlayers.filter(p => p.role === 'undercover')
    const aliveCivilians = alivePlayers.filter(p => p.role === 'civilian')
    
    // 如果卧底全部被淘汰，平民胜利
    if (aliveUndercovers.length === 0) {
      return { ended: true, winner: 'civilian' }
    }
    
    // 如果卧底人数 >= 平民人数，卧底胜利
    if (aliveUndercovers.length >= aliveCivilians.length) {
      return { ended: true, winner: 'undercover' }
    }
    
    return { ended: false }
  }
  
  /**
   * 投票结果统计
   */
  static countVotes(votes: Record<number, number>): {
    eliminated: number
    voteCounts: Record<number, number>
  } {
    const voteCounts: Record<number, number> = {}
    
    // 统计票数
    Object.values(votes).forEach(target => {
      voteCounts[target] = (voteCounts[target] || 0) + 1
    })
    
    // 找出票数最多的玩家
    let maxVotes = 0
    let eliminated = 0
    
    Object.entries(voteCounts).forEach(([player, count]) => {
      if (count > maxVotes) {
        maxVotes = count
        eliminated = parseInt(player)
      }
    })
    
    return { eliminated, voteCounts }
  }
  
  /**
   * 随机选择卧底
   */
  static selectSpies(playerCount: number, spyCount: number = 1): number[] {
    const indices = Array.from({ length: playerCount }, (_, i) => i)
    const spies: number[] = []
    
    for (let i = 0; i < spyCount; i++) {
      const randomIndex = Math.floor(Math.random() * indices.length)
      spies.push(indices[randomIndex] + 1) // 玩家序号从 1 开始
      indices.splice(randomIndex, 1)
    }
    
    return spies
  }
  
  /**
   * 分配词语和角色
   */
  static assignRoles(
    players: PlayerInGame[],
    _wordPair: { civilian: string; undercover: string },
    spyIndices: number[]
  ): void {
    players.forEach((player, index) => {
      if (spyIndices.includes(index + 1)) {
        player.role = 'undercover'
      } else {
        player.role = 'civilian'
      }
    })
  }
  
  /**
   * 验证房间号
   */
  static validateRoomCode(roomCode: string): boolean {
    return /^\d{4}$/.test(roomCode)
  }
  
  /**
   * 验证玩家数量
   */
  static validatePlayerCount(count: number, min: number = 3, max: number = 12): boolean {
    return count >= min && count <= max
  }
  
  /**
   * 计算胜率
   */
  static calculateWinRate(gamesPlayed: number, gamesWon: number): number {
    if (gamesPlayed === 0) return 0
    return Math.round((gamesWon / gamesPlayed) * 100)
  }
}
