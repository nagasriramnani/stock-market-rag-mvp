"use client"

import { useState, useEffect } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { Spotlight } from "@/components/spotlight"
import {
  Printer,
  Link as LinkIcon,
  FileText,
  Download,
  ArrowUp,
  Share2,
} from "lucide-react"

interface ReportShellProps {
  title: string
  date: string
  tickers: string[]
  mdUrl?: string
  pdfUrl?: string
  children: React.ReactNode
  toc: React.ReactNode
}

export function ReportShell({
  title,
  date,
  tickers,
  mdUrl,
  pdfUrl,
  children,
  toc,
}: ReportShellProps) {
  const [showBackToTop, setShowBackToTop] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      setShowBackToTop(window.scrollY > 600)
    }
    window.addEventListener("scroll", handleScroll)
    return () => window.removeEventListener("scroll", handleScroll)
  }, [])

  const handlePrint = () => {
    window.print()
  }

  const handleCopyLink = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href)
      // You could show a toast here
    } catch (err) {
      console.error("Failed to copy link:", err)
    }
  }

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title,
          text: `Stock Research Report for ${tickers.join(", ")}`,
          url: window.location.href,
        })
      } catch (err) {
        console.error("Share failed:", err)
      }
    } else {
      handleCopyLink()
    }
  }

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: "smooth" })
  }

  return (
    <TooltipProvider>
      <main className="min-h-screen bg-black text-white relative overflow-hidden">
        <Spotlight />
        <div className="absolute inset-0 bg-grid-neon bg-[length:50px_50px] opacity-30" />

        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Header */}
          <Card className="glass-glow rounded-2xl p-6 mb-6 border border-white/10">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
              <div>
                <h1 className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-brand to-cyan-300 bg-clip-text text-transparent mb-2">
                  {title}
                </h1>
                <div className="flex flex-wrap items-center gap-3 text-sm text-white/60">
                  <span>{date}</span>
                  <Separator orientation="vertical" className="h-4" />
                  <div className="flex gap-2">
                    {tickers.map((ticker) => (
                      <Badge key={ticker} variant="outline" className="text-xs">
                        {ticker}
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>
              <div className="flex gap-2">
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={handleShare}
                      className="text-brand hover:text-brand-400"
                    >
                      <Share2 className="w-4 h-4" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>Share</TooltipContent>
                </Tooltip>

                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={handlePrint}
                      className="text-brand hover:text-brand-400"
                    >
                      <Printer className="w-4 h-4" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>Print</TooltipContent>
                </Tooltip>

                {mdUrl && (
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => window.open(mdUrl, "_blank")}
                        className="text-brand hover:text-brand-400"
                      >
                        <FileText className="w-4 h-4" />
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent>Open Markdown</TooltipContent>
                  </Tooltip>
                )}

                {pdfUrl && (
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => window.open(pdfUrl, "_blank")}
                        className="text-brand hover:text-brand-400"
                      >
                        <Download className="w-4 h-4" />
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent>Download PDF</TooltipContent>
                  </Tooltip>
                )}
              </div>
            </div>
          </Card>

          {/* 3-column layout */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left: TOC (hidden on mobile) */}
            <aside className="hidden lg:block lg:col-span-2">
              {toc}
            </aside>

            {/* Center: Content */}
            <article className="lg:col-span-8">
              <Card className="glass rounded-2xl p-8 md:p-12 border border-white/10">
                {children}
              </Card>
            </article>

            {/* Right: Actions (sticky) */}
            <aside className="hidden lg:block lg:col-span-2">
              <div className="sticky top-24">
                <Card className="glass rounded-lg p-4 border border-white/10">
                  <h3 className="text-sm font-semibold text-white mb-3">Actions</h3>
                  <div className="space-y-2">
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      className="w-full justify-start text-brand hover:text-brand-400 cursor-pointer"
                      onClick={(e) => {
                        e.preventDefault()
                        handlePrint()
                      }}
                    >
                      <Printer className="w-4 h-4 mr-2" />
                      Print
                    </Button>
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      className="w-full justify-start text-brand hover:text-brand-400 cursor-pointer"
                      onClick={async (e) => {
                        e.preventDefault()
                        await handleCopyLink()
                        // Show toast notification if you have toast system
                      }}
                    >
                      <LinkIcon className="w-4 h-4 mr-2" />
                      Copy Link
                    </Button>
                    {mdUrl && (
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        className="w-full justify-start text-brand hover:text-brand-400 cursor-pointer"
                        onClick={(e) => {
                          e.preventDefault()
                          window.open(mdUrl, "_blank")
                        }}
                      >
                        <FileText className="w-4 h-4 mr-2" />
                        Markdown
                      </Button>
                    )}
                    {pdfUrl && (
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        className="w-full justify-start text-brand hover:text-brand-400 cursor-pointer"
                        onClick={(e) => {
                          e.preventDefault()
                          window.open(pdfUrl, "_blank")
                        }}
                      >
                        <Download className="w-4 h-4 mr-2" />
                        PDF
                      </Button>
                    )}
                  </div>
                </Card>
              </div>
            </aside>
          </div>
        </div>

        {/* Back to top button */}
        {showBackToTop && (
          <button
            onClick={scrollToTop}
            className="fixed bottom-8 right-8 z-50 p-3 rounded-full bg-brand/20 hover:bg-brand/30 border border-brand/50 text-brand backdrop-blur-xl transition-all shadow-glow"
            aria-label="Back to top"
          >
            <ArrowUp className="w-5 h-5" />
          </button>
        )}
      </main>

      {/* Print styles */}
      <style jsx global>{`
        @media print {
          body {
            background: white;
            color: black;
          }
          .no-print {
            display: none !important;
          }
          main {
            max-width: 100%;
            padding: 0;
          }
          article {
            page-break-inside: avoid;
          }
        }
      `}</style>
    </TooltipProvider>
  )
}

