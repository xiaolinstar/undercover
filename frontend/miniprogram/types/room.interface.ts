/**
 * 房间服务接口定义
 */

import type { Room } from '../models/room.model'

/**
 * 房间服务接口
 */
export interface IRoomService {
  /**
   * 创建房间
   */
  createRoom(): Promise<Room>

  /**
   * 加入房间
   * @param roomCode 4位房间号
   */
  joinRoom(roomCode: string): Promise<Room>

  /**
   * 获取房间信息
   * @param roomId 房间唯一标识
   */
  getRoom(roomId: string): Promise<Room>

  /**
   * 离开房间
   * @param roomId 房间唯一标识
   */
  leaveRoom(roomId: string): Promise<void>
}
