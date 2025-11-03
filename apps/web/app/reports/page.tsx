"use client"

import { useEffect, useState } from "react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Spotlight } from "@/components/spotlight"
import { ArrowRight, Download, FileText } from "lucide-react"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

interface ReportItem {
  path: string
  signed_url_md?: string
  signed_url_pdf?: string
  date: string
  tickers: string[]
}

export default function ReportsPage() {
  const [items, setItems] = useState<ReportItem[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState("")
  const bucket = process.env.NEXT_PUBLIC_REPORT_BUCKET || "reports"

  useEffect(() => {
    async function fetchReports() {
      try {
        const response = await fetch(`${API_URL}/reports`)
        if (!response.ok) {
          throw new Error("Failed to fetch reports")
        }
        const data: ReportItem[] = await response.json()
        setItems(data)
      } catch (error) {
        console.error("Error fetching reports:", error)
      } finally {
        setLoading(false)
      }
    }

    fetchReports()
  }, [])

  const filtered = items.filter(
    (item) =>
      !filter ||
      item.date.includes(filter) ||
      item.tickers.some((t) => t.toLowerCase().includes(filter.toLowerCase())) ||
      item.path.toLowerCase().includes(filter.toLowerCase())
  )

  return (
    <main className="min-h-screen bg-black text-white relative overflow-hidden">
      <Spotlight />
      <div className="absolute inset-0 bg-grid-neon bg-[length:50px_50px] opacity-30" />

      <section className="relative z-10 max-w-6xl mx-auto px-6 py-16">
        <div className="glass-glow rounded-2xl p-8 mb-8">
          <h1 className="text-4xl font-semibold mb-4">Reports</h1>
          <Input
            placeholder="Filter by date or ticker..."
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="max-w-md"
          />
        </div>

        {loading ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <Card key={i} className="animate-pulse">
                <CardHeader>
                  <div className="h-6 bg-white/10 rounded w-3/4" />
                </CardHeader>
                <CardContent>
                  <div className="h-4 bg-white/10 rounded w-1/2" />
                </CardContent>
              </Card>
            ))}
          </div>
        ) : filtered.length > 0 ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filtered.map((it) => (
              <Card
                key={it.path}
                className="glass hover:border-brand/40 transition-all hover:shadow-glow group relative overflow-hidden"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-brand/0 via-brand/5 to-brand/0 opacity-0 group-hover:opacity-100 transition-opacity" />
                <CardHeader>
                  <CardTitle className="flex items-center justify-between text-lg relative z-10">
                    <div>
                      <div className="text-white/90">{it.date}</div>
                      <div className="flex gap-2 mt-1">
                        {it.tickers.map((ticker) => (
                          <Badge key={ticker} variant="outline" className="text-xs">
                            {ticker}
                          </Badge>
                        ))}
                      </div>
                    </div>
                    <FileText className="w-5 h-5 text-brand" />
                  </CardTitle>
                </CardHeader>
                <CardContent className="flex gap-3 relative z-10">
                  <Button
                    variant="default"
                    size="sm"
                    className="bg-brand hover:bg-brand-400 text-black"
                    asChild
                  >
                    <a href={`/reports/${encodeURIComponent(it.path)}`}>
                      View Report <ArrowRight className="w-3 h-3 ml-1" />
                    </a>
                  </Button>
                  {it.signed_url_pdf && (
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-brand hover:text-brand-400"
                      asChild
                    >
                      <a href={it.signed_url_pdf} target="_blank" rel="noreferrer">
                        PDF <Download className="w-3 h-3 ml-1" />
                      </a>
                    </Button>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <Card className="glass text-center py-12">
            <p className="text-white/60">
              {filter ? "No reports match your filter." : "No reports yet."}
            </p>
          </Card>
        )}
      </section>
    </main>
  )
}

