import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'
import './style.css'

async function bootstrap() {
  const app = createApp(App)
  app.use(createPinia())
  app.use(router)

  // Resolve whether login is required before the first navigation guard runs.
  await useAuthStore().resolveAuthMode()

  app.mount('#app')
}

bootstrap()
