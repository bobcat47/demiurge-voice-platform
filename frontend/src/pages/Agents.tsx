import { useState } from 'react'
import { useNavigate } from 'react-router'
import { useApi, apiPost } from '@/hooks/useApi'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Bot, Plus, Search } from 'lucide-react'

interface Agent {
  id: string
  name: string
  description: string
  product_key: string | null
  llm_provider: string
  llm_model: string
  voice_provider: string
  active: boolean
  tools_enabled: string[]
  created_at: string
}

export default function Agents() {
  const navigate = useNavigate()
  const { data: agents, loading, refetch } = useApi<Agent[]>('/api/v1/agents')
  const [search, setSearch] = useState('')
  const [open, setOpen] = useState(false)
  const [creating, setCreating] = useState(false)

  const filtered = agents?.filter(a =>
    a.name.toLowerCase().includes(search.toLowerCase()) ||
    a.description?.toLowerCase().includes(search.toLowerCase())
  )

  async function handleCreate(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setCreating(true)
    const form = new FormData(e.currentTarget)
    try {
      await apiPost('/api/v1/agents', {
        name: form.get('name'),
        description: form.get('description'),
        system_prompt: form.get('system_prompt'),
        llm_provider: form.get('llm_provider'),
        llm_model: form.get('llm_model'),
        voice_provider: form.get('voice_provider'),
        tts_provider: form.get('voice_provider'),
        stt_provider: 'whisper',
        product_key: form.get('product_key'),
      })
      setOpen(false)
      refetch()
    } catch (err) {
      alert('Failed to create agent')
    } finally {
      setCreating(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Agents</h1>
          <p className="text-muted-foreground">Manage voice AI agents</p>
        </div>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button><Plus className="w-4 h-4 mr-2" />New Agent</Button>
          </DialogTrigger>
          <DialogContent className="max-w-lg max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Create Voice Agent</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleCreate} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Name *</Label>
                <Input id="name" name="name" required placeholder="e.g. Pharmacy Receptionist" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Input id="description" name="description" placeholder="What does this agent do?" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="product_key">Product Key</Label>
                <Input id="product_key" name="product_key" placeholder="e.g. lead-intel" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="system_prompt">System Prompt *</Label>
                <Textarea id="system_prompt" name="system_prompt" required rows={4}
                  defaultValue="You are a helpful voice assistant. Be concise and natural in your responses." />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>LLM Provider</Label>
                  <Select name="llm_provider" defaultValue="openrouter">
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="openrouter">OpenRouter</SelectItem>
                      <SelectItem value="gemini">Gemini</SelectItem>
                      <SelectItem value="groq">Groq</SelectItem>
                      <SelectItem value="openai">OpenAI</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="llm_model">Model</Label>
                  <Input id="llm_model" name="llm_model" defaultValue="google/gemini-2.0-flash-001" />
                </div>
              </div>
              <div className="space-y-2">
                <Label>Voice Provider</Label>
                <Select name="voice_provider" defaultValue="kokoro">
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="kokoro">Kokoro</SelectItem>
                    <SelectItem value="piper">Piper</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Button type="submit" className="w-full" disabled={creating}>
                {creating ? 'Creating...' : 'Create Agent'}
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
        <Input
          placeholder="Search agents..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="pl-10"
        />
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map(i => <Card key={i}><CardContent className="p-6"><div className="h-20 bg-muted animate-pulse rounded" /></CardContent></Card>)}
        </div>
      ) : filtered?.length === 0 ? (
        <Card><CardContent className="p-12 text-center">
          <Bot className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
          <p className="text-muted-foreground">No agents found</p>
          <Button variant="outline" className="mt-4" onClick={() => setOpen(true)}><Plus className="w-4 h-4 mr-2" />Create your first agent</Button>
        </CardContent></Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered?.map(agent => (
            <Card
              key={agent.id}
              className="cursor-pointer hover:border-primary/50 transition-colors"
              onClick={() => navigate(`/agents/${agent.id}`)}
            >
              <CardContent className="p-5">
                <div className="flex items-start justify-between mb-3">
                  <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                    <Bot className="w-5 h-5 text-primary" />
                  </div>
                  <Badge variant={agent.active ? 'default' : 'secondary'}>
                    {agent.active ? 'Active' : 'Inactive'}
                  </Badge>
                </div>
                <h3 className="font-semibold mb-1">{agent.name}</h3>
                <p className="text-sm text-muted-foreground line-clamp-2 mb-3">{agent.description || 'No description'}</p>
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <span className="px-2 py-0.5 rounded bg-muted">{agent.llm_provider}</span>
                  <span className="px-2 py-0.5 rounded bg-muted">{agent.voice_provider}</span>
                  {agent.product_key && <span className="px-2 py-0.5 rounded bg-muted">{agent.product_key}</span>}
                </div>
                {agent.tools_enabled && agent.tools_enabled.length > 0 && (
                  <div className="mt-2 text-xs text-muted-foreground">
                    {agent.tools_enabled.length} tool{agent.tools_enabled.length > 1 ? 's' : ''} enabled
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
