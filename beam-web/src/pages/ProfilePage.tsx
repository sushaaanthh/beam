import {
  User,
  Shield,
  Key,
  Database,
  Calendar,
  CheckCircle2,
  Mail,
  Sliders,
} from 'lucide-react'

import { Button } from '../components/Button'
import { Card } from '../components/Card'
import { UserAvatar } from '../components/UserAvatar'
import { useAuth } from '../hooks/useAuth'

export function ProfilePage() {
  const { user } = useAuth()
  const displayName = user?.username ?? 'Lead Researcher'
  const email = user?.email ?? 'researcher@beam-lab.org'

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="border-b border-[#1C1C1C] pb-4">
        <span className="text-[10px] font-mono text-[#C7FF4A] tracking-wider uppercase">
          WORKSPACE // ACCOUNT IDENTITY
        </span>
        <h1 className="font-display text-3xl sm:text-4xl font-bold text-[#F5F5F0] tracking-tight mt-1">
          RESEARCHER PROFILE
        </h1>
        <p className="text-xs sm:text-sm text-[#73736F] mt-1">
          Authenticated credentials, role permissions, and session authorization.
        </p>
      </div>

      {/* Main Profile Keycap Card */}
      <Card variant="default" padding="none" className="p-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6">
          <div className="flex items-center gap-4">
            <UserAvatar name={displayName} size="xl" />
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-display text-2xl font-bold text-[#F5F5F0]">
                  {displayName}
                </h3>
                <span className="font-mono text-[10px] text-[#C7FF4A] bg-[#141414] px-2 py-0.5 rounded border border-[#222222]">
                  VERIFIED_RESEARCHER
                </span>
              </div>
              <p className="text-xs text-[#B8B8B0] flex items-center gap-1.5 mt-1">
                <Mail className="h-3.5 w-3.5 text-[#73736F]" />
                {email}
              </p>
              <p className="text-[11px] font-mono text-[#73736F] mt-1">
                SESSION_ID: auth-jwt-prod-active
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Button variant="secondary" size="sm">
              Edit Profile
            </Button>
          </div>
        </div>
      </Card>

      {/* Metrics Row */}
      <div className="grid sm:grid-cols-3 gap-4">
        <Card variant="default" padding="none" className="p-4">
          <span className="text-[10px] font-mono text-[#73736F] uppercase">Account Created</span>
          <p className="font-display text-xl font-bold text-[#F5F5F0] mt-1">2026-01-15</p>
          <span className="text-[11px] text-[#73736F]">7 months active</span>
        </Card>
        <Card variant="default" padding="none" className="p-4">
          <span className="text-[10px] font-mono text-[#73736F] uppercase">Analyses Executed</span>
          <p className="font-display text-xl font-bold text-[#C7FF4A] mt-1">1,248</p>
          <span className="text-[11px] text-[#73736F]">Telemetry queries</span>
        </Card>
        <Card variant="default" padding="none" className="p-4">
          <span className="text-[10px] font-mono text-[#73736F] uppercase">Role Permissions</span>
          <p className="font-display text-xl font-bold text-[#F5F5F0] mt-1">Admin / Lab Lead</p>
          <span className="text-[11px] text-[#73736F]">Full transformer access</span>
        </Card>
      </div>

      {/* Security & Access */}
      <Card variant="default" padding="none" className="p-6 space-y-4">
        <div className="border-b border-[#1C1C1C] pb-3">
          <span className="text-[10px] font-mono text-[#73736F] uppercase">Security</span>
          <h4 className="font-display text-lg font-bold text-[#F5F5F0]">Authentication & Tokens</h4>
        </div>

        <div className="space-y-3 text-xs">
          <div className="flex items-center justify-between p-3 rounded-lg bg-[#0C0C0C] border border-[#1E1E1E]">
            <div>
              <p className="font-medium text-[#F5F5F0]">API Access Token</p>
              <p className="text-[#73736F] text-[11px]">Used for beam-api automated python batch telemetry</p>
            </div>
            <Button variant="secondary" size="sm">
              Generate New Token
            </Button>
          </div>

          <div className="flex items-center justify-between p-3 rounded-lg bg-[#0C0C0C] border border-[#1E1E1E]">
            <div>
              <p className="font-medium text-[#F5F5F0]">Password & Credentials</p>
              <p className="text-[#73736F] text-[11px]">Last rotated 30 days ago</p>
            </div>
            <Button variant="ghost" size="sm">
              Change Password
            </Button>
          </div>
        </div>
      </Card>
    </div>
  )
}