import { create } from 'zustand'
import axiosInstance from '../../core/api'
import { UserProfile } from '../../types'

interface AuthState {
  token: string | null
  profile: UserProfile | null
  login: (username: string, password: string) => Promise<void>
  logout: () => void
  fetchMe: () => Promise<void>
}

export const useAuthStore = create<AuthState>((set) => ({
  token: localStorage.getItem('token'),
  profile: null,

  login: async (username, password) => {
    const { data } = await axiosInstance.post('/api/auth/login', { username, password })
    localStorage.setItem('token', data.access_token)
    set({ token: data.access_token })
    // Fetch full profile after login
    const me = await axiosInstance.get('/api/auth/me')
    set({ profile: me.data })
  },

  logout: () => {
    localStorage.removeItem('token')
    set({ token: null, profile: null })
  },

  fetchMe: async () => {
    try {
      const { data } = await axiosInstance.get('/api/auth/me')
      set({ profile: data })
    } catch {
      localStorage.removeItem('token')
      set({ token: null, profile: null })
    }
  },
}))
