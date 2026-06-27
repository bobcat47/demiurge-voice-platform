import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { CheckCircle, XCircle, AlertCircle, Server, Brain, Mic, Phone, Radio } from 'lucide-react'
import { useApi } from '@/hooks/useApi'

interface ProviderHealth {
  llm: { status: string; error?: string }
  stt: { status: string; error?: string }
  tts: { status: string; error?: string }
  telephony: { status: string; error?: string }
  livekit: { status: string; configured?: boolean }
  pipecat: { status: string; configured?: boolean }
}

interface ProviderConfig {
  llm: { active: string; model: string; available: any[] }
  stt: { active: string; model: string }
  tts: { active: string; voice: string }
  telephony: { active: string }
  livekit: { configured: boolean; url: string | null }
  pipecat: { configured: boolean }
}

function StatusIcon({ status }: { status: string }) {
  if (status === 'healthy' || status === 'available' || status === 'mocked') return <CheckCircle className="w-4 h-4 text-green-500" />
  if (status === 'degraded') return <AlertCircle className="w-4 h-4 text-yellow-500" />
  return <XCircle className="w-4 h-4 text-red-500" />
}

export default function Settings() {
  const { data: health } = useApi<ProviderHealth>('/api/v1/providers/health')
  const { data: config } = useApi<ProviderConfig>('/api/v1/providers')

  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h1 className="text-2xl font-bold">Settings</h1>
        <p className="text-muted-foreground">Provider configuration and system status</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Server className="w-4 h-4" />
            Provider Health
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {health && Object.entries(health).map(([name, data]) => (
            <div key={name} className="flex items-center justify-between py-2">
              <div className="flex items-center gap-3">
                <StatusIcon status={data.status} />
                <span className="text-sm font-medium capitalize">{name}</span>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant={data.status === 'healthy' || data.status === 'available' || data.status === 'mocked' ? 'outline' : 'secondary'} className="text-xs capitalize">
                  {data.status}
                </Badge>
                {(data as any).configured !== undefined && (
                  <span className="text-xs text-muted-foreground">
                    {(data as any).configured ? 'Configured' : 'Not Configured'}
                  </span>
                )}
              </div>
            </div>
          ))}
          {!health && (
            <div className="space-y-2">
              {[1, 2, 3, 4, 5, 6].map(i => (
                <div key={i} className="h-8 bg-muted animate-pulse rounded" />
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Server className="w-4 h-4" />
            Provider Configuration
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Brain className="w-4 h-4 text-primary" />
              <h3 className="text-sm font-medium">LLM</h3>
            </div>
            <div className="grid grid-cols-2 gap-4 text-sm pl-6">
              <div>
                <span className="text-muted-foreground">Provider:</span>
                <span className="ml-2 font-medium">{config?.llm?.active || '-'}</span>
              </div>
              <div>
                <span className="text-muted-foreground">Model:</span>
                <span className="ml-2 font-medium">{config?.llm?.model || '-'}</span>
              </div>
              <div className="col-span-2">
                <span className="text-muted-foreground">Available:</span>
                <div className="flex flex-wrap gap-1 mt-1">
                  {config?.llm?.available?.map((p: any) => (
                    <Badge key={p.name} variant={p.configured ? 'default' : 'secondary'} className="text-xs">
                      {p.name}
                    </Badge>
                  )) || '-'}
                </div>
              </div>
            </div>
          </div>

          <Separator />

          <div>
            <div className="flex items-center gap-2 mb-2">
              <Mic className="w-4 h-4 text-primary" />
              <h3 className="text-sm font-medium">STT</h3>
            </div>
            <div className="grid grid-cols-2 gap-4 text-sm pl-6">
              <div>
                <span className="text-muted-foreground">Provider:</span>
                <span className="ml-2 font-medium">{config?.stt?.active || '-'}</span>
              </div>
              <div>
                <span className="text-muted-foreground">Model:</span>
                <span className="ml-2 font-medium">{config?.stt?.model || '-'}</span>
              </div>
            </div>
          </div>

          <Separator />

          <div>
            <div className="flex items-center gap-2 mb-2">
              <Phone className="w-4 h-4 text-primary" />
              <h3 className="text-sm font-medium">TTS</h3>
            </div>
            <div className="grid grid-cols-2 gap-4 text-sm pl-6">
              <div>
                <span className="text-muted-foreground">Provider:</span>
                <span className="ml-2 font-medium">{config?.tts?.active || '-'}</span>
              </div>
              <div>
                <span className="text-muted-foreground">Voice:</span>
                <span className="ml-2 font-medium">{config?.tts?.voice || '-'}</span>
              </div>
            </div>
          </div>

          <Separator />

          <div>
            <div className="flex items-center gap-2 mb-2">
              <Radio className="w-4 h-4 text-primary" />
              <h3 className="text-sm font-medium">Telephony</h3>
            </div>
            <div className="text-sm pl-6">
              <span className="text-muted-foreground">Provider:</span>
              <span className="ml-2 font-medium">{config?.telephony?.active || '-'}</span>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Environment</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-muted-foreground">Platform:</span>
              <span className="ml-2 font-medium">Demiurge Voice Platform v0.1.0</span>
            </div>
            <div>
              <span className="text-muted-foreground">API Docs:</span>
              <span className="ml-2 font-medium">/docs (debug mode only)</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
