# 游戏配置动态确定机制

## 🎯 设计理念

### 无参数创建房间的考虑

1. **分离关注点**
   - **房间创建** = 创建空间，让玩家聚集
   - **游戏配置** = 根据实际参与情况确定规则
   - **职责分离**：创建时不关心游戏规则，开始时才确定

2. **灵活性优先**
   - **动态适应**：根据实际玩家数量调整配置
   - **用户友好**：避免创建时就要决定复杂规则
   - **实时调整**：玩家加入/离开时可以重新评估

3. **游戏流程匹配**
   ```
   创建房间 → 等待玩家 → 开始游戏 → 确定配置 → 进行游戏
   ```

## 📋 游戏配置规则

### 卧底数量分配

根据玩家数量动态确定卧底数量：

| 玩家数量 | 卧底数量 | 平民数量 | 游戏平衡 |
|----------|----------|----------|----------|
| 3-5人    | 1个      | 2-4人    | 简单     |
| 6-8人    | 2个      | 4-6人    | 中等     |
| 9-12人   | 3个      | 6-9人    | 复杂     |

### 配置算法

```python
@classmethod
def get_undercover_count(cls, player_count: int) -> int:
    """根据玩家数量获取卧底数量"""
    for (min_players, max_players), count in cls.UNDERCOVER_COUNT_RULES.items():
        if min_players <= player_count <= max_players:
            return count
    return 0
```

## 🔄 实际执行流程

### 1. 创建房间阶段
```bash
POST /api/v1/room/create
Authorization: Bearer <token>
# 无需请求体参数
```

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "room_id": "abc12345",
    "room_code": "1234",
    "host_id": "user_123",
    "status": "waiting",
    "config": null  // 游戏配置待定
  }
}
```

### 2. 玩家加入阶段
- 玩家通过房间代码加入
- 实时更新玩家数量
- WebSocket通知玩家加入事件

### 3. 开始游戏阶段
```bash
POST /api/v1/game/start
Authorization: Bearer <token>
Content-Type: application/json

{
  "room_id": "abc12345"
}
```

**服务端处理**：
1. 验证用户身份（从Token获取）
2. 检查是否为房主
3. 验证玩家数量（最少3人）
4. **动态计算游戏配置**：
   ```python
   player_count = len(room.players)  # 例如：6人
   undercover_count = GameConfig.get_undercover_count(6)  # 返回：2个卧底
   ```
5. 随机分配角色
6. 分发词语

### 4. 配置确定结果

**示例：6人游戏**
- 总玩家：6人
- 卧底：2人
- 平民：4人
- 白板：0人（可选）

**WebSocket事件**：
```json
{
  "event": "game.started",
  "room_id": "abc12345",
  "timestamp": 1708675200,
  "data": {
    "player_count": 6,
    "undercover_count": 2,
    "civilian_count": 4,
    "whiteboard_count": 0,
    "game_config": {
      "total_players": 6,
      "undercover_ratio": "33%",
      "difficulty": "中等"
    }
  }
}
```

## 🎮 优势分析

### 1. 用户体验
- **简化操作**：创建房间一步完成
- **灵活组局**：等人齐了再开始
- **自动平衡**：系统自动配置最优规则

### 2. 技术优势
- **动态适应**：适应不同玩家规模
- **规则统一**：避免配置不一致
- **易于维护**：集中管理游戏规则

### 3. 游戏平衡
- **数学平衡**：基于概率论的最优配置
- **可扩展性**：容易添加新的配置规则
- **公平性**：所有玩家同等机会

## 🔧 配置扩展

### 未来可扩展的配置项

1. **白板模式**
   ```python
   if game_mode == "whiteboard":
       whiteboard_count = 1
       undercover_count = max(1, player_count // 4)
   ```

2. **难度等级**
   ```python
   DIFFICULTY_SETTINGS = {
       "easy": {"undercover_ratio": 0.15},
       "normal": {"undercover_ratio": 0.25}, 
       "hard": {"undercover_ratio": 0.35}
   }
   ```

3. **自定义规则**
   - 房主可自定义卧底比例
   - 设置特殊角色（如侦探、医生等）
   - 调整游戏时长限制

## 📊 数据统计

### 配置使用统计
- 记录不同玩家数量的游戏频率
- 分析游戏平衡性
- 优化配置规则

### 用户反馈
- 收集玩家对不同配置的体验
- 调整难度曲线
- 提升游戏满意度

---

这个设计确保了游戏配置的**动态性**、**灵活性**和**平衡性**，为玩家提供最佳的游戏体验。