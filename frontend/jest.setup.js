import '@testing-library/jest-dom'

// Mock Supabase to avoid ES module import issues
jest.mock('@supabase/supabase-js', () => ({
  createClient: jest.fn(() => ({
    auth: {
      signInWithOAuth: jest.fn(),
      signOut: jest.fn(),
      getSession: jest.fn(),
      onAuthStateChange: jest.fn(() => ({
        data: { subscription: { unsubscribe: jest.fn() } }
      })),
    },
    from: jest.fn(() => ({
      select: jest.fn().mockReturnThis(),
      eq: jest.fn().mockReturnThis(),
      single: jest.fn(),
      insert: jest.fn().mockReturnThis(),
      upsert: jest.fn().mockReturnThis(),
    })),
    supabaseUrl: 'https://test.supabase.co',
    supabaseKey: 'test-key',
  }))
}))

// Mock window.location for OAuth redirect tests
Object.defineProperty(window, 'location', {
  value: { origin: 'http://localhost:3000' },
  writable: true
})

// Mock console methods to avoid noise in tests
global.console = {
  ...console,
  // Uncomment to disable specific console methods in tests
  // warn: jest.fn(),
  // error: jest.fn(),
}

// Mock Next.js router
jest.mock('next/navigation', () => ({
  useRouter() {
    return {
      push: jest.fn(),
      replace: jest.fn(),
      prefetch: jest.fn(),
      back: jest.fn(),
      reload: jest.fn(),
    }
  },
  usePathname() {
    return '/'
  },
  useSearchParams() {
    return new URLSearchParams()
  },
}))

// Mock environment variables
process.env.NEXT_PUBLIC_SUPABASE_URL = 'https://jewpkwlteiendvfhslml.supabase.co'
process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Impld3Brd2x0ZWllbmR2ZmhzbG1sIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk3NTEwMjEsImV4cCI6MjA2NTMyNzAyMX0.jGrNVK5pbAX4-9VbUv6LutFUoKbzddmKYQA7_Rw2nlg'

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
}

// Mock ResizeObserver
global.ResizeObserver = class ResizeObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
} 