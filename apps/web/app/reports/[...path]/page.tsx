import { notFound } from "next/navigation"
import { ReportShell } from "@/components/ReportShell"
import { Outline } from "@/components/Outline"
import { Prose } from "@/components/Prose"
import { renderMarkdown } from "@/lib/mdx"
import { Skeleton } from "@/components/ui/skeleton"
import { Card } from "@/components/ui/card"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

interface ReportPageProps {
  params: Promise<{ path: string[] }>
}

export default async function ReportPage({ params }: ReportPageProps) {
  const resolvedParams = await params
  const path = decodeURIComponent(resolvedParams.path.join("/"))
  
  try {
    // Fetch report metadata from API
    const reportRes = await fetch(`${API_URL}/reports?path=${encodeURIComponent(path)}`, {
      cache: "no-store",
    })

    if (!reportRes.ok) {
      notFound()
    }

    const reports: any[] = await reportRes.json()
    const report = reports.find((r) => r.path === path)

    if (!report || !report.signed_url_md) {
      notFound()
    }

    // Fetch markdown content
    const mdRes = await fetch(report.signed_url_md, { cache: "no-store" })
    if (!mdRes.ok) {
      notFound()
    }

    const md = await mdRes.text()
    
    // Extract title from first H1 or use default
    const titleMatch = md.match(/^#\s+(.+)$/m)
    const title = titleMatch ? titleMatch[1] : "Stock Research Report"

    try {
      const { content, toc } = await renderMarkdown(md)
      
      return (
        <ReportShell
          title={title}
          date={report.date || ""}
          tickers={report.tickers || []}
          mdUrl={report.signed_url_md}
          pdfUrl={report.signed_url_pdf}
          toc={<Outline toc={toc} />}
        >
          <Prose>{content}</Prose>
        </ReportShell>
      )
    } catch (renderError) {
      console.error("Error rendering markdown:", renderError)
      // Fallback: render raw markdown
      return (
        <ReportShell
          title={title}
          date={report.date || ""}
          tickers={report.tickers || []}
          mdUrl={report.signed_url_md}
          pdfUrl={report.signed_url_pdf}
          toc={<Outline toc={[]} />}
        >
          <Prose>
            <pre className="whitespace-pre-wrap text-sm">{md}</pre>
          </Prose>
        </ReportShell>
      )
    }
  } catch (error) {
    console.error("Error loading report:", error)
    notFound()
  }
}

// Loading state
export function Loading() {
  return (
    <main className="min-h-screen bg-black text-white relative overflow-hidden">
      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Card className="glass-glow rounded-2xl p-6 mb-6">
          <Skeleton className="h-10 w-64 mb-4" />
          <Skeleton className="h-6 w-32" />
        </Card>
        <Card className="glass rounded-2xl p-8 md:p-12">
          <Skeleton className="h-8 w-full mb-4" />
          <Skeleton className="h-4 w-full mb-2" />
          <Skeleton className="h-4 w-full mb-2" />
          <Skeleton className="h-4 w-3/4 mb-4" />
          <Skeleton className="h-8 w-full mb-4" />
          <Skeleton className="h-4 w-full mb-2" />
          <Skeleton className="h-4 w-full" />
        </Card>
      </div>
    </main>
  )
}

