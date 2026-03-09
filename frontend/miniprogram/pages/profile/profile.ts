/**
 * 个人中心
 */

import { AuthService } from '../../services/auth.service'
import type { StoredUserInfo } from '../../types/auth.interface'

Page({
  data: {
    userInfo: null as StoredUserInfo | null,
    gamesPlayed: 0,
    gamesWon: 0,
    winRate: 0,
    loading: true,
  },

  onLoad() {
    // 直接同步执行，依赖Storage工具类的错误处理
    this.loadUserInfo()
  },

  onShow() {
    // 直接同步执行，依赖Storage工具类的错误处理
    this.loadUserInfo()
  },

  /**
   * 加载用户信息
   */
  async loadUserInfo() {
    this.setData({ loading: true })
    
    try {
      const userInfo = AuthService.getUserInfo()
      
      if (!userInfo) {
        wx.showToast({
          title: '请先登录',
          icon: 'none'
        })
        setTimeout(function() {
          wx.reLaunch({ url: '/pages/login/login' })
        }, 1500)
        return
      }
      
      this.setData({
        userInfo: userInfo,
        gamesPlayed: 0,
        gamesWon: 0,
        winRate: 0,
        loading: false
      })
    } catch (error) {
      console.error('加载用户信息失败:', error)
      wx.showToast({
        title: '加载失败',
        icon: 'error'
      })
      this.setData({ loading: false })
    }
  },

  /**
   * 返回上一页
   */
  handleGoBack() {
    const pages = getCurrentPages()
    if (pages.length > 1) {
      wx.navigateBack()
    } else {
      wx.reLaunch({ url: '/pages/index/index' })
    }
  },

  /**
   * 退出登录
   */
  handleLogout() {
    wx.showModal({
      title: '提示',
      content: '确定要退出登录吗?',
      success: function(res) {
        if (res.confirm) {
          AuthService.logout()
          wx.reLaunch({ url: '/pages/login/login' })
        }
      },
    })
  },
})
