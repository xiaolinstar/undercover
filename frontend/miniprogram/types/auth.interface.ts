/**
 * 服务接口定义
 * 设计与实现分离，提高代码可读性
 */

import type {
  LoginResponse,
} from './api.types'
import type { User } from '../models/user.model'

/**
 * 存储中的用户信息
 */
export interface StoredUserInfo {
  userId: string
  openid: string
  nickname: string
  avatar: string
}

/**
 * 认证服务接口
 */
export interface IAuthService {
  /**
   * 微信登录
   */
  login(): Promise<LoginResponse>

  /**
   * 检查登录状态
   */
  checkLogin(): boolean

  /**
   * 获取用户信息
   */
  getUserInfo(): StoredUserInfo | null

  /**
   * 获取完整用户信息（包含统计数据）
   */
  getFullUserInfo(): Promise<User | null>

  /**
   * 更新用户信息
   */
  updateUserInfo(userInfo: Partial<StoredUserInfo>): Promise<void>

  /**
   * 退出登录
   */
  logout(): Promise<void>
}
