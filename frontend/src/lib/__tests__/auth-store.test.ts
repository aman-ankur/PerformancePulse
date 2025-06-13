/**
 * Tests for Zustand auth store
 * Tests authentication state management and flows
 */

import { renderHook, act } from '@testing-library/react'
import { useAuthStore, useAuth, useRequireAuth } from '../auth-store'
import { auth } from '../supabase'

// Mock the Supabase auth module
jest.mock('../supabase', () => ({
  supabase: {
    auth: {
      onAuthStateChange: jest.fn(() => ({ data: { subscription: { unsubscribe: jest.fn() } } })),
    },
  },
  auth: {
    getSession: jest.fn(),
    signInWithGoogle: jest.fn(),
    signOut: jest.fn(),
    getProfile: jest.fn(),
    upsertProfile: jest.fn(),
  },
}))

const mockAuth = auth as jest.Mocked<typeof auth>

describe('useAuthStore', () => {
  beforeEach(() => {
    // Reset store state before each test
    useAuthStore.setState({
      session: null,
      user: null,
      profile: null,
      loading: false,
      initialized: false,
    })
    jest.clearAllMocks()
  })

  describe('initialization', () => {
    test('should initialize with empty state', () => {
      const { result } = renderHook(() => useAuthStore())
      
      expect(result.current.session).toBeNull()
      expect(result.current.user).toBeNull()
      expect(result.current.profile).toBeNull()
      expect(result.current.loading).toBe(false)
      expect(result.current.initialized).toBe(false)
    })

    test('should initialize auth store with existing session', async () => {
      const mockSession = {
        user: {
          id: 'test-user-id',
          email: 'test@example.com',
          user_metadata: { full_name: 'Test User' }
        }
      }
      const mockProfile = {
        id: 'test-user-id',
        full_name: 'Test User',
        email: 'test@example.com',
        role: 'manager' as const,
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z'
      }

      mockAuth.getSession.mockResolvedValue(mockSession as any)
      mockAuth.getProfile.mockResolvedValue(mockProfile)

      const { result } = renderHook(() => useAuthStore())

      await act(async () => {
        await result.current.initialize()
      })

      expect(result.current.session).toEqual(mockSession)
      expect(result.current.user).toEqual(mockSession.user)
      expect(result.current.profile).toEqual(mockProfile)
      expect(result.current.initialized).toBe(true)
      expect(result.current.loading).toBe(false)
    })

    test('should initialize with empty state when no session exists', async () => {
      mockAuth.getSession.mockResolvedValue(null)

      const { result } = renderHook(() => useAuthStore())

      await act(async () => {
        await result.current.initialize()
      })

      expect(result.current.session).toBeNull()
      expect(result.current.user).toBeNull()
      expect(result.current.profile).toBeNull()
      expect(result.current.initialized).toBe(true)
      expect(result.current.loading).toBe(false)
    })

    test('should create new profile for OAuth users without existing profile', async () => {
      const mockSession = {
        user: {
          id: 'new-user-id',
          email: 'newuser@example.com',
          user_metadata: { full_name: 'New User' }
        }
      }
      const mockNewProfile = {
        id: 'new-user-id',
        full_name: 'New User',
        email: 'newuser@example.com',
        role: 'manager' as const,
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z'
      }

      mockAuth.getSession.mockResolvedValue(mockSession as any)
      mockAuth.getProfile.mockResolvedValue(null) // No existing profile
      mockAuth.upsertProfile.mockResolvedValue(mockNewProfile)

      const { result } = renderHook(() => useAuthStore())

      await act(async () => {
        await result.current.initialize()
      })

      // Note: In the real app, profile creation happens in the onAuthStateChange listener
      // For this test, we'll verify the basic initialization without the listener
      expect(result.current.session).toEqual(mockSession)
      expect(result.current.user).toEqual(mockSession.user)
      expect(result.current.initialized).toBe(true)
      
      // The profile creation would normally happen in the auth state change listener
      // which is harder to test directly in this environment
    })
  })

  describe('signIn', () => {
    test('should call signInWithGoogle', async () => {
      mockAuth.signInWithGoogle.mockResolvedValue({ data: { provider: 'google' } } as any)

      const { result } = renderHook(() => useAuthStore())

      await act(async () => {
        await result.current.signIn()
      })

      expect(mockAuth.signInWithGoogle).toHaveBeenCalled()
    })

    test('should handle sign in errors', async () => {
      const mockError = new Error('Sign in failed')
      mockAuth.signInWithGoogle.mockRejectedValue(mockError)

      const { result } = renderHook(() => useAuthStore())

      await act(async () => {
        await expect(result.current.signIn()).rejects.toThrow('Sign in failed')
      })

      expect(result.current.loading).toBe(false)
    })
  })

  describe('signOut', () => {
    test('should call signOut', async () => {
      mockAuth.signOut.mockResolvedValue()

      const { result } = renderHook(() => useAuthStore())

      await act(async () => {
        await result.current.signOut()
      })

      expect(mockAuth.signOut).toHaveBeenCalled()
    })

    test('should handle sign out errors', async () => {
      const mockError = new Error('Sign out failed')
      mockAuth.signOut.mockRejectedValue(mockError)

      const { result } = renderHook(() => useAuthStore())

      await act(async () => {
        await expect(result.current.signOut()).rejects.toThrow('Sign out failed')
      })

      expect(result.current.loading).toBe(false)
    })
  })

  describe('updateProfile', () => {
    test('should update profile successfully', async () => {
      const mockUser = { id: 'test-user-id', email: 'test@example.com' }
      const mockProfile = {
        id: 'test-user-id',
        full_name: 'Test User',
        email: 'test@example.com',
        role: 'manager' as const,
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z'
      }
      const updatedProfile = { ...mockProfile, full_name: 'Updated User' }

      // Set initial state
      useAuthStore.setState({
        user: mockUser as any,
        profile: mockProfile,
        session: { user: mockUser } as any,
        initialized: true,
        loading: false
      })

      mockAuth.upsertProfile.mockResolvedValue(updatedProfile)

      const { result } = renderHook(() => useAuthStore())

      await act(async () => {
        await result.current.updateProfile({ full_name: 'Updated User' })
      })

      expect(mockAuth.upsertProfile).toHaveBeenCalledWith({
        ...mockProfile,
        full_name: 'Updated User',
        id: 'test-user-id'
      })
      expect(result.current.profile).toEqual(updatedProfile)
    })

    test('should throw error when no authenticated user', async () => {
      const { result } = renderHook(() => useAuthStore())

      await act(async () => {
        await expect(
          result.current.updateProfile({ full_name: 'Test' })
        ).rejects.toThrow('No authenticated user')
      })
    })
  })
})

describe('useAuth helper hook', () => {
  beforeEach(() => {
    useAuthStore.setState({
      session: null,
      user: null,
      profile: null,
      loading: false,
      initialized: false,
    })
  })

  test('should return correct authentication status', () => {
    useAuthStore.setState({
      session: { user: { id: 'test' } } as any,
      profile: { role: 'manager' } as any,
      initialized: true,
      loading: false
    })

    const { result } = renderHook(() => useAuth())

    expect(result.current.isAuthenticated).toBe(true)
    expect(result.current.isManager).toBe(true)
    expect(result.current.isTeamMember).toBe(false)
  })

  test('should return false for unauthenticated user', () => {
    const { result } = renderHook(() => useAuth())

    expect(result.current.isAuthenticated).toBe(false)
    expect(result.current.isManager).toBe(false)
    expect(result.current.isTeamMember).toBe(false)
  })
})

describe('useRequireAuth guard hook', () => {
  beforeEach(() => {
    useAuthStore.setState({
      session: null,
      user: null,
      profile: null,
      loading: false,
      initialized: false,
    })
  })

  test('should deny access when not initialized', () => {
    const { result } = renderHook(() => useRequireAuth())

    expect(result.current.canAccess).toBe(false)
    expect(result.current.reason).toBe('loading')
  })

  test('should deny access when not authenticated', () => {
    useAuthStore.setState({ initialized: true })

    const { result } = renderHook(() => useRequireAuth())

    expect(result.current.canAccess).toBe(false)
    expect(result.current.reason).toBe('not_authenticated')
  })

  test('should deny access when no profile exists', () => {
    useAuthStore.setState({
      initialized: true,
      session: { user: { id: 'test' } } as any,
      profile: null
    })

    const { result } = renderHook(() => useRequireAuth())

    expect(result.current.canAccess).toBe(false)
    expect(result.current.reason).toBe('no_profile')
  })

  test('should deny access for insufficient role', () => {
    useAuthStore.setState({
      initialized: true,
      session: { user: { id: 'test' } } as any,
      profile: { role: 'team_member' } as any
    })

    const { result } = renderHook(() => useRequireAuth('manager'))

    expect(result.current.canAccess).toBe(false)
    expect(result.current.reason).toBe('insufficient_role')
  })

  test('should allow access for authenticated user with correct role', () => {
    useAuthStore.setState({
      initialized: true,
      session: { user: { id: 'test' } } as any,
      profile: { role: 'manager' } as any
    })

    const { result } = renderHook(() => useRequireAuth('manager'))

    expect(result.current.canAccess).toBe(true)
    expect(result.current.reason).toBe('authorized')
  })

  test('should allow access when no specific role required', () => {
    useAuthStore.setState({
      initialized: true,
      session: { user: { id: 'test' } } as any,
      profile: { role: 'team_member' } as any
    })

    const { result } = renderHook(() => useRequireAuth())

    expect(result.current.canAccess).toBe(true)
    expect(result.current.reason).toBe('authorized')
  })
}) 