/**
 * 房间页面
 */

import { RoomService } from '../../services/room.service'
import { wsService } from '../../services/websocket.service'
import { Player } from '../../models/player.model'



Page({
  data: {
    roomId: '',
    roomCode: '',
    players: [] as Player[],
    ownerId: '',
    status: 'waiting', // waiting, playing, finished
    maxPlayers: 0,
    loading: false,
    error: '',
    showInviteModal: false,
    inviteLink: '',
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
    
    // 加载房间信息
    this.loadRoomInfo()
    
    // 加入房间
    this.joinRoom()
    
    // 监听 WebSocket 事件
    this.setupWebSocketListeners()
  },

  onUnload() {
    // 移除 WebSocket 监听
    this.cleanupWebSocketListeners()
  },

  /**
   * 设置 WebSocket 监听器
   */
  setupWebSocketListeners() {
    // 监听房间更新
    wsService.onRoomUpdate((data: any) => {
      this.setData({
        players: data.players,
        status: data.status,
      })
    })

    // 监听玩家加入
    wsService.onPlayerJoin((data: any) => {
      wx.showToast({
        title: data.player.nickname + ' 加入了房间',
        icon: 'none',
      })
    })

    // 监听玩家离开
    wsService.onPlayerLeave(() => {
      wx.showToast({
        title: '有玩家离开了房间',
        icon: 'none',
      })
    })

    // 监听系统消息
    wsService.onSystemMessage((data: any) => {
      wx.showToast({
        title: data.message,
        icon: 'none',
      })
    })
  },

  /**
   * 清理 WebSocket 监听器
   */
  cleanupWebSocketListeners() {
    // 实际上我们不应该在这里移除全局监听器
    // 因为这些监听器可能在其他地方还在使用
    // 这里仅作示意，实际实现需要根据具体需求调整
  },

  /**
   * 加载房间信息
   */
  async loadRoomInfo() {
    this.setData({ loading: true })
    
    try {
      const room = await RoomService.getRoom(this.data.roomId)
      
      this.setData({
        players: room.players || [],
        ownerId: room.ownerId,
        status: room.status,
        maxPlayers: room.maxPlayers,
        loading: false,
      })
    } catch (error: any) {
      console.error('加载房间信息失败:', error)
      this.setData({
        error: error.message,
        loading: false,
      })
      wx.showToast({
        title: '加载房间失败',
        icon: 'error',
      })
    }
  },

  /**
   * 加入房间
   */
  async joinRoom() {
    try {
      await wsService.joinRoom(this.data.roomId)
    } catch (error: any) {
      console.error('加入房间失败:', error)
      wx.showToast({
        title: '加入房间失败',
        icon: 'error',
      })
    }
  },

  /**
   * 开始游戏
   */
  async handleStartGame() {
    if (this.data.players.length < 3) {
      wx.showToast({
        title: '至少需要3人才能开始游戏',
        icon: 'none',
      })
      return
    }

    this.setData({ loading: true })

    try {
      const { GameService } = require('../../services/game.service')
      await GameService.startGame(this.data.roomId)
      
      wx.showToast({
        title: '游戏开始！',
        icon: 'success',
      })

      // 跳转到游戏页面
      wx.navigateTo({
        url: '/pages/game/game?roomId=' + this.data.roomId + '&roomCode=' + this.data.roomCode,
      })
    } catch (error: any) {
      console.error('开始游戏失败:', error)
      wx.showToast({
        title: error.message || '开始游戏失败',
        icon: 'none',
      })
    } finally {
      this.setData({ loading: false })
    }
  },

  /**
   * 复制房间号
   */
  handleCopyRoomCode() {
    wx.setClipboardData({
      data: this.data.roomCode,
      success: function() {
        wx.showToast({
          title: '房间号已复制',
          icon: 'success',
        })
      },
    })
  },

  /**
   * 显示邀请模态框
   */
  handleShowInviteModal() {
    this.setData({
      inviteLink: 'https://your-app-domain.com/join-room?code=' + this.data.roomCode,
      showInviteModal: true,
    })
  },

  /**
   * 隐藏邀请模态框
   */
  handleHideInviteModal() {
    this.setData({
      showInviteModal: false,
    })
  },

  /**
   * 离开房间
   */
  handleLeaveRoom() {
    const self = this
    wx.showModal({
      title: '提示',
      content: '确定要离开房间吗？',
      success: function(res) {
        if (res.confirm) {
          self.doLeaveRoom()
        }
      },
    })
  },
  
  async doLeaveRoom() {
    try {
      await RoomService.leaveRoom(this.data.roomId)
      
      // 返回首页
      wx.reLaunch({
        url: '/pages/index/index',
      })
    } catch (error: any) {
      console.error('离开房间失败:', error)
      wx.showToast({
        title: error.message || '离开房间失败',
        icon: 'none',
      })
    }
  },

  /**
   * 刷新房间信息
   */
  async handleRefresh() {
    await this.loadRoomInfo()
  },
})
