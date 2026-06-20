import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { getToken } from '@/api/client'

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
  ['/post-process', 'post-process', 'Manual Post-Processing'],
  ['/manage', 'manage', 'Mass Update'],
  ['/manage/backlog', 'manage-backlog', 'Backlog Overview'],
  ['/manage/searches', 'manage-searches', 'Manage Searches'],
  ['/manage/episode-status', 'manage-episode-status', 'Episode Status Management'],
  ['/manage/failed', 'manage-failed', 'Failed Downloads'],
  ['/manage/subtitles', 'manage-subtitles', 'Missed Subtitles'],
  ['/config/search', 'config-search', 'Search Settings'],
  ['/config/subtitles', 'config-subtitles', 'Subtitles'],
  ['/config/post-processing', 'config-postprocessing', 'Post Processing'],
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

// Global auth guard: everything except `public` routes requires a token.
router.beforeEach((to) => {
  if (!to.meta.public && !getToken()) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if (to.name === 'login' && getToken()) {
    return { name: 'shows' }
  }
})

export default router
