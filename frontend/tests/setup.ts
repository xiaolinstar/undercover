/**
 * Jest 测试环境设置
 */

// 模拟微信小程序 API
const mockWx = {
  // 存储 API
  setStorageSync: jest.fn(),
  getStorageSync: jest.fn((key: string) => {
    const storage: Record<string, any> = {
      token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoidXNlcl8wMDEiLCJleHAiOjE3NjA0ODA4ODF9.7QZ9c4h8f7g6e5d4c3b2a1",
      openid: 'test_openid',
      user_info: {
        userId: 'user_001',
        openid: 'test_openid',
        nickname: '测试用户',
        avatar: 'https://example.com/avatar.jpg',
      },
    }
    // 如果 key 不存在，返回空字符串而不是 null
    return storage[key] !== undefined ? storage[key] : ''
  }),
  removeStorageSync: jest.fn(),
  clearStorageSync: jest.fn(),
  
  // 登录 API
  login: jest.fn(() => Promise.resolve({ code: 'test_code' })),
  
  // 请求 API
  request: jest.fn((options: any) => {
    return Promise.resolve({
      statusCode: 200,
      data: options.successData || {},
    })
  }),
  
  // WebSocket API
  connectSocket: jest.fn(() => ({
    onOpen: jest.fn(),
    onClose: jest.fn(),
    onError: jest.fn(),
    onMessage: jest.fn(),
    send: jest.fn(),
    close: jest.fn(),
  })),
  
  // UI API
  showToast: jest.fn(),
  showLoading: jest.fn(),
  hideLoading: jest.fn(),
  showModal: jest.fn(),
  navigateTo: jest.fn(),
  navigateBack: jest.fn(),
  reLaunch: jest.fn(),
  setClipboardData: jest.fn(),
  
  // 其他 API
  getSystemInfoSync: jest.fn(() => ({
    model: 'iPhone X',
    pixelRatio: 3,
    windowWidth: 375,
    windowHeight: 812,
  })),
}

// 设置全局 wx 对象
;(global as any).wx = mockWx

// 导出 mock 对象，方便测试使用
export { mockWx }
