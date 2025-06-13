import '@testing-library/jest-dom'

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

// Mock window.location
delete window.location;
window.location = {
  origin: 'http://localhost:3000',
  href: 'http://localhost:3000',
  reload: jest.fn(),
  assign: jest.fn(),
  replace: jest.fn(),
}

// Mock environment variables
process.env.NEXT_PUBLIC_SUPABASE_URL = 'https://jewpkwlteiendvfhslml.supabase.co'
process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Impld3Brd2x0ZWllbmR2ZmhzbG1sIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk3NTEwMjEsImV4cCI6MjA2NTMyNzAyMX0.jGrNVK5pbAX4-9VbUv6LutFUoKbzddmKYQA7_Rw2nlg'

// Mock console methods to reduce noise in tests
global.console = {
  ...console,
  // Suppress console.log in tests
  log: jest.fn(),
  warn: jest.fn(),
  error: jest.fn(),
}

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