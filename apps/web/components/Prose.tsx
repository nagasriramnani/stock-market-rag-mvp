"use client"

import { cn } from "@/lib/utils"

interface ProseProps {
  children: React.ReactNode
  className?: string
}

export function Prose({ children, className }: ProseProps) {
  return (
    <div
      className={cn(
        "prose prose-neon max-w-none",
        "prose-headings:text-white",
        "prose-p:text-slate-200 prose-p:leading-relaxed",
        "prose-a:text-brand prose-a:no-underline hover:prose-a:text-brand-400",
        "prose-strong:text-white",
        "prose-code:text-slate-200",
        "prose-pre:bg-slate-900/50",
        "prose-blockquote:border-brand",
        "prose-ul:list-none",
        "prose-hr:border-white/10",
        className
      )}
    >
      {children}
    </div>
  )
}

