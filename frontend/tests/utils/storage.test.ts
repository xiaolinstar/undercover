/**
 * Storage 工具类测试
 */

import { storage, STORAGE_KEYS } from '../../miniprogram/utils/storage'

describe('Storage 工具类', () => {
  beforeEach(() => {
    // 清空 mock
    jest.clearAllMocks()
  })
  
  describe('set 方法', () => {
    it('应该成功设置存储', () => {
      const key = 'test_key'
      const value = 'test_value'
      
      storage.set(key, value)
      
      expect(wx.setStorageSync).toHaveBeenCalledWith(key, value)
    })
    
    it('应该能存储对象', () => {
      const key = 'test_object'
      const value = { name: 'test', age: 18 }
      
      storage.set(key, value)
      
      expect(wx.setStorageSync).toHaveBeenCalledWith(key, value)
    })
    
    it('应该能存储数组', () => {
      const key = 'test_array'
      const value = [1, 2, 3]
      
      storage.set(key, value)
      
      expect(wx.setStorageSync).toHaveBeenCalledWith(key, value)
    })
  })
  
  describe('get 方法', () => {
    it('应该能获取存储的值', () => {
      const key = 'token'
      const result = storage.get(key)
      
      expect(result).toBe("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoidXNlcl8wMDEiLCJleHAiOjE3NjA0ODA4ODF9.7QZ9c4h8f7g6e5d4c3b2a1")
    })
    
    it('不存在的 key 应该返回 null', () => {
      const key = 'not_exist'
      const result = storage.get(key)
      
      // storage.get 在找不到 key 时返回 null
      expect(result).toBeNull()
    })
  })
  
  describe('remove 方法', () => {
    it('应该能删除存储', () => {
      const key = 'test_key'
      
      storage.remove(key)
      
      expect(wx.removeStorageSync).toHaveBeenCalledWith(key)
    })
  })
  
  describe('clear 方法', () => {
    it('应该能清空所有存储', () => {
      storage.clear()
      
      expect(wx.clearStorageSync).toHaveBeenCalled()
    })
  })
  
  describe('STORAGE_KEYS 常量', () => {
    it('应该包含所有必需的 key', () => {
      expect(STORAGE_KEYS).toHaveProperty('TOKEN')
      expect(STORAGE_KEYS).toHaveProperty('OPENID')
      expect(STORAGE_KEYS).toHaveProperty('USER_INFO')
      expect(STORAGE_KEYS).toHaveProperty('ROOM_ID')
    })
  })
})
