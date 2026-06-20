/**
 * Single source of truth for navigation, modelled on the classic SickChill top
 * menu (Shows / Schedule / History / Manage / Config / System).
 *
 * Both the desktop top-bar and the mobile drawer render from THIS list, so every
 * destination available on desktop is automatically available on mobile.
 */

export interface MenuLink {
  label: string
  icon: string
  route?: string // vue-router route name
  action?: 'logout' // non-navigation action
}

export interface MenuGroup {
  key: string
  label: string
  icon: string
  route?: string // direct link when there are no children
  children?: MenuLink[]
}

export const MENU: MenuGroup[] = [
  {
    key: 'shows',
    label: 'Shows',
    icon: '📺',
    children: [
      { label: 'Show List', icon: '📺', route: 'shows' },
      { label: 'Add Shows', icon: '➕', route: 'add-shows' },
      { label: 'Manual Post-Processing', icon: '🔄', route: 'post-process' },
    ],
  },
  { key: 'schedule', label: 'Schedule', icon: '🗓️', route: 'schedule' },
  { key: 'history', label: 'History', icon: '🕘', route: 'history' },
  {
    key: 'manage',
    label: 'Manage',
    icon: '🛠️',
    children: [
      { label: 'Mass Update', icon: '✏️', route: 'manage' },
      { label: 'Backlog Overview', icon: '🔭', route: 'manage-backlog' },
      { label: 'Manage Searches', icon: '🔎', route: 'manage-searches' },
      { label: 'Episode Status Management', icon: '⚖️', route: 'manage-episode-status' },
      { label: 'Failed Downloads', icon: '👎', route: 'manage-failed' },
      { label: 'Missed Subtitles', icon: '💬', route: 'manage-subtitles' },
    ],
  },
  {
    key: 'config',
    label: 'Config',
    icon: '⚙️',
    children: [
      { label: 'General', icon: '⚙️', route: 'settings' },
      { label: 'Search Settings', icon: '🔍', route: 'config-search' },
      { label: 'Search Providers', icon: '🔌', route: 'config-providers' },
      { label: 'Subtitles', icon: '💬', route: 'config-subtitles' },
      { label: 'Post Processing', icon: '🔄', route: 'config-postprocessing' },
      { label: 'Notifications', icon: '🔔', route: 'config-notifications' },
    ],
  },
  {
    key: 'system',
    label: 'System',
    icon: '🖥️',
    children: [
      { label: 'Server Status', icon: '📊', route: 'system-status' },
      { label: 'View Log', icon: '📄', route: 'system-log' },
      { label: 'Check For Updates', icon: '🔧', route: 'system-updates' },
      { label: 'Restart', icon: '🔁', route: 'system-restart' },
      { label: 'Shutdown', icon: '⏻', route: 'system-shutdown' },
      { label: 'Sign out', icon: '🚪', action: 'logout' },
    ],
  },
]

/** Route names shown in the mobile bottom bar (the rest live in the drawer). */
export const MOBILE_PRIMARY: string[] = ['shows', 'schedule', 'history']
