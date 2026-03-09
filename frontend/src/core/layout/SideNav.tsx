import type React from 'react'
import { NavLink } from 'react-router-dom'
import {
  Box,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
  Divider,
} from '@mui/material'
import BarChartIcon from '@mui/icons-material/BarChart'
import BusinessIcon from '@mui/icons-material/Business'
import ScienceIcon from '@mui/icons-material/Science'
import PeopleIcon from '@mui/icons-material/People'
import BiotechIcon from '@mui/icons-material/Biotech'
import { useAuthStore } from '../../modules/auth/authStore'
import { hasRole } from '../../types'

const NAV_ITEMS: { label: string; path: string; icon: React.ReactNode }[] = [
  { label: 'Visualize', path: '/visualize', icon: <BarChartIcon fontSize="small" /> },
]

const ADMIN_ITEMS = [
  {
    label: 'Companies',
    path: '/admin/companies',
    icon: <BusinessIcon fontSize="small" />,
    minRole: 'super_admin' as const,
  },
  {
    label: 'Labs',
    path: '/admin/labs',
    icon: <ScienceIcon fontSize="small" />,
    minRole: 'company_admin' as const,
  },
  {
    label: 'Users',
    path: '/admin/users',
    icon: <PeopleIcon fontSize="small" />,
    minRole: 'lab_admin' as const,
  },
  {
    label: 'Instruments',
    path: '/admin/instruments',
    icon: <BiotechIcon fontSize="small" />,
    minRole: 'lab_admin' as const,
  },
]

const navItemSx = {
  mx: 1,
  borderRadius: 1.5,
  mb: 0.25,
  '&.active': {
    bgcolor: 'primary.main',
    color: 'primary.contrastText',
    '& .MuiListItemIcon-root': { color: 'primary.contrastText' },
  },
}

export default function SideNav() {
  const { profile } = useAuthStore()
  const role = profile?.role ?? 'member'

  const visibleAdminItems = ADMIN_ITEMS.filter((item) => hasRole(role, item.minRole))

  return (
    <Box
      sx={{
        width: 220,
        flexShrink: 0,
        display: 'flex',
        flexDirection: 'column',
        borderRight: 1,
        borderColor: 'divider',
        bgcolor: 'background.paper',
        height: '100%',
      }}
    >
      {/* Logo */}
      <Box sx={{ px: 2.5, py: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Typography variant="h6" fontWeight={800} color="primary" letterSpacing={-0.5}>
          Benchpress
        </Typography>
      </Box>

      {/* Main nav */}
      <List dense disablePadding sx={{ pt: 1 }}>
        {NAV_ITEMS.map((item) => (
          <ListItemButton key={item.path} component={NavLink} to={item.path} sx={navItemSx}>
            <ListItemIcon sx={{ minWidth: 32 }}>{item.icon}</ListItemIcon>
            <ListItemText primary={item.label} primaryTypographyProps={{ fontSize: 13, fontWeight: 500 }} />
          </ListItemButton>
        ))}
      </List>

      {/* Admin section */}
      {visibleAdminItems.length > 0 && (
        <>
          <Divider sx={{ mx: 2, mt: 1 }} />
          <Typography
            variant="overline"
            sx={{ px: 2.5, pt: 1.5, pb: 0.5, fontSize: 10, color: 'text.disabled', letterSpacing: 1.5 }}
          >
            Admin
          </Typography>
          <List dense disablePadding>
            {visibleAdminItems.map((item) => (
              <ListItemButton key={item.path} component={NavLink} to={item.path} sx={navItemSx}>
                <ListItemIcon sx={{ minWidth: 32 }}>{item.icon}</ListItemIcon>
                <ListItemText primary={item.label} primaryTypographyProps={{ fontSize: 13, fontWeight: 500 }} />
              </ListItemButton>
            ))}
          </List>
        </>
      )}

      <Box sx={{ flex: 1 }} />
    </Box>
  )
}
