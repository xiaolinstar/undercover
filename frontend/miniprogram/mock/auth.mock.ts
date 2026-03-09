/**
 * Mock 认证服务
 */

import { MOCK_TOKEN, MOCK_USER } from './data'

export class MockAuthService {
  /**
   * Mock 登录
   */
  static async login(_code: string): Promise<any> {
    // 模拟网络延迟
    await this.delay(500)
    
    return {
      token: MOCK_TOKEN,
      user: {
        id: MOCK_USER.userId,
        openid: MOCK_USER.openid,
        nickname: MOCK_USER.nickname,
        avatar_url: MOCK_USER.avatar,
        total_games: MOCK_USER.gamesPlayed,
        wins: MOCK_USER.gamesWon
      },
    }
  }

  /**
   * Mock 更新用户信息
   */
  static async updateUserInfo(userInfo: any): Promise<void> {
    await this.delay(300)
    
    // 模拟更新成功
    Object.assign(MOCK_USER, userInfo)
  }

  /**
   * Mock 退出登录
   */
  static async logout(): Promise<void> {
    await this.delay(200)
    
    // 模拟logout成功
    console.log('[MockAuthService] Mock logout成功')
  }

  /**
   * 延迟函数
   */
  private static delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms))
  }
}
