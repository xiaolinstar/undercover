// app.ts
App<IAppOption>({
  globalData: {},

  onLaunch() {
    console.log('[App] 小程序启动')
    // 登录逻辑在 pages/login/login.ts 中处理
    // 静默登录检查：login.ts 的 onLoad 会检查 token 状态
  },
})