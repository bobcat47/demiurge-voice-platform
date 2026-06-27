import { useState } from 'react'
import { useApi } from '@/hooks/useApi'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Phone, Search, Clock, ArrowDownLeft, ArrowUpRight, Play } from 'lucide-react'

interface Call {
  id: string
  agent_id: string | null
  direction: string
  phone_number: string | null
  status: string
  transcript: string | null
  summary: string | null
  recording_url: string | null
  started_at: string | null
  ended_at: string | null
  duration_seconds: number | null
  created_at: string
}

const statusColors: Record<string, string> = {
  queued: 'bg-gray-500',
  ringing: 'bg-blue-500',
  in_progress: 'bg-green-500',
  completed: 'bg-green-600',
  failed: 'bg-red-500',
  cancelled: 'bg-gray-400',
}

export default function Calls() {
  const { data: calls, loading } = useApi<Call[]>('/api/v1/calls')
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')

  const filtered = calls?.filter(c => {
    const matchesSearch = !search ||
      c.phone_number?.includes(search) ||
      c.id.includes(search)
    const matchesStatus = statusFilter === 'all' || c.status === statusFilter
    return matchesSearch && matchesStatus
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Calls</h1>
          <p className="text-muted-foreground">Call history and transcripts</p>
        </div>
      </div>

      <div className="flex gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input placeholder="Search calls..." value={search} onChange={e => setSearch(e.target.value)} className="pl-10" />
        </div>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-40">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="queued">Queued</SelectItem>
            <SelectItem value="in_progress">In Progress</SelectItem>
            <SelectItem value="completed">Completed</SelectItem>
            <SelectItem value="failed">Failed</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3].map(i => <Card key={i}><CardContent className="p-4"><div className="h-12 bg-muted animate-pulse rounded" /></CardContent></Card>)}
        </div>
      ) : filtered?.length === 0 ? (
        <Card><CardContent className="p-12 text-center">
          <Phone className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
          <p className="text-muted-foreground">No calls found</p>
        </CardContent></Card>
      ) : (
        <div className="space-y-3">
          {filtered?.map(call => (
            <Card key={call.id} className="hover:border-primary/30 transition-colors">
              <CardContent className="p-4">
                <div className="flex items-center gap-4">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center ${call.direction === 'inbound' ? 'bg-blue-500/10' : call.direction === 'outbound' ? 'bg-orange-500/10' : 'bg-purple-500/10'}`}>
                    {call.direction === 'inbound' ? <ArrowDownLeft className="w-5 h-5 text-blue-500" /> :
                     call.direction === 'outbound' ? <ArrowUpRight className="w-5 h-5 text-orange-500" /> :
                     <Play className="w-5 h-5 text-purple-500" />}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <p className="font-medium">{call.phone_number || 'Test Call'}</p>
                      <Badge variant="outline" className="text-xs capitalize">{call.direction}</Badge>
                    </div>
                    <div className="flex items-center gap-3 mt-1 text-xs text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <span className={`w-2 h-2 rounded-full ${statusColors[call.status] || 'bg-gray-400'}`} />
                        {call.status}
                      </span>
                      {call.duration_seconds && (
                        <span className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {Math.round(call.duration_seconds / 60)}m {call.duration_seconds % 60}s
                        </span>
                      )}
                      <span>{new Date(call.created_at).toLocaleString()}</span>
                    </div>
                  </div>
                  {call.transcript && (
                    <Dialog>
                      <DialogTrigger asChild>
                        <Button variant="ghost" size="sm">View Transcript</Button>
                      </DialogTrigger>
                      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
                        <DialogHeader>
                          <DialogTitle>Call Transcript</DialogTitle>
                        </DialogHeader>
                        <div className="space-y-4">
                          <div className="p-3 rounded bg-muted font-mono text-sm whitespace-pre-wrap">
                            {call.transcript}
                          </div>
                          {call.summary && (
                            <div>
                              <Label className="text-muted-foreground">Summary</Label>
                              <p className="text-sm mt-1">{call.summary}</p>
                            </div>
                          )}
                        </div>
                      </DialogContent>
                    </Dialog>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
