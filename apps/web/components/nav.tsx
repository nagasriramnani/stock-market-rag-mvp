"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { Sparkles, FileText, Play } from "lucide-react"
import { cn } from "@/lib/utils"

export function Nav() {
  const pathname = usePathname()

  const links = [
    { href: "/", label: "Home", icon: Sparkles },
    { href: "/reports", label: "Reports", icon: FileText },
    { href: "/run", label: "Run", icon: Play },
  ]

  return (
    <nav className="border-b border-white/10 bg-black/50 backdrop-blur-xl sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-6 py-4">
        <div className="flex items-center gap-6">
          {links.map((link) => {
            const Icon = link.icon
            const isActive = pathname === link.href
            return (
              <Link
                key={link.href}
                href={link.href}
                className={cn(
                  "flex items-center gap-2 px-4 py-2 rounded-xl transition-colors",
                  isActive
                    ? "bg-brand text-black"
                    : "text-white/70 hover:text-white hover:bg-white/5"
                )}
              >
                <Icon className="w-4 h-4" />
                <span>{link.label}</span>
              </Link>
            )
          })}
        </div>
      </div>
    </nav>
  )
}

