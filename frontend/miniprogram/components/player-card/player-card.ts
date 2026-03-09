/**
 * 玩家卡片组件
 * 用于展示玩家信息，支持状态显示和交互
 */

Component({
  /**
   * 组件属性
   */
  properties: {
    // 玩家信息
    player: {
      type: Object,
      value: {},
    },
    // 是否显示序号
    showNumber: {
      type: Boolean,
      value: true,
    },
    // 是否显示状态
    showStatus: {
      type: Boolean,
      value: true,
    },
    // 是否可点击
    clickable: {
      type: Boolean,
      value: false,
    },
    // 是否选中（用于投票等场景）
    selected: {
      type: Boolean,
      value: false,
    },
    // 是否禁用
    disabled: {
      type: Boolean,
      value: false,
    },
    // 是否是当前发言者
    isCurrentSpeaker: {
      type: Boolean,
      value: false,
    },
    // 是否被淘汰（动画效果）
    isEliminated: {
      type: Boolean,
      value: false,
    },
    // 投票数
    voteCount: {
      type: Number,
      value: 0,
    },
  },

  /**
   * 组件数据
   */
  data: {
    // 玩家状态文本映射
    statusText: {
      online: '在线',
      offline: '离线',
      eliminated: '淘汰',
      ready: '准备',
      not_ready: '未准备',
    },
    // 玩家状态颜色映射
    statusColor: {
      online: '#52c41a',
      offline: '#8c8c8c',
      eliminated: '#ff4d4f',
      ready: '#52c41a',
      not_ready: '#faad14',
    },
    // 默认头像
    defaultAvatar: 'https://mmbiz.qpic.cn/mmbiz/icTdbqWNOwNRna42FI242Lcia07jQodd2FJGIYQfG0LAJGFxM4FbnQP6yfMxBgJ0F3YRqJCJ1aPAK2dQagdusBZg/0',
  },

  /**
   * 组件方法
   */
  methods: {
    /**
     * 点击玩家卡片
     */
    handleTap() {
      const { clickable, disabled, player } = this.properties
      
      if (!clickable || disabled) {
        return
      }
      
      this.triggerEvent('tap', { player })
    },

    /**
     * 处理头像加载失败
     */
    handleAvatarError() {
      this.setData({
        'player.avatar': this.data.defaultAvatar,
      })
    },
  },
})
