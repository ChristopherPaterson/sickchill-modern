<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const username = ref('admin')
const password = ref('')
const error = ref<string | null>(null)
const busy = ref(false)

async function submit() {
  error.value = null
  busy.value = true
  try {
    await auth.login(username.value, password.value)
    const redirect = (route.query.redirect as string) || '/'
    router.push(redirect)
  } catch {
    error.value = 'Incorrect username or password'
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="login-wrap">
    <form class="card login-card" @submit.prevent="submit">
      <h1>SickChill Modern</h1>
      <label>Username</label>
      <input v-model="username" autocomplete="username" />
      <label>Password</label>
      <input v-model="password" type="password" autocomplete="current-password" />
      <p v-if="error" class="error">{{ error }}</p>
      <button :disabled="busy" type="submit">{{ busy ? 'Signing in…' : 'Sign in' }}</button>
    </form>
  </div>
</template>

<style scoped>
.login-wrap {
  min-height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}
.login-card {
  width: 100%;
  max-width: 360px;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.login-card h1 { margin: 0 0 0.5rem; font-size: 1.25rem; }
.login-card label { font-size: 0.8rem; color: var(--muted); margin-top: 0.5rem; }
.login-card button { margin-top: 1rem; }
.error { color: var(--danger); font-size: 0.85rem; margin: 0.25rem 0 0; }
</style>
