import { useApi } from '@/hooks/useApi'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Phone, Bot, Clock, TrendingUp, Activity } from 'lucide-react'

interface SummaryData {
  total_calls: number
  total_agents: number
  avg_duration_seconds: number
  calls_today: number
  calls_this_week: number
  provider_health: Record<string, string>
  recent_calls: any[]
}

function StatCard({ title, value, subtitle, icon: Icon }: {
  title: string
  value: string | number
  subtitle?: string
  icon: any
}) {
  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <p className="text-sm text-muted-foreground">{title}</p>
            <p className="text-2xl font-bold">{value}</p>
            {subtitle && <p className="text-xs text-muted-foreground">{subtitle}</p>}
          </div>
          <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
            <Icon className="w-5 h-5 text-primary" />
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

function StatusBadge({ status }: { status: string }) {
  const color = status === 'healthy' ? 'bg-green-500/10 text-green-600' :
    status === 'degraded' ? 'bg-yellow-500/10 text-yellow-600' :
    'bg-red-500/10 text-red-600'
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium ${color}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${status === 'healthy' ? 'bg-green-500' : status === 'degraded' ? 'bg-yellow-500' : 'bg-red-500'}`} />
      {status}
    </span>
  )
}

export default function Dashboard() {
  const { data, loading } = useApi<SummaryData>('/api/v1/analytics/summary')

  if (loading || !data) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground">Loading platform overview...</p>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map(i => (
            <Card key={i}><CardContent className="p-6"><div className="h-16 bg-muted animate-pulse rounded" /></CardContent></Card>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground">Platform overview and key metrics</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Total Calls" value={data.total_calls} subtitle={`+${data.calls_today} today`} icon={Phone} />
        <StatCard title="Active Agents" value={data.total_agents} icon={Bot} />
        <StatCard title="Avg Duration" value={`${Math.round(data.avg_duration_seconds / 60)}m`} icon={Clock} />
        <StatCard title="This Week" value={data.calls_this_week} icon={TrendingUp} />
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Activity className="w-4 h-4" />
            Provider Health
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-3">
            {Object.entries(data.provider_health).map(([name, status]) => (
              <div key={name} className="flex items-center gap-2 px-3 py-2 rounded-lg border bg-card">
                <span className="text-sm font-medium capitalize">{name}</span>
                <StatusBadge status={status} />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Phone className="w-4 h-4" />
            Recent Calls
          </CardTitle>
        </CardHeader>
        <CardContent>
          {data.recent_calls.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-8">No calls yet</p>
          ) : (
            <div className="space-y-2">
              {data.recent_calls.slice(0, 5).map((call: any) => (
                <div key={call.id} className="flex items-center justify-between py-2 px-3 rounded-lg hover:bg-muted/50 transition-colors">
                  <div className="flex items-center gap-3">
                    <div className={`w-2 h-2 rounded-full ${call.status === 'completed' ? 'bg-green-500' : call.status === 'in_progress' ? 'bg-blue-500' : 'bg-gray-400'}`} />
                    <div>
                      <p className="text-sm font-medium">{call.phone_number || 'Test Call'}</p>
                      <p className="text-xs text-muted-foreground capitalize">{call.direction} &middot; {call.status}</p>
                    </div>
                  </div>
                  <span className="text-xs text-muted-foreground">
                    {call.duration_seconds ? `${Math.round(call.duration_seconds / 60)}m` : '-'}
                  </span>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
