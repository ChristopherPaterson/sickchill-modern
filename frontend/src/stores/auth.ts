import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api, clearToken, getToken, setToken } from '@/api/client'

export const useAuthStore = defineStore('auth', () => {
  const username = ref<string | null>(null)
  const isAuthenticated = ref<boolean>(!!getToken())

  async function login(user: string, password: string): Promise<void> {
    // OAuth2 password flow expects form-encoded body.
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

  return { username, isAuthenticated, login, fetchMe, logout }
})
