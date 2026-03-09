/**
 * AuthService 完整测试（包括登录流程）
 */

import { AuthService } from '../../miniprogram/services/auth.service'
import { storage, STORAGE_KEYS } from '../../miniprogram/utils/storage'
import { request } from '../../miniprogram/utils/request'

// Mock 依赖
jest.mock('../../miniprogram/utils/request')
jest.mock('../../miniprogram/utils/storage')
jest.mock('../../miniprogram/config/api.config', () => ({
  API_CONFIG: {
    USE_MOCK: false,
    BASE_URL: 'https://test.com/api',
    TIMEOUT: 10000,
  },
  API_ENDPOINTS: {
    LOGIN: '/auth/login',
    UPDATE_USERINFO: '/auth/update-userinfo',
  },
}))

describe('AuthService 认证服务完整测试', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })
  
  describe('login 方法（真实 API 模式）', () => {
    it('应该成功登录并保存 token', async () => {
      const mockLoginResult = {
        token: 'test_token_123',
        user: {
          id: 'user_test_c',
          openid: 'test_openid',
          nickname: '测试用户',
          avatar_url: 'https://example.com/avatar.jpg',
          total_games: 0,
          wins: 0
        },
      }
      ;(request.post as jest.Mock).mockResolvedValue(mockLoginResult)
      
      const result = await AuthService.login()
      
      expect(result).toEqual(mockLoginResult)
      expect(request.setToken).toHaveBeenCalledWith('test_token_123')
      expect(storage.set).toHaveBeenCalledWith(STORAGE_KEYS.TOKEN, 'test_token_123')
      expect(storage.set).toHaveBeenCalledWith(STORAGE_KEYS.OPENID, 'test_openid')
    })
  })
  
  describe('updateUserInfo 方法（真实 API 模式）', () => {
    it('应该成功更新用户信息', async () => {
      const oldInfo = {
        userId: 'user_001',
        openid: 'test_openid',
        nickname: '旧昵称',
        avatar: 'https://example.com/old.jpg',
      }
      const newInfo = {
        nickname: '新昵称',
        avatar: 'https://example.com/new.jpg',
      }
      
      ;(storage.get as jest.Mock).mockReturnValue(oldInfo)
      ;(request.post as jest.Mock).mockResolvedValue(undefined)
      
      await AuthService.updateUserInfo(newInfo)
      
      expect(request.post).toHaveBeenCalledWith('/auth/update-userinfo', newInfo)
      expect(storage.set).toHaveBeenCalledWith(STORAGE_KEYS.USER_INFO, {
        ...oldInfo,
        ...newInfo,
      })
    })
  })
})
