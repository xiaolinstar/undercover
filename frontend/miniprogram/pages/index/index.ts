/**
 * 首页 - 游戏大厅
 */

import { AuthService } from '../../services/auth.service'
import type { StoredUserInfo } from '../../types/auth.interface'
import { RoomService } from '../../services/room.service'

Page({
  data: {
    userInfo: null as StoredUserInfo | null,
    showJoinModal: false,
    roomCode: '',
    skipAuthCheck: false, // 是否跳过认证检查
  },

  onLoad(options: any) {
    // 检查是否从登录页面跳转过来
    if (options.from === 'login') {
      this.setData({ skipAuthCheck: true })
    }
    
    // 检查登录状态
    // 直接同步执行，依赖Storage工具类的错误处理
    // 如果skipAuthCheck为true，跳过认证检查
    if (!this.data.skipAuthCheck && !AuthService.checkLogin()) {
      wx.redirectTo({ url: '/pages/login/login' }) // 使用redirectTo而不是reLaunch，避免过度跳转
      return
    }
    
    // 加载用户信息
    this.loadUserInfo()
  },

  onShow() {
    // 每次显示时刷新用户信息
    // 检查登录状态，如果不是从登录页跳转过来的，才检查登录状态
    // 直接同步执行，依赖Storage工具类的错误处理
    if (!this.data.skipAuthCheck && AuthService.checkLogin()) {
      this.loadUserInfo()
    }
  },

  /**
   * 加载用户信息
   */
  loadUserInfo() {
    try {
      const userInfo = AuthService.getUserInfo()
      this.setData({ userInfo, skipAuthCheck: false }) // 重置skipAuthCheck标志
    } catch (error) {
      console.error('加载用户信息失败:', error)
    }
  },

  /**
   * 创建房间
   */
  async handleCreateRoom() {
    try {
      wx.showLoading({ title: '创建中...' })
      
      const room = await RoomService.createRoom()
      
      console.log("[RoomService 创建房间]: ", room)
      wx.hideLoading()
      wx.navigateTo({ url: `/pages/room/room?roomId=${room.roomId}&roomCode=${room.roomCode}` })

    } catch (error: any) {
      wx.hideLoading()
      wx.showToast({
        title: error.message || '创建失败',
        icon: 'none',
      })
    }
  },

  /**
   * 显示加入房间弹窗
   */
  handleShowJoinModal() {
    this.setData({ showJoinModal: true })
  },

  /**
   * 隐藏加入房间弹窗
   */
  handleHideJoinModal() {
    this.setData({ showJoinModal: false, roomCode: '' })
  },

  /**
   * 输入房间号
   */
  handleRoomCodeInput(e: any) {
    this.setData({ roomCode: e.detail.value })
  },

  /**
   * 加入房间
   */
  async handleJoinRoom() {
    const { roomCode } = this.data
    
    if (!roomCode || roomCode.length !== 4) {
      wx.showToast({
        title: '请输入4位房间号',
        icon: 'none',
      })
      return
    }

    try {
      wx.showLoading({ title: '加入中...' })
      
      const room = await RoomService.joinRoom(roomCode)
      
      this.handleHideJoinModal()
      wx.hideLoading()
      wx.navigateTo({ url: `/pages/room/room?roomId=${room.roomId}&roomCode=${room.roomCode}` })
    } catch (error: any) {
      wx.hideLoading()
      wx.showToast({
        title: error.message || '加入失败',
        icon: 'none',
      })
    }
  },

  /**
   * 查看规则
   */
  handleShowRules() {
    wx.showModal({
      title: '游戏规则',
      content: '谁是卧底是一款多人游戏,游戏中平民和卧底会得到相近但不相同的词语。通过描述词语和投票找出卧底!',
      showCancel: false,
    })
  },

  /**
   * 查看个人中心
   */
  handleGoToProfile() {
    wx.navigateTo({ url: '/pages/profile/profile' })
  },

})
