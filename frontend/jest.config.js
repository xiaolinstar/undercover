module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  
  // 测试文件匹配
  testMatch: [
    '<rootDir>/tests/**/*.test.ts',
    '<rootDir>/tests/**/*.spec.ts',
  ],
  
  // 忽略的文件
  testPathIgnorePatterns: [
    '/node_modules/',
    '/miniprogram_npm/',
  ],
  
  // 模块路径映射
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/miniprogram/$1',
  },
  
  // 覆盖率配置
  collectCoverageFrom: [
    'miniprogram/**/*.ts',
    '!miniprogram/**/*.d.ts',
    '!miniprogram/pages/**/*.ts',
    '!miniprogram/components/**/*.ts',
    '!miniprogram/app.ts',
  ],
  
  // 覆盖率阈值（核心业务逻辑至少 70%）
  coverageThreshold: {
    global: {
      branches: 55,
      functions: 70,
      lines: 70,
      statements: 70,
    },
  },
  
  // 覆盖率报告格式
  coverageReporters: [
    'text',
    'text-summary',
    'html',
    'lcov',
  ],
  
  // 输出目录
  coverageDirectory: 'coverage',
  
  // 设置文件
  setupFilesAfterEnv: ['<rootDir>/tests/setup.ts'],
  
  // 预处理文件
  transform: {
    '^.+\\.ts$': ['ts-jest', {
      tsconfig: 'tsconfig.json',
    }],
  },
  
  // 模块文件扩展名
  moduleFileExtensions: ['ts', 'js', 'json'],
}
