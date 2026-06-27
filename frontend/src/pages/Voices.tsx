import { useState } from 'react'
import { useApi } from '@/hooks/useApi'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { AudioWaveform, Search, Play } from 'lucide-react'

interface Voice {
  id: string
  provider: string
  name: string
  language: string
  gender: string | null
  sample_url: string | null
  enabled: boolean
  created_at: string
}

export default function Voices() {
  const { data: voices, loading } = useApi<Voice[]>('/api/v1/voices')
  const [search, setSearch] = useState('')

  const filtered = voices?.filter(v =>
    v.name.toLowerCase().includes(search.toLowerCase()) ||
    v.provider.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Voices</h1>
        <p className="text-muted-foreground">TTS voice presets and configuration</p>
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
        <Input placeholder="Search voices..." value={search} onChange={e => setSearch(e.target.value)} className="pl-10" />
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map(i => <Card key={i}><CardContent className="p-6"><div className="h-16 bg-muted animate-pulse rounded" /></CardContent></Card>)}
        </div>
      ) : filtered?.length === 0 ? (
        <Card><CardContent className="p-12 text-center">
          <AudioWaveform className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
          <p className="text-muted-foreground">No voice presets configured</p>
        </CardContent></Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered?.map(voice => (
            <Card key={voice.id}>
              <CardContent className="p-5">
                <div className="flex items-start justify-between mb-3">
                  <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                    <AudioWaveform className="w-5 h-5 text-primary" />
                  </div>
                  <Badge variant={voice.enabled ? 'default' : 'secondary'}>
                    {voice.enabled ? 'Active' : 'Inactive'}
                  </Badge>
                </div>
                <h3 className="font-semibold">{voice.name}</h3>
                <div className="flex items-center gap-2 mt-2 text-xs text-muted-foreground">
                  <span className="px-2 py-0.5 rounded bg-muted">{voice.provider}</span>
                  <span className="px-2 py-0.5 rounded bg-muted">{voice.language}</span>
                  {voice.gender && <span className="px-2 py-0.5 rounded bg-muted capitalize">{voice.gender}</span>}
                </div>
                {voice.sample_url && (
                  <button className="mt-3 flex items-center gap-1 text-xs text-primary hover:underline">
                    <Play className="w-3 h-3" /> Play Sample
                  </button>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
