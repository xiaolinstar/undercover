/**
 * AuthService 认证服务测试
 */

import { AuthService } from '../../miniprogram/services/auth.service'
import { storage, STORAGE_KEYS } from '../../miniprogram/utils/storage'
import { request } from '../../miniprogram/utils/request'

// Mock 依赖
jest.mock('../../miniprogram/utils/request')
jest.mock('../../miniprogram/utils/storage')

describe('AuthService 认证服务', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })
  
  describe('checkLogin 方法', () => {
    it('有 token 时应该返回 true', () => {
      ;(storage.get as jest.Mock).mockReturnValue('test_token')
      
      const result = AuthService.checkLogin()
      
      expect(result).toBe(true)
      expect(storage.get).toHaveBeenCalledWith(STORAGE_KEYS.TOKEN)
    })
    
    it('没有 token 时应该返回 false', () => {
      ;(storage.get as jest.Mock).mockReturnValue(null)
      
      const result = AuthService.checkLogin()
      
      expect(result).toBe(false)
    })
  })
  
  describe('getUserInfo 方法', () => {
    it('应该返回用户信息', () => {
      const mockUserInfo = {
        userId: 'user_001',
        openid: 'test_openid',
        nickname: '测试用户',
        avatar: 'https://example.com/avatar.jpg',
      }
      ;(storage.get as jest.Mock).mockReturnValue(mockUserInfo)
      
      const result = AuthService.getUserInfo()
      
      expect(result).toEqual(mockUserInfo)
      expect(storage.get).toHaveBeenCalledWith(STORAGE_KEYS.USER_INFO)
    })
    
    it('没有用户信息时应该返回 null', () => {
      ;(storage.get as jest.Mock).mockReturnValue(null)
      
      const result = AuthService.getUserInfo()
      
      expect(result).toBeNull()
    })
  })
  
  describe('logout 方法', () => {
    it('应该清除所有登录信息', () => {
      AuthService.logout()
      
      expect(storage.remove).toHaveBeenCalledWith(STORAGE_KEYS.TOKEN)
      expect(storage.remove).toHaveBeenCalledWith(STORAGE_KEYS.OPENID)
      expect(storage.remove).toHaveBeenCalledWith(STORAGE_KEYS.USER_INFO)
      expect(request.setToken).toHaveBeenCalledWith('')
    })
  })
})
