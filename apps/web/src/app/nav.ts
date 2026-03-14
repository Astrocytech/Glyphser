import {
  BadgeCheck,
  FileSearch,
  FolderTree,
  LayoutDashboard,
  Settings,
} from 'lucide-react'

export const navItems = [
  {
    to: '/',
    label: 'Dashboard',
    title: 'Dashboard',
    icon: LayoutDashboard,
  },
  {
    to: '/verify',
    label: 'Verify',
    title: 'Verify',
    icon: BadgeCheck,
  },
  {
    to: '/runs',
    label: 'Runs',
    title: 'Runs',
    icon: FileSearch,
  },
  {
    to: '/artifacts',
    label: 'Artifacts',
    title: 'Artifacts',
    icon: FolderTree,
  },
  {
    to: '/settings',
    label: 'Settings',
    title: 'Settings',
    icon: Settings,
  },
] as const
