/**
 * 登录页面
 */

import { AuthService } from '../../services/auth.service'

Page({
  data: {
    loading: false,
  },

  onLoad() {
    // 检查是否已登录
    if (AuthService.checkLogin()) {
      this.redirectToHome()
    }
  },

  /**
   * 处理登录
   */
  async handleLogin() {
    this.setData({ loading: true })

    try {
      // 清除旧的 token 和缓存数据
      AuthService.logout()
      console.log('[Login] 已清除旧缓存')
      
      await AuthService.login()
      this.redirectToHome()
    } catch (error: any) {
      console.error('登录失败:', error)
      wx.showToast({
        title: error.message || '登录失败',
        icon: 'none',
      })
    } finally {
      this.setData({ loading: false })
    }
  },

  /**
   * 跳转到首页
   */
  redirectToHome() {
    wx.reLaunch({
      url: '/pages/index/index?from=login',
    })
  },
})
