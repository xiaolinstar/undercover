/**
 * 游戏历史页面
 */

Page({
  data: {
    gameHistory: [] as any[],
    statusBarHeight: 0,
    loading: true,
    currentPage: 1,
    hasMore: true
  },

  onLoad() {
    // 获取状态栏高度
    const systemInfo = wx.getSystemInfoSync()
    this.setData({ statusBarHeight: systemInfo.statusBarHeight || 20 })
    
    // 加载游戏历史
    this.loadGameHistory()
  },

  /**
   * 加载游戏历史
   */
  async loadGameHistory() {
    this.setData({ loading: true })
    
    try {
      // 模拟加载游戏历史数据
      // 在实际应用中，这里应该调用API获取真实的游戏历史数据
      const mockHistory = [
        {
          id: 1,
          date: '2024-01-15',
          result: '胜利',
          role: '平民',
          word: '苹果',
          duration: '15分钟',
          players: 8
        },
        {
          id: 2,
          date: '2024-01-14',
          result: '失败',
          role: '卧底',
          word: '橘子',
          duration: '12分钟',
          players: 6
        },
        {
          id: 3,
          date: '2024-01-12',
          result: '胜利',
          role: '平民',
          word: '电脑',
          duration: '18分钟',
          players: 10
        },
        {
          id: 4,
          date: '2024-01-10',
          result: '失败',
          role: '卧底',
          word: '笔记本',
          duration: '14分钟',
          players: 7
        },
        {
          id: 5,
          date: '2024-01-08',
          result: '胜利',
          role: '平民',
          word: '手机',
          duration: '16分钟',
          players: 9
        }
      ]

      this.setData({
        gameHistory: mockHistory,
        loading: false
      })
    } catch (error) {
      console.error('加载游戏历史失败:', error)
      wx.showToast({
        title: '加载失败',
        icon: 'error'
      })
      this.setData({ loading: false })
    }
  },

  /**
   * 返回上一页
   */
  handleGoBack() {
    wx.navigateBack()
  },

  /**
   * 下拉刷新
   */
  onPullDownRefresh() {
    this.setData({
      currentPage: 1,
      hasMore: true
    })
    this.loadGameHistory()
    wx.stopPullDownRefresh()
  },

  /**
   * 上拉加载更多
   */
  onReachBottom() {
    if (this.data.hasMore) {
      this.loadMoreHistory()
    }
  },

  /**
   * 加载更多游戏历史
   */
  async loadMoreHistory() {
    // 模拟加载更多数据
    // 在实际应用中，这里应该调用API获取更多的游戏历史数据
    const { currentPage, gameHistory } = this.data
    const nextPage = currentPage + 1
    
    if (nextPage > 3) { // 模拟只有3页数据
      this.setData({ hasMore: false })
      return
    }
    
    // 模拟新的历史记录
    const newHistory = [
      {
        id: gameHistory.length + 1,
        date: `2024-01-${15 - nextPage * 2}`,
        result: nextPage % 2 === 0 ? '胜利' : '失败',
        role: nextPage % 2 === 0 ? '平民' : '卧底',
        word: nextPage % 2 === 0 ? '桌子' : '椅子',
        duration: `${Math.floor(Math.random() * 10) + 10}分钟`,
        players: Math.floor(Math.random() * 5) + 5
      }
    ]
    
    this.setData({
      gameHistory: [...gameHistory, ...newHistory],
      currentPage: nextPage
    })
  }
})