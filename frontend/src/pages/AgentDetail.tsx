import { useState } from 'react'
import { useParams, useNavigate } from 'react-router'
import { useApi, apiPut, apiDelete } from '@/hooks/useApi'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Switch } from '@/components/ui/switch'
import { ArrowLeft, Bot, Save, Trash2, Phone, MessageSquare } from 'lucide-react'

interface Agent {
  id: string
  name: string
  description: string
  system_prompt: string
  product_key: string | null
  squad_key: string | null
  llm_provider: string
  llm_model: string
  voice_provider: string
  voice_id: string
  stt_provider: string
  tts_provider: string
  language: string
  tools_enabled: string[]
  memory_enabled: boolean
  active: boolean
  metadata: Record<string, any>
  created_at: string
  updated_at: string
}

export default function AgentDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { data: agent, loading, refetch } = useApi<Agent>(`/api/v1/agents/${id}`)
  const [saving, setSaving] = useState(false)
  const [testText, setTestText] = useState('')
  const [testResponse, setTestResponse] = useState('')
  const [testing, setTesting] = useState(false)

  async function handleSave(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setSaving(true)
    const form = new FormData(e.currentTarget)
    try {
      await apiPut(`/api/v1/agents/${id}`, {
        name: form.get('name'),
        description: form.get('description'),
        system_prompt: form.get('system_prompt'),
        llm_model: form.get('llm_model'),
        voice_id: form.get('voice_id'),
        active: form.get('active') === 'on',
        memory_enabled: form.get('memory_enabled') === 'on',
      })
      refetch()
    } catch {
      alert('Failed to save')
    } finally {
      setSaving(false)
    }
  }

  async function handleDelete() {
    if (!confirm('Deactivate this agent?')) return
    try {
      await apiDelete(`/api/v1/agents/${id}`)
      navigate('/agents')
    } catch {
      alert('Failed to delete')
    }
  }

  async function handleTest() {
    if (!testText.trim()) return
    setTesting(true)
    setTestResponse('')
    try {
      const callRes = await fetch('/api/v1/calls', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ agent_id: id, direction: 'test', status: 'in_progress' }),
      })
      const call = await callRes.json()

      await fetch(`/api/v1/calls/${call.id}/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ agent_id: id, direction: 'test' }),
      })

      const turnRes = await fetch(`/api/v1/calls/${call.id}/text-turn`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: testText }),
      })
      const turn = await turnRes.json()
      setTestResponse(turn.response || 'No response')

      await fetch(`/api/v1/calls/${call.id}/end`, { method: 'POST' })
    } catch (err: any) {
      setTestResponse(`Error: ${err.message}`)
    } finally {
      setTesting(false)
    }
  }

  if (loading || !agent) {
    return (
      <div className="space-y-6">
        <Button variant="ghost" onClick={() => navigate('/agents')}><ArrowLeft className="w-4 h-4 mr-2" />Back</Button>
        <Card><CardContent className="p-12 text-center"><div className="h-8 bg-muted animate-pulse rounded w-1/3 mx-auto" /></CardContent></Card>
      </div>
    )
  }

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="sm" onClick={() => navigate('/agents')}><ArrowLeft className="w-4 h-4" /></Button>
          <div>
            <h1 className="text-2xl font-bold flex items-center gap-2">
              <Bot className="w-6 h-6 text-primary" />
              {agent.name}
            </h1>
            <p className="text-muted-foreground text-sm">{agent.description || 'No description'}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant={agent.active ? 'default' : 'secondary'}>
            {agent.active ? 'Active' : 'Inactive'}
          </Badge>
          <Button variant="destructive" size="sm" onClick={handleDelete}><Trash2 className="w-4 h-4" /></Button>
        </div>
      </div>

      <Tabs defaultValue="general">
        <TabsList>
          <TabsTrigger value="general">General</TabsTrigger>
          <TabsTrigger value="prompt">Prompt</TabsTrigger>
          <TabsTrigger value="providers">Providers</TabsTrigger>
          <TabsTrigger value="test">Test</TabsTrigger>
        </TabsList>

        <TabsContent value="general">
          <form onSubmit={handleSave}>
            <Card>
              <CardContent className="p-6 space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="name">Name</Label>
                    <Input id="name" name="name" defaultValue={agent.name} />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="description">Description</Label>
                    <Input id="description" name="description" defaultValue={agent.description || ''} />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="product_key">Product Key</Label>
                    <Input id="product_key" name="product_key" defaultValue={agent.product_key || ''} />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="squad_key">Squad Key</Label>
                    <Input id="squad_key" name="squad_key" defaultValue={agent.squad_key || ''} />
                  </div>
                </div>
                <div className="flex items-center gap-6 pt-2">
                  <div className="flex items-center gap-2">
                    <Switch id="active" name="active" defaultChecked={agent.active} />
                    <Label htmlFor="active">Active</Label>
                  </div>
                  <div className="flex items-center gap-2">
                    <Switch id="memory_enabled" name="memory_enabled" defaultChecked={agent.memory_enabled} />
                    <Label htmlFor="memory_enabled">Memory Enabled</Label>
                  </div>
                </div>
                <Button type="submit" disabled={saving}><Save className="w-4 h-4 mr-2" />{saving ? 'Saving...' : 'Save Changes'}</Button>
              </CardContent>
            </Card>
          </form>
        </TabsContent>

        <TabsContent value="prompt">
          <form onSubmit={handleSave}>
            <Card>
              <CardHeader><CardTitle>System Prompt</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                <Textarea
                  id="system_prompt"
                  name="system_prompt"
                  defaultValue={agent.system_prompt}
                  rows={12}
                  className="font-mono text-sm"
                />
                <Button type="submit" disabled={saving}><Save className="w-4 h-4 mr-2" />Save</Button>
              </CardContent>
            </Card>
          </form>
        </TabsContent>

        <TabsContent value="providers">
          <Card>
            <CardContent className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-muted-foreground">LLM Provider</Label>
                  <p className="font-medium">{agent.llm_provider}</p>
                </div>
                <div>
                  <Label className="text-muted-foreground">LLM Model</Label>
                  <Input name="llm_model" defaultValue={agent.llm_model} />
                </div>
                <div>
                  <Label className="text-muted-foreground">STT Provider</Label>
                  <p className="font-medium">{agent.stt_provider}</p>
                </div>
                <div>
                  <Label className="text-muted-foreground">TTS Provider</Label>
                  <p className="font-medium">{agent.tts_provider}</p>
                </div>
                <div>
                  <Label className="text-muted-foreground">Voice Provider</Label>
                  <p className="font-medium">{agent.voice_provider}</p>
                </div>
                <div>
                  <Label className="text-muted-foreground">Voice ID</Label>
                  <Input name="voice_id" defaultValue={agent.voice_id} />
                </div>
                <div>
                  <Label className="text-muted-foreground">Language</Label>
                  <p className="font-medium">{agent.language}</p>
                </div>
              </div>
              {agent.tools_enabled && agent.tools_enabled.length > 0 && (
                <div className="pt-4 border-t">
                  <Label className="text-muted-foreground mb-2 block">Enabled Tools ({agent.tools_enabled.length})</Label>
                  <div className="flex flex-wrap gap-2">
                    {agent.tools_enabled.map(t => (
                      <Badge key={t} variant="outline">{t}</Badge>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="test">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="w-4 h-4" />
                Text Chat Test
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Your Message</Label>
                <Textarea
                  value={testText}
                  onChange={e => setTestText(e.target.value)}
                  placeholder="Type a message to test this agent..."
                  rows={3}
                />
              </div>
              <Button onClick={handleTest} disabled={testing || !testText.trim()}>
                <Phone className="w-4 h-4 mr-2" />
                {testing ? 'Processing...' : 'Send Test Message'}
              </Button>
              {testResponse && (
                <div className="mt-4 p-4 rounded-lg bg-muted">
                  <Label className="text-xs text-muted-foreground mb-1 block">Agent Response</Label>
                  <p className="text-sm whitespace-pre-wrap">{testResponse}</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
