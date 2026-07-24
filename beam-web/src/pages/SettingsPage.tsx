import { useState } from 'react'

import { Button } from '../components/Button'
import { Card } from '../components/Card'
import { SectionHeading } from '../components/SectionHeading'
import { useTheme } from '../hooks/useTheme'

export function SettingsPage() {
  const { theme, toggleTheme } = useTheme()
  const [emailNotifications, setEmailNotifications] = useState(true)

  return (
    <div className="space-y-8">
      <SectionHeading
        eyebrow="Settings"
        title="Application preferences"
        description="Keep the UI comfortable for long research sessions with theme support and a few user-facing toggles."
      />

      <div className="grid gap-5 lg:grid-cols-2">
        <Card className="space-y-4">
          <h3 className="text-lg font-semibold text-slate-950 dark:text-white">Appearance</h3>
          <p className="text-sm leading-7 text-slate-600 dark:text-slate-300">
            Current theme: <span className="font-semibold capitalize">{theme}</span>
          </p>
          <Button variant="secondary" onClick={toggleTheme}>
            Toggle theme
          </Button>
        </Card>

        <Card className="space-y-4">
          <h3 className="text-lg font-semibold text-slate-950 dark:text-white">Notifications</h3>
          <p className="text-sm leading-7 text-slate-600 dark:text-slate-300">
            These controls are placeholders for the production settings surface.
          </p>
          <label className="flex items-center justify-between gap-4 rounded-2xl border border-slate-200 px-4 py-3 dark:border-slate-800">
            <span className="text-sm font-medium text-slate-700 dark:text-slate-200">Email notifications</span>
            <input
              type="checkbox"
              checked={emailNotifications}
              onChange={(event) => setEmailNotifications(event.target.checked)}
              className="h-4 w-4 rounded border-slate-300 text-sky-500 focus:ring-sky-500"
            />
          </label>
        </Card>
      </div>
    </div>
  )
}