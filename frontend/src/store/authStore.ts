import { create } from 'zustand'
import type { User, LoginFormData, RegisterFormData, UpdateProfileFormData, UpdatePasswordFormData } from '../types'
import * as api from '../services/api'

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (credentials: LoginFormData) => Promise<void>
  register: (data: RegisterFormData) => Promise<void>
  logout: () => Promise<void>
  fetchMe: () => Promise<void>
  updateMe: (data: UpdateProfileFormData) => Promise<void>
  updatePassword: (data: UpdatePasswordFormData) => Promise<void>
}

export const useAuthStore = create<AuthState>((set) => {
  const store: AuthState = {
    user: null,
    isAuthenticated: false,
    isLoading: true,

    async login(credentials) {
      const user = await api.login(credentials)
      set({ user, isAuthenticated: true })
    },

    async register(data) {
      const user = await api.register(data)
      set({ user, isAuthenticated: true })
    },

    async logout() {
      await api.logout()
      set({ user: null, isAuthenticated: false })
    },

    async fetchMe() {
      try {
        const user = await api.getMe()
        set({ user, isAuthenticated: true, isLoading: false })
      } catch {
        set({ user: null, isAuthenticated: false, isLoading: false })
      }
    },

    async updateMe(data) {
      const user = await api.updateMe(data)
      set({ user })
    },

    async updatePassword(data) {
      await api.updatePassword(data)
    },
  }

  // Initialise session check
  store.fetchMe()

  return store
})
