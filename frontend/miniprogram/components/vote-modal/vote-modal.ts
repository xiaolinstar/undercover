/**
 * 投票弹窗组件
 * 用于游戏中的投票环节
 */

Component({
  /**
   * 组件属性
   */
  properties: {
    // 是否显示弹窗
    visible: {
      type: Boolean,
      value: false,
    },
    // 玩家列表
    players: {
      type: Array,
      value: [],
    },
    // 当前玩家ID
    currentPlayerId: {
      type: String,
      value: '',
    },
    // 标题
    title: {
      type: String,
      value: '投票环节',
    },
    // 提示文本
    hint: {
      type: String,
      value: '请选择你要投票的玩家',
    },
    // 倒计时（秒）
    countdown: {
      type: Number,
      value: 30,
    },
  },

  /**
   * 组件数据
   */
  data: {
    // 选中的玩家ID
    selectedPlayerId: '',
    // 倒计时文本
    countdownText: '',
    // 倒计时定时器
    timer: null as NodeJS.Timeout | null,
  },

  /**
   * 组件生命周期
   */
  lifetimes: {
    attached() {
      // 初始化倒计时文本
      this.updateCountdownText()
    },
    
    detached() {
      // 清除定时器
      if (this.data.timer) {
        clearInterval(this.data.timer)
      }
    },
  },

  /**
   * 监听属性变化
   */
  observers: {
    'visible, countdown': function(visible: boolean, countdown: number) {
      if (visible && countdown > 0) {
        this.startCountdown()
      } else if (!visible) {
        this.stopCountdown()
      }
    },
  },

  /**
   * 组件方法
   */
  methods: {
    /**
     * 选择玩家
     */
    handleSelectPlayer(e: any) {
      const { playerId } = e.currentTarget.dataset
      this.setData({ selectedPlayerId: playerId })
    },

    /**
     * 确认投票
     */
    handleConfirm() {
      const { selectedPlayerId } = this.data
      
      if (!selectedPlayerId) {
        wx.showToast({
          title: '请选择要投票的玩家',
          icon: 'none',
        })
        return
      }
      
      this.triggerEvent('confirm', { playerId: selectedPlayerId })
    },

    /**
     * 取消投票
     */
    handleCancel() {
      this.setData({ selectedPlayerId: '' })
      this.triggerEvent('cancel')
    },

    /**
     * 开始倒计时
     */
    startCountdown() {
      this.stopCountdown()
      
      let remaining = this.properties.countdown
      this.updateCountdownText(remaining)
      
      const timer = setInterval(() => {
        remaining--
        
        if (remaining <= 0) {
          this.stopCountdown()
          // 倒计时结束，自动提交投票
          if (this.data.selectedPlayerId) {
            this.handleConfirm()
          } else {
            this.triggerEvent('timeout')
          }
          return
        }
        
        this.updateCountdownText(remaining)
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

    /**
     * 更新倒计时文本
     */
    updateCountdownText(seconds?: number) {
      const countdown = seconds !== undefined ? seconds : this.properties.countdown
      const minutes = Math.floor(countdown / 60)
      const secs = countdown % 60
      
      this.setData({
        countdownText: `${minutes}:${secs.toString().padStart(2, '0')}`,
      })
    },

    /**
     * 阻止冒泡
     */
    preventBubble() {
      // 阻止点击弹窗内容区域关闭弹窗
    },
  },
})
