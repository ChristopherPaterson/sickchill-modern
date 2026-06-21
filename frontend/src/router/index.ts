import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Routes backed by real views.
const realRoutes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
    meta: { public: true, title: 'Sign in' },
  },
  { path: '/', name: 'shows', component: () => import('@/views/ShowsView.vue'), meta: { title: 'Shows' } },
  {
    path: '/show/:id',
    name: 'show-detail',
    component: () => import('@/views/ShowDetailView.vue'),
    props: true,
    meta: { title: 'Show' },
  },
  { path: '/add-shows', name: 'add-shows', component: () => import('@/views/AddShowsView.vue'), meta: { title: 'Add Shows' } },
  {
    path: '/post-process',
    name: 'post-process',
    component: () => import('@/views/ManualPostProcessView.vue'),
    meta: { title: 'Manual Post-Processing' },
  },
  {
    path: '/config/post-processing',
    name: 'config-postprocessing',
    component: () => import('@/views/PostProcessingConfigView.vue'),
    meta: { title: 'Post Processing' },
  },
  { path: '/schedule', name: 'schedule', component: () => import('@/views/CalendarView.vue'), meta: { title: 'Schedule' } },
  { path: '/history', name: 'history', component: () => import('@/views/HistoryView.vue'), meta: { title: 'History' } },
  { path: '/settings', name: 'settings', component: () => import('@/views/SettingsView.vue'), meta: { title: 'General' } },
  {
    path: '/config/providers',
    name: 'config-providers',
    component: () => import('@/views/SearchProvidersView.vue'),
    meta: { title: 'Search Providers' },
  },
]

// Routes that are scaffolded (in the menu, routable) but not yet implemented.
// They render the generic PlaceholderView using meta.title.
const placeholder = () => import('@/views/PlaceholderView.vue')
const stub: Array<[string, string, string]> = [
  ['/manage', 'manage', 'Mass Update'],
  ['/manage/backlog', 'manage-backlog', 'Backlog Overview'],
  ['/manage/searches', 'manage-searches', 'Manage Searches'],
  ['/manage/episode-status', 'manage-episode-status', 'Episode Status Management'],
  ['/manage/failed', 'manage-failed', 'Failed Downloads'],
  ['/manage/subtitles', 'manage-subtitles', 'Missed Subtitles'],
  ['/config/search', 'config-search', 'Search Settings'],
  ['/config/subtitles', 'config-subtitles', 'Subtitles'],
  ['/config/notifications', 'config-notifications', 'Notifications'],
  ['/system/status', 'system-status', 'Server Status'],
  ['/system/log', 'system-log', 'View Log'],
  ['/system/updates', 'system-updates', 'Check For Updates'],
  ['/system/restart', 'system-restart', 'Restart'],
  ['/system/shutdown', 'system-shutdown', 'Shutdown'],
]

const stubRoutes: RouteRecordRaw[] = stub.map(([path, name, title]) => ({
  path,
  name,
  component: placeholder,
  meta: { title },
}))

const router = createRouter({
  history: createWebHistory(),
  routes: [...realRoutes, ...stubRoutes],
})

// Reactive auth: the guard never forces the login page. If the server requires
// auth, a protected API call returns 401 and the API client redirects to login
// (see api/client.ts). When auth is disabled the server never 401s, so login can
// never appear, regardless of network timing. This avoids the startup race where
// a slow "is login required?" check let the login page show first.
router.beforeEach((to) => {
  const auth = useAuthStore()
  // Keep users off the login page when login isn't required.
  if (to.name === 'login' && auth.authEnabled === false) {
    return { name: 'shows' }
  }
  return true
})

export default router
