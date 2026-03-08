import { useState } from 'react'
import { useLocation } from 'react-router-dom'
import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  IconButton,
  Tooltip,
  Menu,
  MenuItem,
  Avatar,
  Chip,
  Divider,
} from '@mui/material'
import DarkModeOutlinedIcon from '@mui/icons-material/DarkModeOutlined'
import LightModeOutlinedIcon from '@mui/icons-material/LightModeOutlined'
import { useAuthStore } from '../../modules/auth/authStore'
import { useThemeStore } from '../themeStore'

const PAGE_TITLES: Record<string, string> = {
  '/system-designer': 'System Designer',
  '/admin/companies': 'Companies',
  '/admin/labs': 'Labs',
  '/admin/users': 'Users',
}

const ROLE_LABELS: Record<string, string> = {
  super_admin: 'Super Admin',
  company_admin: 'Company Admin',
  lab_admin: 'Lab Admin',
  member: 'Member',
}

export default function TopNav() {
  const { profile, logout } = useAuthStore()
  const { mode, toggleMode } = useThemeStore()
  const { pathname } = useLocation()
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null)

  const pageTitle = PAGE_TITLES[pathname] ?? 'Benchpress'
  const initials = profile?.username?.slice(0, 2).toUpperCase() ?? '??'

  return (
    <AppBar
      position="static"
      elevation={0}
      sx={{
        bgcolor: 'background.paper',
        color: 'text.primary',
        borderBottom: 1,
        borderColor: 'divider',
        zIndex: 1,
      }}
    >
      <Toolbar variant="dense" sx={{ gap: 2 }}>
        <Typography variant="subtitle1" fontWeight={600} sx={{ flex: 1 }}>
          {pageTitle}
        </Typography>

        {/* Lab / Company breadcrumb */}
        {profile?.lab && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="caption" color="text.disabled">
              {profile.lab.company.name}
            </Typography>
            <Typography variant="caption" color="text.disabled">/</Typography>
            <Chip label={profile.lab.name} size="small" variant="outlined" sx={{ fontSize: 11 }} />
          </Box>
        )}

        {/* Theme toggle */}
        <Tooltip title={mode === 'dark' ? 'Light mode' : 'Dark mode'}>
          <IconButton size="small" onClick={toggleMode}>
            {mode === 'dark' ? <LightModeOutlinedIcon fontSize="small" /> : <DarkModeOutlinedIcon fontSize="small" />}
          </IconButton>
        </Tooltip>

        {/* User menu */}
        <Tooltip title={profile?.username ?? ''}>
          <IconButton size="small" onClick={(e) => setAnchorEl(e.currentTarget)}>
            <Avatar sx={{ width: 28, height: 28, fontSize: 12, bgcolor: 'primary.main' }}>
              {initials}
            </Avatar>
          </IconButton>
        </Tooltip>

        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={() => setAnchorEl(null)}
          transformOrigin={{ horizontal: 'right', vertical: 'top' }}
          anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
          slotProps={{ paper: { elevation: 2, sx: { minWidth: 180 } } }}
        >
          <Box sx={{ px: 2, py: 1 }}>
            <Typography variant="body2" fontWeight={600}>{profile?.username}</Typography>
            <Typography variant="caption" color="text.secondary">
              {ROLE_LABELS[profile?.role ?? 'member']}
            </Typography>
          </Box>
          <Divider />
          <MenuItem onClick={() => { logout(); setAnchorEl(null) }}>Sign out</MenuItem>
        </Menu>
      </Toolbar>
    </AppBar>
  )
}
