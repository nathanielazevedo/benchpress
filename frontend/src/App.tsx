import { useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { ThemeProvider, CssBaseline } from '@mui/material'
import { useAuthStore } from './modules/auth/authStore'
import { useThemeStore } from './core/themeStore'
import { lightTheme, darkTheme } from './core/theme'
import LoginPage from './modules/auth/LoginPage'
import MainLayout from './core/layout/MainLayout'
import SystemDesignerPage from './modules/designer/SystemDesignerPage'
import CompaniesPage from './modules/admin/CompaniesPage'
import LabsPage from './modules/admin/LabsPage'
import UsersPage from './modules/admin/UsersPage'

export default function App() {
  const { token, profile, fetchMe } = useAuthStore()
  const { mode } = useThemeStore()

  useEffect(() => {
    if (token && !profile) fetchMe()
  }, [token, profile, fetchMe])

  return (
    <ThemeProvider theme={mode === 'dark' ? darkTheme : lightTheme}>
      <CssBaseline />
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={token ? <Navigate to="/system-designer" /> : <LoginPage />} />
          <Route element={token ? <MainLayout /> : <Navigate to="/login" />}>
            <Route index element={<Navigate to="/system-designer" replace />} />
            <Route path="/system-designer" element={<SystemDesignerPage />} />
            <Route path="/admin/companies" element={<CompaniesPage />} />
            <Route path="/admin/labs" element={<LabsPage />} />
            <Route path="/admin/users" element={<UsersPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  )
}
