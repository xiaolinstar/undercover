/**
 * 房间卡片组件
 * 用于展示房间信息，支持点击进入房间
 */

Component({
  /**
   * 组件属性
   */
  properties: {
    // 房间信息
    room: {
      type: Object,
      value: {},
    },
    // 是否显示创建时间
    showCreateTime: {
      type: Boolean,
      value: false,
    },
  },

  /**
   * 组件数据
   */
  data: {
    // 房间状态文本映射
    statusText: {
      waiting: '等待中',
      playing: '游戏中',
      finished: '已结束',
    },
    // 房间状态颜色映射
    statusColor: {
      waiting: '#52c41a',
      playing: '#1890ff',
      finished: '#8c8c8c',
    },
  },

  /**
   * 组件方法
   */
  methods: {
    /**
     * 点击房间卡片
     */
    handleTap() {
      const { room } = this.properties
      this.triggerEvent('tap', { room })
    },

    /**
     * 点击进入房间按钮
     */
    handleEnterRoom() {
      const { room } = this.properties
      this.triggerEvent('enter', { room })
    },

    /**
     * 格式化时间
     */
    formatTime(timestamp: number): string {
      if (!timestamp) return ''
      
      const date = new Date(timestamp)
      const now = new Date()
      const diff = now.getTime() - date.getTime()
      
      // 1小时内
      if (diff < 3600000) {
        const minutes = Math.floor(diff / 60000)
        return `${minutes}分钟前`
      }
      
      // 24小时内
      if (diff < 86400000) {
        const hours = Math.floor(diff / 3600000)
        return `${hours}小时前`
      }
      
      // 超过24小时
      const month = date.getMonth() + 1
      const day = date.getDate()
      const hour = date.getHours()
      const minute = date.getMinutes()
      
      return `${month}月${day}日 ${hour}:${minute.toString().padStart(2, '0')}`
    },
  },
})
