/**
 * Mock 游戏服务
 */

import { MOCK_GAME, MOCK_WORDS } from './data'

export class MockGameService {
  /**
   * Mock 开始游戏
   */
  static async startGame(_roomId: string): Promise<any> {
    await this.delay(500)
    
    const playerCount = MOCK_GAME.players.length
    
    // 根据玩家数量确定卧底数量
    let spyCount: number
    if (playerCount <= 4) {
      spyCount = 1
    } else if (playerCount <= 8) {
      spyCount = 2
    } else {
      spyCount = 3
    }
    
    // 随机选择词语对
    const wordPair = MOCK_WORDS[Math.floor(Math.random() * MOCK_WORDS.length)]
    
    // 随机选择卧底
    const spyIndices: number[] = []
    while (spyIndices.length < spyCount) {
      const randomIndex = Math.floor(Math.random() * playerCount)
      if (!spyIndices.includes(randomIndex)) {
        spyIndices.push(randomIndex)
      }
    }
    
    // 分配词语和角色
    MOCK_GAME.players.forEach((player, index) => {
      if (spyIndices.includes(index)) {
        player.role = 'undercover'
      } else {
        player.role = 'civilian'
      }
    })
    
    // 设置当前玩家的词语和角色
    const currentPlayer = MOCK_GAME.players[0] // 假设当前用户是第一个玩家
    MOCK_GAME.word = currentPlayer.role === 'undercover' ? wordPair.undercover : wordPair.civilian
    MOCK_GAME.role = currentPlayer.role as any
    MOCK_GAME.spies = spyIndices.map(index => index + 1)
    
    MOCK_GAME.status = 'describing'
    MOCK_GAME.currentRound = 1
    MOCK_GAME.currentPlayer = 1
    
    console.log(`[MockGameService] 游戏开始 - 玩家数: ${playerCount}, 卧底数: ${spyCount}`)
    
    return MOCK_GAME
  }

  /**
   * Mock 获取游戏状态
   */
  static async getGameStatus(_roomId: string): Promise<any> {
    await this.delay(300)
    
    return MOCK_GAME
  }

  /**
   * Mock 投票
   */
  static async vote(_roomId: string, targetPlayer: number): Promise<any> {
    await this.delay(500)
    
    // 模拟投票结果
    const targetPlayerData = MOCK_GAME.players.find(p => p.playerNumber === targetPlayer)
    
    if (!targetPlayerData) {
      throw new Error('玩家不存在')
    }
    
    // 标记玩家为淘汰
    targetPlayerData.isAlive = false
    
    // 检查游戏是否结束
    const alivePlayers = MOCK_GAME.players.filter(p => p.isAlive)
    const aliveSpies = alivePlayers.filter(p => p.role === 'spy')
    const aliveCivilians = alivePlayers.filter(p => p.role === 'civilian')
    
    let gameEnded = false
    let winner: 'civilian' | 'spy' | undefined
    
    if (aliveSpies.length === 0) {
      // 平民胜利
      gameEnded = true
      winner = 'civilian'
      ;(MOCK_GAME as any).status = 'finished'
      ;(MOCK_GAME as any).winner = 'civilian'
    } else if (aliveSpies.length >= aliveCivilians.length) {
      // 卧底胜利
      gameEnded = true
      winner = 'spy'
      ;(MOCK_GAME as any).status = 'finished'
      ;(MOCK_GAME as any).winner = 'spy'
    }
    
    return {
      eliminated: targetPlayer,
      isSpy: targetPlayerData.role === 'spy',
      gameEnded,
      winner,
    }
  }

  /**
   * 延迟函数
   */
  private static delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms))
  }
}
