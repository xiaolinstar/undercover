/**
 * 网络请求封装
 */

import { API_CONFIG } from '../config/api.config'

interface RequestOptions {
  url: string
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  data?: any
  header?: Record<string, string>
}

class Request {
  private token: string

  constructor() {
    this.token = ''
  }

  /**
   * 设置 Token
   */
  setToken(token: string): void {
    this.token = token
  }

  /**
   * 获取 Token
   */
  getToken(): string {
    return this.token || wx.getStorageSync('token') || ''
  }

  /**
   * 发起请求
   */
  async request<T = any>(options: RequestOptions): Promise<T> {
    const { url, method = 'GET', data, header = {} } = options
    const token = this.getToken()

    // 添加 token
    if (token) {
      header['Authorization'] = `Bearer ${token}`
    }

    return new Promise((resolve, reject) => {
      wx.request({
        url: `${API_CONFIG.BASE_URL}${url}`,
        method,
        data,
        header: {
          'Content-Type': 'application/json',
          ...header,
        },
        timeout: API_CONFIG.TIMEOUT,
        success: (res: any) => {
          if (res.statusCode === 200) {
            resolve(res.data)
          } else if (res.statusCode === 401) {
            // token 过期,重新登录
            this.handleTokenExpired()
            reject(new Error('Token expired'))
          } else {
            reject(new Error(res.data.error || 'Request failed'))
          }
        },
        fail: (err) => {
          reject(err)
        },
      })
    })
  }

  /**
   * 处理 Token 过期
   */
  private handleTokenExpired(): void {
    this.token = ''
    wx.removeStorageSync('token')
    
    // 跳转到登录页
    wx.reLaunch({
      url: '/pages/login/login',
    })
  }

  /**
   * GET 请求
   */
  get<T = any>(url: string, data?: any): Promise<T> {
    return this.request({ url, method: 'GET', data })
  }

  /**
   * POST 请求
   */
  post<T = any>(url: string, data?: any): Promise<T> {
    return this.request({ url, method: 'POST', data })
  }
}

export const request = new Request()
