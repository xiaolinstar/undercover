/**
 * 本地存储工具
 */

class Storage {
  /**
   * 设置存储
   */
  set(key: string, value: any): void {
    try {
      // 尝试设置存储，如果失败（如存储系统未初始化），忽略错误
      wx.setStorageSync(key, value)
    } catch (error) {
      console.error('Storage set error:', error)
    }
  }

  /**
   * 获取存储
   */
  get<T = any>(key: string): T | null {
    try {
      // 尝试获取存储，如果失败（如存储系统未初始化），返回null
      return wx.getStorageSync(key) || null
    } catch (error) {
      console.error('Storage get error:', error)
      // 捕获存储系统未初始化的错误，避免程序崩溃
      return null
    }
  }

  /**
   * 删除存储
   */
  remove(key: string): void {
    try {
      // 尝试删除存储，如果失败（如存储系统未初始化），忽略错误
      wx.removeStorageSync(key)
    } catch (error) {
      console.error('Storage remove error:', error)
    }
  }

  /**
   * 清空存储
   */
  clear(): void {
    try {
      // 尝试清空存储，如果失败（如存储系统未初始化），忽略错误
      wx.clearStorageSync()
    } catch (error) {
      console.error('Storage clear error:', error)
    }
  }
}

export const storage = new Storage()

// 存储 Keys
export const STORAGE_KEYS = {
  TOKEN: 'token',
  OPENID: 'openid',
  USER_INFO: 'user_info',
  ROOM_ID: 'room_id',
}
