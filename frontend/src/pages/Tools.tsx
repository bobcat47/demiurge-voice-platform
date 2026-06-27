import { useState } from 'react'
import { useApi } from '@/hooks/useApi'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Wrench, Search, Play, ChevronDown, ChevronUp } from 'lucide-react'

interface ToolItem {
  name: string
  description: string
  input_schema: Record<string, any>
  output_schema: Record<string, any>
  enabled: boolean
}

export default function Tools() {
  const { data: builtinData } = useApi<{ tools: ToolItem[] }>('/api/v1/tools/builtin')
  const [search, setSearch] = useState('')
  const [expandedTool, setExpandedTool] = useState<string | null>(null)
  const [testParams, setTestParams] = useState('{}')
  const [testResult, setTestResult] = useState('')
  const [testing, setTesting] = useState(false)

  const builtinTools = builtinData?.tools || []

  const filtered = builtinTools.filter(t =>
    t.name.toLowerCase().includes(search.toLowerCase()) ||
    t.description.toLowerCase().includes(search.toLowerCase())
  )

  async function handleTest(toolName: string) {
    setTesting(true)
    setTestResult('')
    try {
      const params = JSON.parse(testParams)
      const res = await fetch(`/api/v1/tools/${toolName}/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params),
      })
      const data = await res.json()
      setTestResult(JSON.stringify(data, null, 2))
    } catch (e: any) {
      setTestResult(`Error: ${e.message}`)
    } finally {
      setTesting(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Tool Registry</h1>
        <p className="text-muted-foreground">Demiurge tools available to voice agents</p>
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
        <Input placeholder="Search tools..." value={search} onChange={e => setSearch(e.target.value)} className="pl-10" />
      </div>

      <div className="flex gap-4">
        <Card className="flex-1"><CardContent className="p-4 flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
            <Wrench className="w-4 h-4 text-primary" />
          </div>
          <div>
            <p className="text-lg font-bold">{builtinTools.length}</p>
            <p className="text-xs text-muted-foreground">Built-in Tools</p>
          </div>
        </CardContent></Card>
        <Card className="flex-1"><CardContent className="p-4 flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-green-500/10 flex items-center justify-center">
            <Wrench className="w-4 h-4 text-green-500" />
          </div>
          <div>
            <p className="text-lg font-bold">{builtinTools.filter(t => t.enabled).length}</p>
            <p className="text-xs text-muted-foreground">Enabled</p>
          </div>
        </CardContent></Card>
      </div>

      <div className="space-y-3">
        {filtered.map(tool => (
          <Card key={tool.name} className="overflow-hidden">
            <CardContent className="p-0">
              <button
                className="w-full flex items-center justify-between p-4 hover:bg-muted/30 transition-colors text-left"
                onClick={() => setExpandedTool(expandedTool === tool.name ? null : tool.name)}
              >
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                    <Wrench className="w-4 h-4 text-primary" />
                  </div>
                  <div>
                    <p className="font-medium font-mono text-sm">{tool.name}</p>
                    <p className="text-xs text-muted-foreground">{tool.description}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <Badge variant={tool.enabled ? 'default' : 'secondary'}>
                    {tool.enabled ? 'Enabled' : 'Disabled'}
                  </Badge>
                  {expandedTool === tool.name ? <ChevronUp className="w-4 h-4 text-muted-foreground" /> : <ChevronDown className="w-4 h-4 text-muted-foreground" />}
                </div>
              </button>

              {expandedTool === tool.name && (
                <div className="px-4 pb-4 border-t bg-muted/20">
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 pt-4">
                    <div>
                      <p className="text-xs font-medium text-muted-foreground mb-2">Input Schema</p>
                      <pre className="text-xs bg-muted p-3 rounded-lg overflow-auto max-h-48">
                        {JSON.stringify(tool.input_schema, null, 2)}
                      </pre>
                    </div>
                    <div>
                      <p className="text-xs font-medium text-muted-foreground mb-2">Output Schema</p>
                      <pre className="text-xs bg-muted p-3 rounded-lg overflow-auto max-h-48">
                        {JSON.stringify(tool.output_schema, null, 2)}
                      </pre>
                    </div>
                  </div>
                  <div className="mt-4 space-y-2">
                    <p className="text-xs font-medium text-muted-foreground">Test Tool</p>
                    <div className="flex gap-2">
                      <textarea
                        className="flex-1 min-h-[60px] p-2 text-xs font-mono bg-muted rounded-lg border resize-y"
                        value={testParams}
                        onChange={e => setTestParams(e.target.value)}
                        placeholder='{"key": "value"}'
                      />
                      <Button size="sm" onClick={() => handleTest(tool.name)} disabled={testing}>
                        <Play className="w-3 h-3 mr-1" />
                        {testing ? '...' : 'Run'}
                      </Button>
                    </div>
                    {testResult && (
                      <pre className="text-xs bg-muted p-3 rounded-lg overflow-auto max-h-40">
                        {testResult}
                      </pre>
                    )}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
