/**
 * 游戏状态栏组件
 * 用于显示游戏进度和状态信息
 */

Component({
  /**
   * 组件属性
   */
  properties: {
    // 当前轮次
    round: {
      type: Number,
      value: 1,
    },
    // 游戏阶段（describing: 描述, voting: 投票, finished: 结束）
    phase: {
      type: String,
      value: 'describing',
    },
    // 倒计时（秒）
    countdown: {
      type: Number,
      value: 0,
    },
    // 存活玩家数
    alivePlayers: {
      type: Number,
      value: 0,
    },
    // 总玩家数
    totalPlayers: {
      type: Number,
      value: 0,
    },
    // 当前发言玩家序号
    currentPlayerNumber: {
      type: Number,
      value: 0,
    },
  },

  /**
   * 组件数据
   */
  data: {
    // 阶段文本映射
    phaseText: {
      describing: '描述环节',
      voting: '投票环节',
      finished: '游戏结束',
    },
    // 阶段图标映射
    phaseIcon: {
      describing: '💬',
      voting: '🗳️',
      finished: '🏆',
    },
    // 倒计时文本
    countdownText: '',
    // 倒计时定时器
    timer: null as NodeJS.Timeout | null,
    // 是否显示警告（倒计时少于10秒）
    showWarning: false,
  },

  /**
   * 组件生命周期
   */
  lifetimes: {
    attached() {
      this.updateCountdown()
    },
    
    detached() {
      this.stopCountdown()
    },
  },

  /**
   * 监听属性变化
   */
  observers: {
    'countdown': function(countdown: number) {
      if (countdown > 0) {
        this.updateCountdown()
        this.startCountdown()
      } else {
        this.stopCountdown()
        this.setData({ countdownText: '', showWarning: false })
      }
    },
  },

  /**
   * 组件方法
   */
  methods: {
    /**
     * 更新倒计时显示
     */
    updateCountdown() {
      const { countdown } = this.properties
      
      if (countdown <= 0) {
        this.setData({ countdownText: '', showWarning: false })
        return
      }
      
      const minutes = Math.floor(countdown / 60)
      const seconds = countdown % 60
      
      this.setData({
        countdownText: `${minutes}:${seconds.toString().padStart(2, '0')}`,
        showWarning: countdown <= 10,
      })
    },

    /**
     * 开始倒计时
     */
    startCountdown() {
      this.stopCountdown()
      
      const timer = setInterval(() => {
        let remaining = this.properties.countdown
        
        if (remaining <= 0) {
          this.stopCountdown()
          this.triggerEvent('timeout')
          return
        }
        
        remaining--
        this.updateCountdown()
        
        // 触发倒计时更新事件
        this.triggerEvent('countdown', { remaining })
      }, 1000)
      
      this.setData({ timer })
    },

    /**
     * 停止倒计时
     */
    stopCountdown() {
      if (this.data.timer) {
        clearInterval(this.data.timer)
        this.setData({ timer: null })
      }
    },
  },
})
