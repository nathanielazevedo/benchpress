import { Box } from '@mui/material'
import { Outlet } from 'react-router-dom'
import SideNav from './SideNav'
import TopNav from './TopNav'

export default function MainLayout() {
  return (
    <Box sx={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
      <SideNav />
      <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <TopNav />
        <Box sx={{ flex: 1, overflow: 'hidden' }}>
          <Outlet />
        </Box>
      </Box>
    </Box>
  )
}
