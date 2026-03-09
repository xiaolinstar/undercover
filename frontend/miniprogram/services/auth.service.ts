/**
 * 认证服务
 * 实现 IAuthService 接口
 */

import { request } from '../utils/request'
import { storage, STORAGE_KEYS } from '../utils/storage'
import { API_ENDPOINTS, API_CONFIG } from '../config/api.config'
import { MockAuthService } from '../mock/auth.mock'
import { User } from '../models/user.model'
import type { IAuthService, StoredUserInfo } from '../types/auth.interface'
import type { LoginResponse, ApiResponse } from '../types/api.types'

// ============ 数据处理函数 ============

/**
 * 处理登录响应
 */
function processLoginResponse(response: unknown): LoginResponse {
  if (!response) {
    throw new Error('登录响应为空')
  }

  // 处理嵌套结构
  const rawData = (response as { data?: unknown }).data || response
  const data = rawData as LoginResponse

  if (!data.token) {
    console.error('[AuthService] 登录响应缺少 token')
    throw new Error('登录失败：未获取到 token')
  }

  if (!data.user) {
    console.error('[AuthService] 登录响应缺少 user 信息')
    throw new Error('登录失败：未获取到用户信息')
  }

  return data
}

/**
 * 处理用户统计响应
 */
function processUserStatsResponse(response: unknown): User {
  if (!response) {
    throw new Error('用户统计响应为空')
  }

  const rawData = (response as { data?: unknown }).data || response
  const data = rawData as User

  return data
}



// ============ 认证服务实现 ============

/**
 * 认证服务类
 * 实现 IAuthService 接口
 */
export class AuthService implements IAuthService {
  /**
   * 微信登录
   */
  static async login(): Promise<LoginResponse> {
    // Mock 模式
    if (API_CONFIG.USE_MOCK) {
      const { code } = await wx.login()
      const result = await MockAuthService.login(code)

      // 保存 token
      request.setToken(result.token)
      storage.set(STORAGE_KEYS.TOKEN, result.token)
      storage.set(STORAGE_KEYS.OPENID, result.user.openid)
      storage.set(STORAGE_KEYS.USER_INFO, {
        userId: result.user.id,
        openid: result.user.openid,
        nickname: result.user.nickname,
        avatar: result.user.avatar_url
      })

      return result
    }

    // 真实 API 模式
    const { code } = await wx.login()
    console.log('[AuthService] 微信登录 code:', code)

    const response = await request.post<ApiResponse<LoginResponse>>(
      API_ENDPOINTS.LOGIN,
      { code }
    )
    console.log('[AuthService] 登录响应:', JSON.stringify(response, null, 2))

    const loginResp = processLoginResponse(response)
    
    console.log("[AuthService] 登录响应反序列化:", loginResp )
    // 保存 token 和用户信息
      request.setToken(loginResp.token)
      storage.set(STORAGE_KEYS.TOKEN, loginResp.token)
      storage.set(STORAGE_KEYS.OPENID, loginResp.user.openid)
      storage.set(STORAGE_KEYS.USER_INFO, {
        userId: loginResp.user.id,
        openid: loginResp.user.openid,
        nickname: loginResp.user.nickname,
        avatar: loginResp.user.avatar_url
      })

    console.log('[AuthService] Token 已保存:', loginResp.token.substring(0, 20) + '...')

    return loginResp
  }

  /**
   * 检查登录状态
   */
  static checkLogin(): boolean {
    try {
      const token = storage.get<string>(STORAGE_KEYS.TOKEN)
      if (token) {
        request.setToken(token)
        return true
      }
      return false
    } catch (error) {
      console.error('[AuthService] 检查登录状态失败:', error)
      return false
    }
  }

  /**
   * 获取用户信息
   */
  static getUserInfo(): StoredUserInfo | null {
    return storage.get<StoredUserInfo>(STORAGE_KEYS.USER_INFO)
  }

  /**
   * 获取完整用户信息（包含统计数据）
   */
  static async getFullUserInfo(): Promise<User | null> {
    // Mock 模式
    if (API_CONFIG.USE_MOCK) {
      const storedInfo = storage.get<User>(STORAGE_KEYS.USER_INFO)
      if (storedInfo) {
        return storedInfo
      }

      // 返回默认用户数据
      const basicInfo = this.getUserInfo()
      if (basicInfo) {
        return this.createDefaultUser(basicInfo)
      }

      return null
    }

    // 真实 API 模式
    try {
      const response = await request.get<ApiResponse<User>>(
        API_ENDPOINTS.GET_USER_STATS
      )
      return processUserStatsResponse(response)
    } catch (error) {
      console.error('[AuthService] 获取用户统计数据失败:', error)
      // 出错时返回本地存储的信息作为备选
      return storage.get<User>(STORAGE_KEYS.USER_INFO) || null
    }
  }

  /**
   * 更新用户信息
   */
  static async updateUserInfo(userInfo: Partial<StoredUserInfo>): Promise<void> {
    // Mock 模式
    if (API_CONFIG.USE_MOCK) {
      await MockAuthService.updateUserInfo(userInfo)

      // 更新本地存储
      this.updateStoredUserInfo(userInfo)
      return
    }

    // 真实 API 模式
    await request.post<void>(API_ENDPOINTS.UPDATE_USERINFO, userInfo)

    // 更新本地存储
    this.updateStoredUserInfo(userInfo)
  }

  /**
   * 退出登录
   */
  static async logout(): Promise<void> {
    try {
      // 向服务端发送logout请求，使Token失效
      if (API_CONFIG.USE_MOCK) {
        await MockAuthService.logout()
      } else {
        await request.post<void>(API_ENDPOINTS.LOGOUT)
      }
      
      console.log('[AuthService] 服务端logout成功')
    } catch (error) {
      console.warn('[AuthService] 服务端logout失败，但继续清理本地数据:', error)
      // 即使服务端logout失败，也要清理本地数据
    } finally {
      // 无论服务端请求是否成功，都清理本地数据
      storage.remove(STORAGE_KEYS.TOKEN)
      storage.remove(STORAGE_KEYS.OPENID)
      storage.remove(STORAGE_KEYS.USER_INFO)
      request.setToken('')
      
      console.log('[AuthService] 本地数据清理完成')
    }
  }

  // ============ 私有辅助方法 ============

  /**
   * 创建默认用户数据
   */
  private static createDefaultUser(basicInfo: StoredUserInfo): User {
    return {
      userId: basicInfo.userId,
      openid: basicInfo.openid,
      nickname: basicInfo.nickname,
      avatar: basicInfo.avatar,
      gamesPlayed: 0,
      gamesWon: 0,
      createdAt: new Date().toISOString(),
    }
  }

  /**
   * 更新本地存储的用户信息
   */
  private static updateStoredUserInfo(userInfo: Partial<StoredUserInfo>): void {
    const oldInfo = this.getUserInfo()
    if (oldInfo) {
      storage.set(STORAGE_KEYS.USER_INFO, { ...oldInfo, ...userInfo })
    }
  }

  // ============ 实例方法（实现接口） ============

  async login(): Promise<LoginResponse> {
    return AuthService.login()
  }

  checkLogin(): boolean {
    return AuthService.checkLogin()
  }

  getUserInfo(): StoredUserInfo | null {
    return AuthService.getUserInfo()
  }

  async getFullUserInfo(): Promise<User | null> {
    return AuthService.getFullUserInfo()
  }

  async updateUserInfo(userInfo: Partial<StoredUserInfo>): Promise<void> {
    return AuthService.updateUserInfo(userInfo)
  }

  async logout(): Promise<void> {
    return AuthService.logout()
  }
}
