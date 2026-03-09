/**
 * 编辑资料页面
 */

import { AuthService } from '../../../services/auth.service'

Page({
  data: {
    userInfo: {
      nickname: '',
      avatar: ''
    },
    statusBarHeight: 0,
    uploading: false
  },

  onLoad() {
    // 获取状态栏高度
    const systemInfo = wx.getSystemInfoSync()
    this.setData({ statusBarHeight: systemInfo.statusBarHeight || 20 })
    
    // 加载用户信息
    const userInfo = AuthService.getUserInfo()
    if (userInfo) {
      this.setData({
        userInfo: {
          nickname: userInfo.nickname,
          avatar: userInfo.avatar
        }
      })
    }
  },

  /**
   * 输入框改变事件
   */
  onNicknameChange(e: any) {
    const nickname = e.detail.value
    this.setData({
      'userInfo.nickname': nickname
    })
  },

  /**
   * 选择头像
   */
  async onSelectAvatar() {
    this.setData({ uploading: true })
    
    try {
      const result = await wx.chooseImage({
        count: 1,
        sizeType: ['compressed'],
        sourceType: ['album', 'camera']
      })
      
      if (result.tempFilePaths && result.tempFilePaths.length > 0) {
        const tempFilePath = result.tempFilePaths[0]
        
        // 这里应该是上传图片的逻辑
        // 由于目前是mock模式，我们直接使用临时路径
        this.setData({
          'userInfo.avatar': tempFilePath
        })
        
        wx.showToast({
          title: '头像已更新',
          icon: 'success'
        })
      }
    } catch (error) {
      console.error('选择头像失败:', error)
      wx.showToast({
        title: '选择失败',
        icon: 'error'
      })
    } finally {
      this.setData({ uploading: false })
    }
  },

  /**
   * 保存更改
   */
  async onSaveChanges() {
    const { userInfo } = this.data
    
    if (!userInfo.nickname.trim()) {
      wx.showToast({
        title: '请输入昵称',
        icon: 'none'
      })
      return
    }

    wx.showLoading({ title: '保存中...' })

    try {
      // 更新用户信息
      await AuthService.updateUserInfo({
        nickname: userInfo.nickname,
        avatar: userInfo.avatar
      })

      wx.showToast({
        title: '保存成功',
        icon: 'success'
      })

      // 直接返回上一页
      wx.navigateBack()
    } catch (error) {
      console.error('更新用户信息失败:', error)
      wx.showToast({
        title: '保存失败',
        icon: 'error'
      })
    } finally {
      wx.hideLoading()
    }
  },

  /**
   * 返回上一页
   */
  handleGoBack() {
    wx.navigateBack()
  }
})