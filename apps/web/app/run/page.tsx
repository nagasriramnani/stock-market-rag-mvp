"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Skeleton } from "@/components/ui/skeleton"
import { Spotlight } from "@/components/spotlight"
import { Sparkles, Loader2, CheckCircle2, XCircle } from "lucide-react"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

interface RunStatus {
  run_id: string
  status: "running" | "completed" | "failed"
  started_at?: string
  finished_at?: string
  errors: string[]
  artifacts: string[]
}

export default function RunPage() {
  const [tickers, setTickers] = useState("")
  const [hours, setHours] = useState(24)
  const [loading, setLoading] = useState(false)
  const [runId, setRunId] = useState<string | null>(null)
  const [runStatus, setRunStatus] = useState<RunStatus | null>(null)
  const router = useRouter()

  // Poll for run status
  useEffect(() => {
    if (!runId) return
    
    // Validate runId is a valid UUID format
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i
    if (!uuidRegex.test(runId)) {
      console.error("Invalid runId format:", runId)
      return
    }

    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(`${API_URL}/runs/${runId}`)
        if (response.ok) {
          const status: RunStatus = await response.json()
          setRunStatus(status)

          if (status.status === "completed" || status.status === "failed") {
            clearInterval(pollInterval)
            setLoading(false)
            if (status.status === "completed" && status.artifacts.length > 0) {
              setTimeout(() => {
                router.push("/reports")
              }, 2000)
            }
          }
        }
      } catch (error) {
        console.error("Error polling status:", error)
      }
    }, 2000) // Poll every 2 seconds

    return () => clearInterval(pollInterval)
  }, [runId, router])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setRunStatus(null)
    setRunId(null)

    try {
      const tickerList = tickers
        .split(",")
        .map((t) => t.trim().toUpperCase())
        .filter(Boolean)

      if (tickerList.length === 0) {
        alert("Please enter at least one ticker")
        setLoading(false)
        return
      }

      const response = await fetch(`${API_URL}/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tickers: tickerList,
          hours: parseInt(String(hours)) || 24,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || "Failed to start analysis")
      }

      const data = await response.json()
      setRunId(data.run_id)
      setRunStatus({
        run_id: data.run_id,
        status: "running",
        errors: data.errors || [],
        artifacts: data.artifacts || [],
      })
    } catch (error: any) {
      console.error("Error:", error)
      setRunStatus({
        run_id: "",
        status: "failed",
        errors: [error.message || String(error)],
        artifacts: [],
      })
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-black text-white relative overflow-hidden">
      <Spotlight />
      <div className="absolute inset-0 bg-grid-neon bg-[length:50px_50px] opacity-30" />

      <section className="relative z-10 max-w-2xl mx-auto px-6 py-16">
        <div className="glass-glow rounded-2xl p-8 md:p-12">
          <div className="flex items-center gap-2 mb-6">
            <Sparkles className="w-6 h-6 text-brand" />
            <h1 className="text-4xl font-semibold">Run Analysis</h1>
          </div>

          {!runId && (
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Tickers (comma-separated)
                </label>
                <Input
                  type="text"
                  placeholder="AAPL, MSFT, NVDA"
                  value={tickers}
                  onChange={(e) => setTickers(e.target.value)}
                  disabled={loading}
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Time Window (hours)
                </label>
                <Input
                  type="number"
                  min="1"
                  max="168"
                  value={hours}
                  onChange={(e) => setHours(parseInt(e.target.value) || 24)}
                  disabled={loading}
                />
              </div>

              <Button
                type="submit"
                size="lg"
                className="w-full"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Starting...
                  </>
                ) : (
                  "Start Analysis"
                )}
              </Button>
            </form>
          )}

          {runStatus && (
            <Card className="glass mt-8">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  {runStatus.status === "running" && (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin text-brand" />
                      Analysis Running...
                    </>
                  )}
                  {runStatus.status === "completed" && (
                    <>
                      <CheckCircle2 className="w-5 h-5 text-green-400" />
                      Analysis Complete
                    </>
                  )}
                  {runStatus.status === "failed" && (
                    <>
                      <XCircle className="w-5 h-5 text-red-400" />
                      Analysis Failed
                    </>
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="text-sm">
                  <span className="text-white/60">Run ID:</span>{" "}
                  <code className="text-brand">{runStatus.run_id}</code>
                </div>

                {runStatus.status === "running" && (
                  <div className="space-y-2">
                    <Skeleton className="h-4 w-full bg-white/10" />
                    <Skeleton className="h-4 w-3/4 bg-white/10" />
                    <Skeleton className="h-4 w-1/2 bg-white/10" />
                  </div>
                )}

                {runStatus.artifacts && runStatus.artifacts.length > 0 && (
                  <div>
                    <p className="text-sm font-medium mb-1">Artifacts:</p>
                    <ul className="list-disc list-inside text-sm text-brand">
                      {runStatus.artifacts.map((a: string, i: number) => (
                        <li key={i}>{a}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {runStatus.errors && runStatus.errors.length > 0 && (
                  <div className="text-red-400 text-sm">
                    <p className="font-medium mb-1">Errors:</p>
                    <ul className="list-disc list-inside">
                      {runStatus.errors.map((e: string, i: number) => (
                        <li key={i}>{e}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {runStatus.status === "completed" && runStatus.artifacts.length > 0 && (
                  <p className="text-sm text-brand animate-pulse">
                    Redirecting to reports...
                  </p>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      </section>
    </main>
  )
}
