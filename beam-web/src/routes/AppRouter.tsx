import { Route, Routes } from 'react-router-dom'

import { AppLayout } from '../layouts/AppLayout'
import { PublicLayout } from '../layouts/PublicLayout'
import { AnalysisPage } from '../pages/AnalysisPage'
import { DashboardPage } from '../pages/DashboardPage'
import { HistoryPage } from '../pages/HistoryPage'
import { LandingPage } from '../pages/LandingPage'
import { LoginPage } from '../pages/LoginPage'
import { NotFoundPage } from '../pages/NotFoundPage'
import { ProfilePage } from '../pages/ProfilePage'
import { RegisterPage } from '../pages/RegisterPage'
import { SettingsPage } from '../pages/SettingsPage'
import { ProtectedRoute } from './ProtectedRoute'
import { PublicRoute } from './PublicRoute'

export function AppRouter() {
  return (
    <Routes>
      <Route element={<PublicRoute />}>
        <Route element={<PublicLayout />}>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Route>

      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/analysis" element={<AnalysisPage />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Route>
      </Route>
    </Routes>
  )
}