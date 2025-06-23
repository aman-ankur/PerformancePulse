import type { Config } from '@jest/types'
import type { jest } from '@jest/globals'

declare global {
  const jest: typeof jest
  const describe: jest.Describe
  const it: jest.It
  const test: jest.It
  const expect: jest.Expect
  const beforeAll: jest.Lifecycle
  const afterAll: jest.Lifecycle
  const beforeEach: jest.Lifecycle
  const afterEach: jest.Lifecycle
} 