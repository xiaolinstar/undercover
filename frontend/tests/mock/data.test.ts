/**
 * Mock 数据工具函数测试
 */

import { generateUUID, generateRoomCode } from '../../miniprogram/mock/data'

describe('Mock 数据工具函数', () => {
  describe('generateUUID 函数', () => {
    it('应该生成有效的 UUID', () => {
      const uuid = generateUUID()
      
      // UUID 格式: xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx
      expect(uuid).toMatch(/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/)
    })
    
    it('每次生成的 UUID 应该不同', () => {
      const uuid1 = generateUUID()
      const uuid2 = generateUUID()
      
      expect(uuid1).not.toBe(uuid2)
    })
  })
  
  describe('generateRoomCode 函数', () => {
    it('应该生成 4 位数字的房间号', () => {
      const roomCode = generateRoomCode()
      
      expect(roomCode).toMatch(/^\d{4}$/)
      expect(parseInt(roomCode)).toBeGreaterThanOrEqual(1000)
      expect(parseInt(roomCode)).toBeLessThanOrEqual(9999)
    })
    
    it('每次生成的房间号应该不同（大概率）', () => {
      const codes = new Set()
      for (let i = 0; i < 100; i++) {
        codes.add(generateRoomCode())
      }
      
      // 100 次生成应该有至少 90 个不同的房间号
      expect(codes.size).toBeGreaterThan(90)
    })
  })
})
