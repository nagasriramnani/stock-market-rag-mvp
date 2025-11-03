"use client"

import { useEffect, useState } from "react"
import { ScrollArea } from "@/components/ui/scroll-area"
import { cn } from "@/lib/utils"

interface TocItem {
  id: string
  text: string
  level: number
}

interface OutlineProps {
  toc: TocItem[]
}

export function Outline({ toc }: OutlineProps) {
  const [activeId, setActiveId] = useState<string>("")

  useEffect(() => {
    if (toc.length === 0) return

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setActiveId(entry.target.id)
          }
        })
      },
      {
        rootMargin: "-100px 0px -66%",
      }
    )

    const headings = toc.map((item) => document.getElementById(item.id)).filter(Boolean)
    headings.forEach((heading) => {
      if (heading) observer.observe(heading)
    })

    return () => {
      headings.forEach((heading) => {
        if (heading) observer.unobserve(heading)
      })
    }
  }, [toc])

  const scrollToHeading = (id: string) => {
    const element = document.getElementById(id)
    if (element) {
      element.scrollIntoView({ behavior: "smooth", block: "start" })
    }
  }

  if (toc.length === 0) {
    return null
  }

  return (
    <div className="sticky top-24 h-[calc(100vh-8rem)]">
      <div className="glass rounded-lg p-4 border border-white/10">
        <h3 className="text-sm font-semibold text-white mb-3">Contents</h3>
        <ScrollArea className="h-full">
          <nav className="space-y-1">
            {toc.map((item) => (
              <button
                key={item.id}
                type="button"
                onClick={(e) => {
                  e.preventDefault()
                  scrollToHeading(item.id)
                }}
                className={cn(
                  "block w-full text-left text-sm transition-colors cursor-pointer",
                  "hover:text-brand hover:bg-white/5 px-2 py-1 rounded",
                  item.level === 1 && "pl-2 font-medium",
                  item.level === 2 && "pl-6",
                  item.level === 3 && "pl-10",
                  item.level === 4 && "pl-14",
                  activeId === item.id
                    ? "text-brand font-medium bg-brand/10"
                    : "text-white/60"
                )}
              >
                {item.text}
              </button>
            ))}
          </nav>
        </ScrollArea>
      </div>
    </div>
  )
}

