/**
 * 词语展示组件
 * 用于展示玩家的词语和角色信息
 */

Component({
  /**
   * 组件属性
   */
  properties: {
    // 词语
    word: {
      type: String,
      value: '',
    },
    // 角色（civilian: 平民, undercover: 卧底）
    role: {
      type: String,
      value: '',
    },
    // 是否显示词语
    showWord: {
      type: Boolean,
      value: false,
    },
    // 是否显示角色
    showRole: {
      type: Boolean,
      value: false,
    },
    // 是否可点击
    clickable: {
      type: Boolean,
      value: true,
    },
    // 提示文本
    hint: {
      type: String,
      value: '点击查看你的词语',
    },
  },

  /**
   * 组件数据
   */
  data: {
    // 角色文本映射
    roleText: {
      civilian: '平民',
      undercover: '卧底',
    },
    // 角色颜色映射
    roleColor: {
      civilian: '#52c41a',
      undercover: '#ff4d4f',
    },
    // 是否正在播放动画
    animating: false,
  },

  /**
   * 组件方法
   */
  methods: {
    /**
     * 点击展示词语
     */
    handleTap() {
      const { clickable, showWord } = this.properties
      
      if (!clickable) {
        return
      }
      
      // 切换显示状态
      if (!showWord) {
        this.showWord()
      }
    },

    /**
     * 展示词语（带动画）
     */
    showWord() {
      this.setData({ animating: true })
      
      // 触发显示事件
      this.triggerEvent('show', {
        word: this.properties.word,
        role: this.properties.role,
      })
      
      // 动画结束后重置状态
      setTimeout(() => {
        this.setData({ animating: false })
      }, 600)
    },

    /**
     * 隐藏词语
     */
    hideWord() {
      this.triggerEvent('hide')
    },
  },
})
