import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'
import './style.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')

// Resolve auth mode in the background (only used to hide the "Sign out" item).
// The actual login gate is reactive: the API client redirects to login on a 401,
// so when auth is disabled (server never 401s) login can never appear.
useAuthStore().resolveAuthMode()
