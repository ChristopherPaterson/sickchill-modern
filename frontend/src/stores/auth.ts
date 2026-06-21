import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api, clearToken, getToken, setToken } from '@/api/client'

export const useAuthStore = defineStore('auth', () => {
  const username = ref<string | null>(null)
  // Whether the backend requires login. Resolved at startup from /system/health.
  const authEnabled = ref<boolean>(true)
  const isAuthenticated = ref<boolean>(!!getToken())

  async function resolveAuthMode(): Promise<void> {
    try {
      const { data } = await api.get('/system/health')
      authEnabled.value = !!data.auth_enabled
    } catch {
      authEnabled.value = true // fail safe: assume login required
    }
  }

  async function login(user: string, password: string): Promise<void> {
    const body = new URLSearchParams()
    body.set('username', user)
    body.set('password', password)
    const { data } = await api.post('/auth/login', body)
    setToken(data.access_token)
    isAuthenticated.value = true
    await fetchMe()
  }

  async function fetchMe(): Promise<void> {
    const { data } = await api.get('/auth/me')
    username.value = data.username
  }

  function logout(): void {
    clearToken()
    isAuthenticated.value = false
    username.value = null
  }

  return { username, authEnabled, isAuthenticated, resolveAuthMode, login, fetchMe, logout }
})
