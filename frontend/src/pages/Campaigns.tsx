import { useState } from 'react'
import { useApi, apiPost } from '@/hooks/useApi'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Radio, Plus, Search, Play, Pause } from 'lucide-react'

interface Campaign {
  id: string
  name: string
  agent_id: string | null
  target_source: string
  status: string
  schedule: Record<string, any>
  created_at: string
}

const statusColors: Record<string, string> = {
  draft: 'secondary',
  scheduled: 'outline',
  running: 'default',
  paused: 'secondary',
  completed: 'outline',
}

export default function Campaigns() {
  const { data: campaigns, loading, refetch } = useApi<Campaign[]>('/api/v1/campaigns')
  const [search, setSearch] = useState('')
  const [open, setOpen] = useState(false)
  const [creating, setCreating] = useState(false)

  const filtered = campaigns?.filter(c =>
    c.name.toLowerCase().includes(search.toLowerCase())
  )

  async function handleCreate(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setCreating(true)
    const form = new FormData(e.currentTarget)
    try {
      await apiPost('/api/v1/campaigns', {
        name: form.get('name'),
        agent_id: form.get('agent_id') || null,
        target_source: form.get('target_source'),
        status: 'draft',
        schedule: {},
      })
      setOpen(false)
      refetch()
    } catch {
      alert('Failed to create campaign')
    } finally {
      setCreating(false)
    }
  }

  async function handleAction(campaignId: string, action: 'start' | 'pause') {
    try {
      await apiPost(`/api/v1/campaigns/${campaignId}/${action}`, {})
      refetch()
    } catch {
      alert(`Failed to ${action} campaign`)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Campaigns</h1>
          <p className="text-muted-foreground">Outbound call campaigns</p>
        </div>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button><Plus className="w-4 h-4 mr-2" />New Campaign</Button>
          </DialogTrigger>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle>Create Campaign</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleCreate} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Name *</Label>
                <Input id="name" name="name" required placeholder="e.g. Q4 Outreach" />
              </div>
              <div className="space-y-2">
                <Label>Target Source</Label>
                <Select name="target_source" defaultValue="manual">
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="manual">Manual Upload</SelectItem>
                    <SelectItem value="csv">CSV Import</SelectItem>
                    <SelectItem value="api">API Source</SelectItem>
                    <SelectItem value="lead_intel">Lead Intelligence</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Button type="submit" className="w-full" disabled={creating}>
                {creating ? 'Creating...' : 'Create Campaign'}
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
        <Input placeholder="Search campaigns..." value={search} onChange={e => setSearch(e.target.value)} className="pl-10" />
      </div>

      {loading ? (
        <div className="space-y-3">
          {[1, 2].map(i => <Card key={i}><CardContent className="p-4"><div className="h-12 bg-muted animate-pulse rounded" /></CardContent></Card>)}
        </div>
      ) : filtered?.length === 0 ? (
        <Card><CardContent className="p-12 text-center">
          <Radio className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
          <p className="text-muted-foreground">No campaigns yet</p>
        </CardContent></Card>
      ) : (
        <div className="space-y-3">
          {filtered?.map(campaign => (
            <Card key={campaign.id}>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                      <Radio className="w-5 h-5 text-primary" />
                    </div>
                    <div>
                      <p className="font-medium">{campaign.name}</p>
                      <div className="flex items-center gap-2 mt-1 text-xs text-muted-foreground">
                        <Badge variant={statusColors[campaign.status] as any || 'secondary'} className="capitalize">
                          {campaign.status}
                        </Badge>
                        <span className="capitalize">{campaign.target_source.replace('_', ' ')}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {campaign.status === 'draft' || campaign.status === 'paused' ? (
                      <Button size="sm" variant="outline" onClick={() => handleAction(campaign.id, 'start')}>
                        <Play className="w-3 h-3 mr-1" /> Start
                      </Button>
                    ) : campaign.status === 'running' ? (
                      <Button size="sm" variant="outline" onClick={() => handleAction(campaign.id, 'pause')}>
                        <Pause className="w-3 h-3 mr-1" /> Pause
                      </Button>
                    ) : null}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
