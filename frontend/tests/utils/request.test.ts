/**
 * Request 工具类测试
 */

import { request } from '../../miniprogram/utils/request'

describe('Request 网络请求工具类', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    // 清除内存中的 token，确保测试隔离
    request.setToken('')
  })
  
  describe('setToken 和 getToken 方法', () => {
    it('应该能设置和获取 token', () => {
      const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoidXNlcl8wMDEiLCJleHAiOjE3NjA0ODA4ODF9.7QZ9c4h8f7g6e5d4c3b2a1"
      request.setToken(token)
      
      expect(request.getToken()).toBe(token)
    })
    
    it('没有设置 token 时应该从 storage 获取', () => {
      const token = request.getToken()
      
      expect(token).toBe("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoidXNlcl8wMDEiLCJleHAiOjE3NjA0ODA4ODF9.7QZ9c4h8f7g6e5d4c3b2a1")
    })
  })
  
  describe('request 方法', () => {
    it('应该发送成功的请求', async () => {
      const mockResponse = { data: 'test' }
      ;(wx.request as jest.Mock).mockImplementation((options: any) => {
        options.success({ statusCode: 200, data: mockResponse })
        return Promise.resolve({ statusCode: 200, data: mockResponse })
      })
      
      const result = await request.request({ url: '/test' })
      
      expect(result).toEqual(mockResponse)
    })
    
    it('应该在请求头中添加 token', async () => {
      const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoidXNlcl8wMDEiLCJleHAiOjE3NjA0ODA4ODF9.7QZ9c4h8f7g6e5d4c3b2a1"
      request.setToken(token)
      let requestHeaders: any = {}
      
      ;(wx.request as jest.Mock).mockImplementation((options: any) => {
        requestHeaders = options.header
        options.success({ statusCode: 200, data: {} })
        return Promise.resolve({ statusCode: 200, data: {} })
      })
      
      await request.request({ url: '/test' })
      
      expect(requestHeaders['Authorization']).toBe(`Bearer ${token}`)
    })
    
    it('401 错误应该触发重新登录', async () => {
      ;(wx.request as jest.Mock).mockImplementation((options: any) => {
        options.success({ statusCode: 401, data: {} })
        return Promise.resolve({ statusCode: 401, data: {} })
      })
      
      await expect(request.request({ url: '/test' })).rejects.toThrow('Token expired')
      
      expect(wx.reLaunch).toHaveBeenCalledWith({ url: '/pages/login/login' })
    })
    
    it('其他错误应该返回错误信息', async () => {
      ;(wx.request as jest.Mock).mockImplementation((options: any) => {
        options.success({ statusCode: 500, data: { error: 'Server Error' } })
        return Promise.resolve({ statusCode: 500, data: { error: 'Server Error' } })
      })
      
      await expect(request.request({ url: '/test' })).rejects.toThrow('Server Error')
    })
    
    it('请求失败应该抛出错误', async () => {
      ;(wx.request as jest.Mock).mockImplementation((options: any) => {
        options.fail(new Error('Network Error'))
        return {} // wx.request 返回 RequestTask，不是 Promise
      })
      
      await expect(request.request({ url: '/test' })).rejects.toThrow('Network Error')
    })
  })
  
  describe('GET 方法', () => {
    it('应该发送 GET 请求', async () => {
      const mockResponse = { data: 'test' }
      ;(wx.request as jest.Mock).mockImplementation((options: any) => {
        expect(options.method).toBe('GET')
        options.success({ statusCode: 200, data: mockResponse })
        return Promise.resolve({ statusCode: 200, data: mockResponse })
      })
      
      const result = await request.get('/test')
      
      expect(result).toEqual(mockResponse)
    })
  })
  
  describe('POST 方法', () => {
    it('应该发送 POST 请求', async () => {
      const mockResponse = { data: 'test' }
      const postData = { name: 'test' }
      
      ;(wx.request as jest.Mock).mockImplementation((options: any) => {
        expect(options.method).toBe('POST')
        expect(options.data).toEqual(postData)
        options.success({ statusCode: 200, data: mockResponse })
        return Promise.resolve({ statusCode: 200, data: mockResponse })
      })
      
      const result = await request.post('/test', postData)
      
      expect(result).toEqual(mockResponse)
    })
  })
})
