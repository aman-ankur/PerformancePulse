/**
 * Tests for Supabase client configuration and auth functions
 * These tests verify the Supabase integration works correctly
 */

import { supabase, auth } from '../supabase'

// Mock environment variables for testing
const mockEnvVars = {
  NEXT_PUBLIC_SUPABASE_URL: 'https://jewpkwlteiendvfhslml.supabase.co',
  NEXT_PUBLIC_SUPABASE_ANON_KEY: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Impld3Brd2x0ZWllbmR2ZmhzbG1sIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk3NTEwMjEsImV4cCI6MjA2NTMyNzAyMX0.jGrNVK5pbAX4-9VbUv6LutFUoKbzddmKYQA7_Rw2nlg'
}

describe('Supabase Configuration', () => {
  beforeAll(() => {
    // Set up environment variables
    Object.keys(mockEnvVars).forEach(key => {
      process.env[key] = mockEnvVars[key as keyof typeof mockEnvVars]
    })
  })

  test('should create Supabase client successfully', () => {
    expect(supabase).toBeDefined()
    expect(supabase.auth).toBeDefined()
    expect(supabase.from).toBeDefined()
  })

  test('should have correct auth configuration', () => {
    // Test that auth options are properly set (with mocked values)
    expect(supabase.supabaseKey).toBe('test-key')
    expect(supabase.supabaseUrl).toBe('https://test.supabase.co')
  })
})

describe('Auth Functions', () => {
  // Mock window.location for OAuth tests
  const mockLocation = {
    origin: 'http://localhost:3000'
  }
  
  beforeAll(() => {
    Object.defineProperty(window, 'location', {
      value: mockLocation,
      writable: true
    })
  })

  describe('signInWithGoogle', () => {
    test('should call signInWithOAuth with correct parameters', async () => {
      const mockSignInWithOAuth = jest.fn().mockResolvedValue({ 
        data: { provider: 'google' }, 
        error: null 
      })
      
      // Mock the Supabase auth method
      jest.spyOn(supabase.auth, 'signInWithOAuth').mockImplementation(mockSignInWithOAuth)

      const result = await auth.signInWithGoogle()

      expect(mockSignInWithOAuth).toHaveBeenCalledWith({
        provider: 'google',
        options: {
          redirectTo: 'http://localhost:3000/auth/callback',
          queryParams: {
            access_type: 'offline',
            prompt: 'consent',
          }
        }
      })
      
      expect(result).toEqual({ provider: 'google' })
    })

    test('should throw error if OAuth fails', async () => {
      const mockError = new Error('OAuth failed')
      jest.spyOn(supabase.auth, 'signInWithOAuth').mockResolvedValue({
        data: null,
        error: mockError
      })

      await expect(auth.signInWithGoogle()).rejects.toThrow('OAuth failed')
    })
  })

  describe('signOut', () => {
    test('should call supabase signOut', async () => {
      const mockSignOut = jest.fn().mockResolvedValue({ error: null })
      jest.spyOn(supabase.auth, 'signOut').mockImplementation(mockSignOut)

      await auth.signOut()

      expect(mockSignOut).toHaveBeenCalled()
    })

    test('should throw error if signOut fails', async () => {
      const mockError = new Error('Sign out failed')
      jest.spyOn(supabase.auth, 'signOut').mockResolvedValue({ error: mockError })

      await expect(auth.signOut()).rejects.toThrow('Sign out failed')
    })
  })

  describe('getSession', () => {
    test('should return session data', async () => {
      const mockSession = { 
        user: { id: 'test-user-id', email: 'test@example.com' } 
      }
      const mockGetSession = jest.fn().mockResolvedValue({ 
        data: { session: mockSession }, 
        error: null 
      })
      
      jest.spyOn(supabase.auth, 'getSession').mockImplementation(mockGetSession)

      const result = await auth.getSession()

      expect(mockGetSession).toHaveBeenCalled()
      expect(result).toEqual(mockSession)
    })

    test('should throw error if getSession fails', async () => {
      const mockError = new Error('Session fetch failed')
      jest.spyOn(supabase.auth, 'getSession').mockResolvedValue({
        data: { session: null },
        error: mockError
      })

      await expect(auth.getSession()).rejects.toThrow('Session fetch failed')
    })
  })

  describe('getProfile', () => {
    test('should return user profile', async () => {
      const mockProfile = {
        id: 'test-user-id',
        full_name: 'Test User',
        email: 'test@example.com',
        role: 'manager' as const,
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z'
      }

      const mockFrom = jest.fn().mockReturnValue({
        select: jest.fn().mockReturnValue({
          eq: jest.fn().mockReturnValue({
            single: jest.fn().mockResolvedValue({ data: mockProfile, error: null })
          })
        })
      })
      
      jest.spyOn(supabase, 'from').mockImplementation(mockFrom)

      const result = await auth.getProfile('test-user-id')

      expect(mockFrom).toHaveBeenCalledWith('profiles')
      expect(result).toEqual(mockProfile)
    })

    test('should return null if profile not found', async () => {
      const mockFrom = jest.fn().mockReturnValue({
        select: jest.fn().mockReturnValue({
          eq: jest.fn().mockReturnValue({
            single: jest.fn().mockResolvedValue({ 
              data: null, 
              error: { code: 'PGRST116' } 
            })
          })
        })
      })
      
      jest.spyOn(supabase, 'from').mockImplementation(mockFrom)

      const result = await auth.getProfile('non-existent-user')

      expect(result).toBeNull()
    })

    test('should throw error if database query fails', async () => {
      const mockError = new Error('Database error')
      const mockFrom = jest.fn().mockReturnValue({
        select: jest.fn().mockReturnValue({
          eq: jest.fn().mockReturnValue({
            single: jest.fn().mockResolvedValue({ data: null, error: mockError })
          })
        })
      })
      
      jest.spyOn(supabase, 'from').mockImplementation(mockFrom)

      await expect(auth.getProfile('test-user-id')).rejects.toThrow('Database error')
    })
  })

  describe('upsertProfile', () => {
    test('should create/update profile successfully', async () => {
      const mockProfile = {
        id: 'test-user-id',
        full_name: 'Test User',
        email: 'test@example.com',
        role: 'manager' as const
      }

      const mockFrom = jest.fn().mockReturnValue({
        upsert: jest.fn().mockReturnValue({
          select: jest.fn().mockReturnValue({
            single: jest.fn().mockResolvedValue({ data: mockProfile, error: null })
          })
        })
      })
      
      jest.spyOn(supabase, 'from').mockImplementation(mockFrom)

      const result = await auth.upsertProfile(mockProfile)

      expect(mockFrom).toHaveBeenCalledWith('profiles')
      expect(result).toEqual(mockProfile)
    })

    test('should throw error if upsert fails', async () => {
      const mockError = new Error('Upsert failed')
      const mockFrom = jest.fn().mockReturnValue({
        upsert: jest.fn().mockReturnValue({
          select: jest.fn().mockReturnValue({
            single: jest.fn().mockResolvedValue({ data: null, error: mockError })
          })
        })
      })
      
      jest.spyOn(supabase, 'from').mockImplementation(mockFrom)

      await expect(auth.upsertProfile({})).rejects.toThrow('Upsert failed')
    })
  })
})

// Cleanup after tests
afterEach(() => {
  jest.clearAllMocks()
}) 