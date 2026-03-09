/**
 * 游戏进行页
 */

import { wsService } from '../../services/websocket.service'
import { storage } from '../../utils/storage'
import { Player } from '../../models/player.model'



Page({
  data: {
    // 房间信息
    roomId: '',
    roomCode: '',
    
    // 游戏状态
    gameStatus: 'describing' as 'describing' | 'voting' | 'finished',
    currentRound: 1,
    countdown: 0,
    
    // 玩家信息
    word: '',
    role: '' as 'civilian' | 'undercover' | '',
    players: [] as Player[],
    currentPlayerId: '',
    currentPlayerNumber: 0,
    alivePlayersCount: 0,
    totalPlayersCount: 0,
    alivePlayers: [] as Player[],
    
    // 游戏结果
    winner: '' as 'civilian' | 'undercover' | '',
    words: { civilian: '', undercover: '' },
    
    // UI 状态
    showWord: false,
    showVoteModal: false,
    selectedPlayerId: '',
    voteCounts: {} as Record<string, number>,
    hasVoted: false,
    
    // 描述环节
    currentSpeakerNumber: 0,
    speakingPlayerId: '',
    descriptions: [] as { playerNumber: number; nickname: string; description: string }[],
    showDescriptionInput: false,
    descriptionText: '',
    
    // 动画状态
    showResultAnimation: false,
    eliminatedPlayerNumber: 0,
  },

  onLoad(options: Record<string, string | undefined>) {
    const roomId = options.roomId
    const roomCode = options.roomCode
    
    if (!roomId) {
      wx.showToast({
        title: '房间信息错误',
        icon: 'error'
      })
      setTimeout(function() {
        wx.navigateBack()
      }, 1500)
      return
    }
    
    this.setData({ roomId, roomCode })
    
    // 获取当前玩家信息
    const userInfo = storage.get<any>('user_info')
    if (userInfo && userInfo.userId) {
      this.setData({ currentPlayerId: userInfo.userId })
    }
    
    // 加载游戏信息
    this.loadGameInfo()
    
    // 监听 WebSocket 事件
    this.setupWebSocketListeners()
  },

  onUnload() {
    // 移除 WebSocket 监听
    wsService.leaveRoom()
  },

  /**
   * 设置 WebSocket 监听器
   */
  setupWebSocketListeners() {
    // 监听游戏开始
    wsService.onGameStart((data) => {
      const alivePlayers = data.players.filter((p: any) => p.isAlive !== false)
      const alivePlayersCount = alivePlayers.length
      const totalPlayersCount = data.players.length
      
      this.setData({
        word: data.word,
        role: data.role,
        players: data.players,
        gameStatus: 'describing',
        alivePlayers,
        alivePlayersCount,
        totalPlayersCount,
        descriptions: [],
        hasVoted: false,
        showWord: false,
      })
    })
    
    // 监听游戏阶段变化
    wsService.onGamePhaseChange((data) => {
      this.setData({
        gameStatus: data.phase,
        currentRound: data.round,
        countdown: data.countdown || 0,
        currentSpeakerNumber: data.currentPlayerNumber || 0,
      })
      
      // 进入投票环节
      if (data.phase === 'voting') {
        this.setData({ 
          showVoteModal: true,
          hasVoted: false,
        })
      }
      
      // 描述环节开始
      if (data.phase === 'describing' && data.currentPlayerNumber) {
        this.checkIfMyTurn(data.currentPlayerNumber)
      }
    })
    
    // 监听玩家投票
    wsService.onPlayerVote((data) => {
      this.setData({
        voteCounts: data.voteCounts,
      })
    })
    
    // 监听游戏结束
    wsService.onGameEnd((data) => {
      const alivePlayers = data.players.filter((p: any) => p.isAlive !== false)
      const alivePlayersCount = alivePlayers.length
      const totalPlayersCount = data.players.length
      
      this.setData({
        gameStatus: 'finished',
        winner: data.winner,
        words: data.words,
        players: data.players,
        alivePlayers,
        alivePlayersCount,
        totalPlayersCount,
        showResultAnimation: true,
      })
      
      // 3秒后关闭动画
      setTimeout(() => {
        this.setData({ showResultAnimation: false })
      }, 3000)
    })
    
    // 监听玩家消息（描述）
    wsService.onPlayerMessage((data) => {
      // 添加描述到列表
      const player = this.data.players.find((p: Player) => p.playerId === data.playerId)
      if (player) {
        const descriptions = [...this.data.descriptions, {
          playerNumber: player.playerNumber,
          nickname: player.nickname,
          description: data.message,
        }]
        this.setData({ descriptions })
      }
    })
    
    // 监听系统消息
    wsService.onSystemMessage((data) => {
      wx.showToast({
        title: data.message,
        icon: 'none',
      })
      
      // 玩家被淘汰消息
      if (data.type === 'warning' && data.message.includes('淘汰')) {
        // 提取玩家序号
        const match = data.message.match(/(\d+)号/)
        if (match) {
          this.setData({ 
            eliminatedPlayerNumber: parseInt(match[1]),
          })
          // 动画后重置
          setTimeout(() => {
            this.setData({ eliminatedPlayerNumber: 0 })
          }, 2000)
        }
      }
    })
  },

  /**
   * 检查是否轮到自己发言
   */
  checkIfMyTurn(speakerNumber: number) {
    const currentPlayer = this.data.players.find(
      (p: Player) => p.playerId === this.data.currentPlayerId
    )
    
    if (currentPlayer && currentPlayer.playerNumber === speakerNumber) {
      // 轮到自己发言
      this.setData({ showDescriptionInput: true })
    } else {
      this.setData({ showDescriptionInput: false })
    }
  },

  /**
   * 加载游戏信息
   */
  async loadGameInfo() {
    try {
      const { GameService } = require('../../services/game.service')
      const game = await GameService.getGameStatus(this.data.roomId)
      
      const alivePlayers = game.players.filter((p: any) => p.isAlive !== false)
      const alivePlayersCount = alivePlayers.length
      const totalPlayersCount = game.players.length
      
      this.setData({
        gameStatus: game.status,
        currentRound: game.currentRound,
        word: game.word || '',
        role: game.role || '',
        players: game.players,
        winner: game.winner || '',
        alivePlayers,
        alivePlayersCount,
        totalPlayersCount,
      })
      
      // 如果正在描述环节，检查是否轮到自己
      if (game.status === 'describing' && game.currentPlayerNumber) {
        this.checkIfMyTurn(game.currentPlayerNumber)
      }
    } catch (error: any) {
      console.error('加载游戏信息失败:', error)
      wx.showToast({
        title: error.message || '加载失败',
        icon: 'none',
      })
    }
  },

  /**
   * 展示词语
   */
  handleShowWord() {
    this.setData({ showWord: true })
  },

  /**
   * 输入描述
   */
  handleDescriptionInput(e: { detail: { value: string } }) {
    this.setData({ descriptionText: e.detail.value })
  },

  /**
   * 提交描述
   */
  async handleSubmitDescription() {
    const { descriptionText } = this.data
    
    if (!descriptionText.trim()) {
      wx.showToast({
        title: '请输入描述内容',
        icon: 'none',
      })
      return
    }
    
    try {
      await wsService.sendPlayerMessage(descriptionText)
      
      this.setData({
        descriptionText: '',
        showDescriptionInput: false,
      })
      
      wx.showToast({
        title: '发言成功',
        icon: 'success',
      })
    } catch (error: any) {
      wx.showToast({
        title: error.message || '发言失败',
        icon: 'none',
      })
    }
  },

  /**
   * 跳过描述
   */
  handleSkipDescription() {
    this.setData({
      descriptionText: '',
      showDescriptionInput: false,
    })
  },

  /**
   * 确认投票
   */
  async handleVoteConfirm(e: { detail: { playerId: string } }) {
    const { playerId } = e.detail
    
    try {
      wx.showLoading({ title: '投票中...' })
      
      const { GameService } = require('../../services/game.service')
      await GameService.vote(this.data.roomId, playerId)
      
      wx.hideLoading()
      this.setData({ 
        showVoteModal: false,
        selectedPlayerId: playerId,
        hasVoted: true,
      })
      
      wx.showToast({
        title: '投票成功',
        icon: 'success',
      })
    } catch (error: any) {
      wx.hideLoading()
      wx.showToast({
        title: error.message || '投票失败',
        icon: 'none',
      })
    }
  },

  /**
   * 取消投票
   */
  handleVoteCancel() {
    this.setData({ showVoteModal: false })
  },

  /**
   * 返回首页
   */
  handleBackToHome() {
    wx.showModal({
      title: '提示',
      content: '确定要退出游戏吗？',
      success: (res) => {
        if (res.confirm) {
          wsService.leaveRoom()
          wx.reLaunch({ url: '/pages/index/index' })
        }
      },
    })
  },

  /**
   * 再来一局
   */
  handlePlayAgain() {
    wx.navigateBack({ delta: 1 })
  },
})
