import { Card } from '../components/Card'
import { SectionHeading } from '../components/SectionHeading'
import { UserAvatar } from '../components/UserAvatar'
import { useAuth } from '../hooks/useAuth'

export function ProfilePage() {
  const { user } = useAuth()

  return (
    <div className="space-y-8">
      <SectionHeading
        eyebrow="Profile"
        title="Your account"
        description="The profile screen is wired to the authenticated user endpoint and will reflect the backend user record."
      />

      <Card className="flex flex-col gap-6 md:flex-row md:items-center">
        <UserAvatar name={user?.username ?? 'Researcher'} className="h-16 w-16 text-lg" />
        <div className="space-y-2">
          <h3 className="text-2xl font-semibold text-slate-950 dark:text-white">{user?.username ?? 'Researcher'}</h3>
          <p className="text-sm text-slate-600 dark:text-slate-300">{user?.email ?? 'Signed in with a secure JWT session'}</p>
          <p className="text-sm text-slate-500 dark:text-slate-400">Account status: {user?.is_active ? 'Active' : 'Inactive'}</p>
        </div>
      </Card>

      <div className="grid gap-5 md:grid-cols-3">
        {[
          { title: 'Role', value: 'Research user' },
          { title: 'Access', value: 'Protected session' },
          { title: 'Profile sync', value: 'Live from /users/me' },
        ].map((item) => (
          <Card key={item.title} className="space-y-2">
            <p className="text-sm text-slate-500 dark:text-slate-400">{item.title}</p>
            <p className="text-lg font-semibold text-slate-950 dark:text-white">{item.value}</p>
          </Card>
        ))}
      </div>
    </div>
  )
}