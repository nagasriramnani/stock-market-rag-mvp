"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { supabase } from "@/lib/supabase"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Spotlight } from "@/components/spotlight"
import { ArrowRight, Sparkles } from "lucide-react"

interface ReportItem {
  path: string
  url?: string
}

export default function Home() {
  const [items, setItems] = useState<ReportItem[]>([])
  const [loading, setLoading] = useState(true)
  const bucket = process.env.NEXT_PUBLIC_REPORT_BUCKET || "reports"

  useEffect(() => {
    async function fetchReports() {
      try {
        const { data: folders } = await supabase.storage
          .from(bucket)
          .list("", { limit: 100, sortBy: { column: "name", order: "desc" } })

        const flat: ReportItem[] = []
        for (const f of folders || []) {
          if (f.name && !f.id) {
            // It's a folder
            const { data: files } = await supabase.storage
              .from(bucket)
              .list(f.name)
            for (const file of files || []) {
              if (file.name && file.name.endsWith(".md")) {
                flat.push({ path: `${f.name}/${file.name}` })
              }
            }
          }
        }

        const signed = await Promise.all(
          flat.map(async (f) => {
            const { data } = await supabase.storage
              .from(bucket)
              .createSignedUrl(f.path, 600)
            return { ...f, url: data?.signedUrl }
          })
        )

        setItems(
          signed.sort((a, b) => (a.path < b.path ? 1 : -1)).slice(0, 6)
        )
      } catch (error) {
        console.error("Error fetching reports:", error)
      } finally {
        setLoading(false)
      }
    }

    fetchReports()
  }, [bucket])

  return (
    <main className="min-h-screen bg-black text-white relative overflow-hidden">
      <Spotlight />
      <div className="absolute inset-0 bg-grid-neon bg-[length:50px_50px] opacity-30" />
      
      <section className="relative z-10 max-w-6xl mx-auto px-6 py-16">
        <div className="glass-glow rounded-2xl p-8 md:p-12 mb-12">
          <div className="flex items-center gap-2 mb-4">
            <Sparkles className="w-6 h-6 text-brand" />
            <h1 className="text-4xl md:text-5xl font-semibold tracking-tight">
              Autonomous <span className="text-brand">Stock Research Agent</span>
            </h1>
          </div>
          <p className="mt-3 text-lg text-white/70 max-w-2xl">
            Daily briefs with sources, impact ranking, and market context.
            Powered by AI, Tavily, and real-time market data.
          </p>
          <div className="mt-8 flex gap-4 flex-wrap">
            <Link href="/run">
              <Button size="lg" className="gap-2">
                Run Now <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
            <Link href="/reports">
              <Button variant="outline" size="lg">
                View Reports
              </Button>
            </Link>
          </div>
        </div>

        <div className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">Recent Reports</h2>
          {loading ? (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[1, 2, 3].map((i) => (
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
          ) : items.length > 0 ? (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {items.map((it) => (
                <Card
                  key={it.path}
                  className="glass hover:border-brand/40 transition-all hover:shadow-glow"
                >
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between text-lg">
                      <span className="truncate">{it.path.split("/")[0]}</span>
                      <Badge className="bg-brand text-black">Report</Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <a
                      className="text-brand hover:text-brand-400 underline flex items-center gap-2"
                      href={it.url}
                      target="_blank"
                      rel="noreferrer"
                    >
                      Open <ArrowRight className="w-3 h-3" />
                    </a>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <Card className="glass text-center py-12">
              <p className="text-white/60">No reports yet. Run your first analysis!</p>
            </Card>
          )}
        </div>
      </section>
    </main>
  )
}

