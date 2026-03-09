# 快速开始指南

本文档将指导您快速开始"谁是卧底"微信小程序客户端的开发。

## 📋 前置准备

### 1. 环境要求

- **微信开发者工具**: 最新稳定版
- **Node.js**: 16+ (可选,用于工具链)
- **服务端**: mp-undercover 项目已部署并运行

### 2. 账号准备

- [ ] 微信小程序 AppID
- [ ] 服务端 API 地址
- [ ] WebSocket 地址

---

## 🚀 第一步: 项目初始化

### 1. 创建项目目录结构

在 `miniprogram/` 目录下创建必要的文件夹:

```bash
cd /Users/xlxing/WeChatProjects/undercover/miniprogram

# 创建目录
mkdir -p pages/login
mkdir -p pages/room
mkdir -p pages/game
mkdir -p pages/profile

mkdir -p components/room-card
mkdir -p components/player-card
mkdir -p components/word-display
mkdir -p components/vote-modal
mkdir -p components/game-status
mkdir -p components/countdown
mkdir -p components/loading

mkdir -p services
mkdir -p utils
mkdir -p models
mkdir -p config
mkdir -p behaviors
mkdir -p assets/images
mkdir -p assets/icons
```

### 2. 更新 app.json

更新 `miniprogram/app.json`:

```json
{
  "pages": [
    "pages/login/login",
    "pages/index/index",
    "pages/room/room",
    "pages/game/game",
    "pages/profile/profile",
    "pages/logs/logs"
  ],
  "window": {
    "navigationBarTextStyle": "black",
    "navigationStyle": "custom",
    "backgroundColor": "#F5F5F5"
  },
  "style": "v2",
  "rendererOptions": {
    "skyline": {
      "defaultDisplayBlock": true,
      "defaultContentBox": true,
      "tagNameStyleIsolation": "legacy",
      "disableABTest": true,
      "sdkVersionBegin": "3.0.0",
      "sdkVersionEnd": "15.255.255"
    }
  },
  "componentFramework": "glass-easel",
  "sitemapLocation": "sitemap.json",
  "lazyCodeLoading": "requiredComponents"
}
```

---

## 🎨 第二步: 创建基础工具类

### 1. 创建配置文件

创建 `miniprogram/config/api.config.ts`:

```typescript
/**
 * API 配置
 */

export const API_CONFIG = {
  // 服务端 API 地址
  BASE_URL: 'https://your-domain.com/api/miniprogram',
  
  // WebSocket 地址
  WS_URL: 'wss://your-domain.com/ws',
  
  // 请求超时时间
  TIMEOUT: 10000,
}

export const API_ENDPOINTS = {
  // 认证相关
  LOGIN: '/auth/login',
  UPDATE_USERINFO: '/auth/update-userinfo',
  
  // 房间相关
  CREATE_ROOM: '/room/create',
  JOIN_ROOM: '/room/join',
  GET_ROOM: '/room/:roomId',
  LEAVE_ROOM: '/room/leave',
  
  // 游戏相关
  START_GAME: '/game/start',
  GET_STATUS: '/game/status',
  VOTE: '/game/vote',
}

export const GAME_CONFIG = {
  MAX_PLAYERS: 12,
  MIN_PLAYERS: 3,
  VOTE_TIME: 30,
  DESCRIBE_TIME: 60,
}
```

### 2. 创建网络请求封装

创建 `miniprogram/utils/request.ts`:

```typescript
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
  private token: string = ''

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
```

### 3. 创建本地存储工具

创建 `miniprogram/utils/storage.ts`:

```typescript
/**
 * 本地存储工具
 */

class Storage {
  /**
   * 设置存储
   */
  set(key: string, value: any): void {
    try {
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
      return wx.getStorageSync(key) || null
    } catch (error) {
      console.error('Storage get error:', error)
      return null
    }
  }

  /**
   * 删除存储
   */
  remove(key: string): void {
    try {
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
```

### 4. 创建常量定义

创建 `miniprogram/utils/constants.ts`:

```typescript
/**
 * 常量定义
 */

// 游戏状态
export enum GameStatus {
  WAITING = 'waiting',
  PLAYING = 'playing',
  FINISHED = 'finished',
}

// 游戏阶段
export enum GamePhase {
  DESCRIBING = 'describing',
  VOTING = 'voting',
  FINISHED = 'finished',
}

// 玩家角色
export enum PlayerRole {
  CIVILIAN = 'civilian',
  SPY = 'spy',
}

// WebSocket 事件
export enum WSEvent {
  // 客户端 -> 服务端
  JOIN_ROOM = 'join_room',
  LEAVE_ROOM = 'leave_room',
  START_GAME = 'start_game',
  VOTE = 'vote',
  
  // 服务端 -> 客户端
  PLAYER_JOINED = 'player_joined',
  PLAYER_LEFT = 'player_left',
  GAME_STARTED = 'game_started',
  GAME_STATUS = 'game_status',
  VOTE_START = 'vote_start',
  VOTE_RESULT = 'vote_result',
  GAME_FINISHED = 'game_finished',
  ERROR = 'error',
}

// 颜色主题
export const COLORS = {
  PRIMARY: '#667eea',
  SUCCESS: '#10b981',
  WARNING: '#f59e0b',
  DANGER: '#ef4444',
  INFO: '#3b82f6',
  TEXT: '#333333',
  TEXT_LIGHT: '#666666',
  TEXT_LIGHTER: '#999999',
  BG: '#F5F5F5',
  WHITE: '#FFFFFF',
  BORDER: '#E5E5E5',
}
```

---

## 🔐 第三步: 创建认证服务

### 1. 创建认证服务

创建 `miniprogram/services/auth.service.ts`:

```typescript
/**
 * 认证服务
 */

import { request } from '../utils/request'
import { storage, STORAGE_KEYS } from '../utils/storage'
import { API_ENDPOINTS } from '../config/api.config'

export interface LoginResult {
  token: string
  openid: string
  userInfo: {
    nickname: string
    avatar: string
  }
}

export interface UserInfo {
  userId: string
  openid: string
  nickname: string
  avatar: string
}

export class AuthService {
  /**
   * 微信登录
   */
  static async login(): Promise<LoginResult> {
    // 获取微信登录 code
    const { code } = await wx.login()
    
    // 发送到服务器
    const result = await request.post<LoginResult>(API_ENDPOINTS.LOGIN, { code })
    
    // 保存 token
    request.setToken(result.token)
    storage.set(STORAGE_KEYS.TOKEN, result.token)
    storage.set(STORAGE_KEYS.OPENID, result.openid)
    storage.set(STORAGE_KEYS.USER_INFO, result.userInfo)
    
    return result
  }

  /**
   * 检查登录状态
   */
  static checkLogin(): boolean {
    const token = storage.get<string>(STORAGE_KEYS.TOKEN)
    if (token) {
      request.setToken(token)
      return true
    }
    return false
  }

  /**
   * 获取用户信息
   */
  static getUserInfo(): UserInfo | null {
    return storage.get<UserInfo>(STORAGE_KEYS.USER_INFO)
  }

  /**
   * 更新用户信息
   */
  static async updateUserInfo(userInfo: Partial<UserInfo>): Promise<void> {
    await request.post(API_ENDPOINTS.UPDATE_USERINFO, userInfo)
    
    // 更新本地存储
    const oldInfo = this.getUserInfo()
    if (oldInfo) {
      storage.set(STORAGE_KEYS.USER_INFO, { ...oldInfo, ...userInfo })
    }
  }

  /**
   * 退出登录
   */
  static logout(): void {
    storage.remove(STORAGE_KEYS.TOKEN)
    storage.remove(STORAGE_KEYS.OPENID)
    storage.remove(STORAGE_KEYS.USER_INFO)
    request.setToken('')
  }
}
```

---

## 📄 第四步: 创建登录页面

### 1. 创建登录页面逻辑

创建 `miniprogram/pages/login/login.ts`:

```typescript
/**
 * 登录页面
 */

import { AuthService } from '../../services/auth.service'

Page({
  data: {
    loading: false,
  },

  onLoad() {
    // 检查是否已登录
    if (AuthService.checkLogin()) {
      this.redirectToHome()
    }
  },

  /**
   * 处理登录
   */
  async handleLogin() {
    this.setData({ loading: true })

    try {
      await AuthService.login()
      this.redirectToHome()
    } catch (error: any) {
      console.error('登录失败:', error)
      wx.showToast({
        title: error.message || '登录失败',
        icon: 'none',
      })
    } finally {
      this.setData({ loading: false })
    }
  },

  /**
   * 跳转到首页
   */
  redirectToHome() {
    wx.reLaunch({
      url: '/pages/index/index',
    })
  },
})
```

### 2. 创建登录页面模板

创建 `miniprogram/pages/login/login.wxml`:

```xml
<view class="login-container">
  <view class="login-header">
    <view class="logo">🎭</view>
    <text class="title">谁是卧底</text>
    <text class="subtitle">聚会桌游</text>
  </view>

  <button 
    class="login-button" 
    bindtap="handleLogin"
    loading="{{loading}}"
    disabled="{{loading}}"
  >
    <text class="button-text">微信登录</text>
  </button>

  <view class="login-footer">
    <text class="footer-text">登录即表示同意用户协议</text>
  </view>
</view>
```

### 3. 创建登录页面样式

创建 `miniprogram/pages/login/login.scss`:

```scss
.login-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  height: 100vh;
  padding: 200rpx 60rpx 100rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-header {
  text-align: center;
  margin-top: 100rpx;
}

.logo {
  font-size: 160rpx;
  margin-bottom: 40rpx;
}

.title {
  display: block;
  font-size: 80rpx;
  font-weight: bold;
  color: #ffffff;
  margin-bottom: 20rpx;
}

.subtitle {
  display: block;
  font-size: 32rpx;
  color: rgba(255, 255, 255, 0.8);
}

.login-button {
  width: 100%;
  height: 88rpx;
  background: #ffffff;
  border-radius: 44rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32rpx;
  font-weight: 500;
  color: #667eea;
  border: none;
  
  &::after {
    border: none;
  }
}

.button-text {
  color: #667eea;
}

.login-footer {
  text-align: center;
}

.footer-text {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.6);
}
```

### 4. 创建登录页面配置

创建 `miniprogram/pages/login/login.json`:

```json
{
  "usingComponents": {},
  "navigationStyle": "custom"
}
```

---

## 🏠 第五步: 更新首页

### 1. 更新首页逻辑

更新 `miniprogram/pages/index/index.ts`:

```typescript
/**
 * 首页 - 游戏大厅
 */

import { AuthService } from '../../services/auth.service'

Page({
  data: {
    userInfo: null as any,
    showJoinModal: false,
    roomCode: '',
  },

  onLoad() {
    // 检查登录状态
    if (!AuthService.checkLogin()) {
      wx.reLaunch({ url: '/pages/login/login' })
      return
    }
    
    // 加载用户信息
    this.loadUserInfo()
  },

  onShow() {
    // 每次显示时刷新用户信息
    this.loadUserInfo()
  },

  /**
   * 加载用户信息
   */
  loadUserInfo() {
    const userInfo = AuthService.getUserInfo()
    this.setData({ userInfo })
  },

  /**
   * 创建房间
   */
  async handleCreateRoom() {
    try {
      wx.showLoading({ title: '创建中...' })
      
      // TODO: 调用创建房间 API
      // const room = await RoomService.createRoom()
      // wx.navigateTo({ url: `/pages/room/room?roomId=${room.roomId}` })
      
      wx.hideLoading()
    } catch (error: any) {
      wx.hideLoading()
      wx.showToast({
        title: error.message || '创建失败',
        icon: 'none',
      })
    }
  },

  /**
   * 显示加入房间弹窗
   */
  handleShowJoinModal() {
    this.setData({ showJoinModal: true })
  },

  /**
   * 隐藏加入房间弹窗
   */
  handleHideJoinModal() {
    this.setData({ showJoinModal: false, roomCode: '' })
  },

  /**
   * 输入房间号
   */
  handleRoomCodeInput(e: any) {
    this.setData({ roomCode: e.detail.value })
  },

  /**
   * 加入房间
   */
  async handleJoinRoom() {
    const { roomCode } = this.data
    
    if (!roomCode || roomCode.length !== 4) {
      wx.showToast({
        title: '请输入4位房间号',
        icon: 'none',
      })
      return
    }

    try {
      wx.showLoading({ title: '加入中...' })
      
      // TODO: 调用加入房间 API
      // const room = await RoomService.joinRoom(roomCode)
      // wx.navigateTo({ url: `/pages/room/room?roomId=${room.roomId}` })
      
      this.handleHideJoinModal()
      wx.hideLoading()
    } catch (error: any) {
      wx.hideLoading()
      wx.showToast({
        title: error.message || '加入失败',
        icon: 'none',
      })
    }
  },

  /**
   * 查看规则
   */
  handleShowRules() {
    wx.showModal({
      title: '游戏规则',
      content: '谁是卧底是一款多人游戏,游戏中平民和卧底会得到相近但不相同的词语。通过描述词语和投票找出卧底!',
      showCancel: false,
    })
  },

  /**
   * 查看个人中心
   */
  handleGoToProfile() {
    wx.navigateTo({ url: '/pages/profile/profile' })
  },
})
```

### 2. 更新首页模板

更新 `miniprogram/pages/index/index.wxml`:

```xml
<view class="index-container">
  <!-- 顶部用户信息 -->
  <view class="header">
    <view class="user-info" bindtap="handleGoToProfile">
      <image class="avatar" src="{{userInfo.avatar || '/assets/images/default-avatar.png'}}" />
      <text class="nickname">{{userInfo.nickname || '微信用户'}}</text>
    </view>
  </view>

  <!-- 主内容区 -->
  <view class="main-content">
    <view class="game-title">
      <text class="title-text">🎭 谁是卧底</text>
      <text class="title-subtitle">聚会桌游</text>
    </view>

    <!-- 操作按钮 -->
    <view class="action-buttons">
      <button class="primary-button" bindtap="handleCreateRoom">
        创建房间
      </button>
      <button class="secondary-button" bindtap="handleShowJoinModal">
        加入房间
      </button>
    </view>

    <!-- 游戏规则 -->
    <view class="rules-section" bindtap="handleShowRules">
      <text class="rules-title">📖 游戏规则</text>
      <text class="rules-desc">点击查看详细规则</text>
    </view>
  </view>

  <!-- 加入房间弹窗 -->
  <view class="modal-mask" wx:if="{{showJoinModal}}" bindtap="handleHideJoinModal">
    <view class="modal-container" catchtap>
      <view class="modal-header">
        <text class="modal-title">加入房间</text>
      </view>
      <view class="modal-body">
        <input 
          class="room-code-input"
          type="number"
          maxlength="4"
          placeholder="请输入4位房间号"
          value="{{roomCode}}"
          bindinput="handleRoomCodeInput"
        />
      </view>
      <view class="modal-footer">
        <button class="cancel-button" bindtap="handleHideJoinModal">取消</button>
        <button class="confirm-button" bindtap="handleJoinRoom">加入</button>
      </view>
    </view>
  </view>
</view>
```

### 3. 更新首页样式

更新 `miniprogram/pages/index/index.scss`:

```scss
.index-container {
  min-height: 100vh;
  background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
  padding: 0 40rpx;
}

.header {
  padding-top: 100rpx;
  padding-bottom: 40rpx;
}

.user-info {
  display: flex;
  align-items: center;
  padding: 20rpx;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50rpx;
}

.avatar {
  width: 60rpx;
  height: 60rpx;
  border-radius: 50%;
  margin-right: 20rpx;
}

.nickname {
  font-size: 28rpx;
  color: #ffffff;
}

.main-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 100rpx;
}

.game-title {
  text-align: center;
  margin-bottom: 100rpx;
}

.title-text {
  display: block;
  font-size: 72rpx;
  font-weight: bold;
  color: #ffffff;
  margin-bottom: 20rpx;
}

.title-subtitle {
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.8);
}

.action-buttons {
  width: 100%;
  margin-bottom: 60rpx;
}

.primary-button,
.secondary-button {
  width: 100%;
  height: 88rpx;
  border-radius: 44rpx;
  font-size: 32rpx;
  font-weight: 500;
  margin-bottom: 30rpx;
  
  &::after {
    border: none;
  }
}

.primary-button {
  background: #ffffff;
  color: #667eea;
}

.secondary-button {
  background: rgba(255, 255, 255, 0.3);
  color: #ffffff;
  border: 2rpx solid rgba(255, 255, 255, 0.5);
}

.rules-section {
  width: 100%;
  padding: 30rpx;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 20rpx;
}

.rules-title {
  display: block;
  font-size: 28rpx;
  color: #ffffff;
  margin-bottom: 10rpx;
}

.rules-desc {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.6);
}

/* 弹窗样式 */
.modal-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-container {
  width: 600rpx;
  background: #ffffff;
  border-radius: 20rpx;
  overflow: hidden;
}

.modal-header {
  padding: 40rpx;
  text-align: center;
  border-bottom: 1rpx solid #e5e5e5;
}

.modal-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333333;
}

.modal-body {
  padding: 40rpx;
}

.room-code-input {
  width: 100%;
  height: 80rpx;
  padding: 0 30rpx;
  background: #f5f5f5;
  border-radius: 10rpx;
  font-size: 32rpx;
  text-align: center;
}

.modal-footer {
  display: flex;
  border-top: 1rpx solid #e5e5e5;
}

.cancel-button,
.confirm-button {
  flex: 1;
  height: 100rpx;
  line-height: 100rpx;
  border: none;
  border-radius: 0;
  font-size: 32rpx;
  
  &::after {
    border: none;
  }
}

.cancel-button {
  background: #ffffff;
  color: #666666;
  border-right: 1rpx solid #e5e5e5;
}

.confirm-button {
  background: #667eea;
  color: #ffffff;
}
```

---

## ✅ 第六步: 配置微信开发者工具

### 1. 导入项目

1. 打开微信开发者工具
2. 选择"导入项目"
3. 选择项目目录: `/Users/xlxing/WeChatProjects/undercover`
4. 填写 AppID
5. 点击"导入"

### 2. 本地开发配置

在微信开发者工具中:

1. 右上角"详情"
2. 本地设置
3. 勾选"不校验合法域名、web-view(业务域名)、TLS 版本以及 HTTPS 证书"

### 3. 编译运行

1. 点击"编译"按钮
2. 查看控制台是否有错误
3. 在模拟器中测试登录功能

---

## 🎯 下一步

恭喜!您已经完成了小程序客户端的基础开发环境搭建。接下来可以:

1. **开发房间功能**: 实现创建房间、加入房间
2. **开发游戏功能**: 实现游戏流程
3. **开发组件**: 创建可复用的 UI 组件
4. **对接服务端**: 与 mp-undercover 服务端对接

## 📚 相关文档

- [架构设计文档](./ARCHITECTURE.md)
- [微信小程序官方文档](https://developers.weixin.qq.com/miniprogram/dev/framework/)

## 💡 开发提示

1. **频繁提交代码**: 每完成一个小功能就提交代码
2. **保持类型安全**: 充分利用 TypeScript 的类型检查
3. **组件化开发**: 提取可复用的组件
4. **查看日志**: 遇到问题先查看控制台日志

## 🐛 常见问题

### Q1: 编译报错"找不到模块"

A: 检查文件路径是否正确,TypeScript 文件是否正确导出

### Q2: 样式不生效

A: 检查 SCSS 语法,确保样式类名与模板匹配

### Q3: API 请求失败

A: 检查服务端是否运行,域名是否正确配置,本地开发是否勾选"不校验合法域名"

### Q4: 登录失败

A: 检查服务端登录接口是否正常,小程序 AppID 是否正确

## 📞 需要帮助?

如果遇到问题,可以:
1. 查看微信小程序官方文档
2. 查看控制台错误日志
3. 在项目 Issues 中提问
