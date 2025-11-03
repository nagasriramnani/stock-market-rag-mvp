"use client"

import * as React from "react"
import { cn } from "@/lib/utils"

interface ToastProps {
  title?: string
  description?: string
  variant?: "default" | "success" | "error"
}

export function Toast({ title, description, variant = "default" }: ToastProps) {
  return (
    <div
      className={cn(
        "pointer-events-auto w-full max-w-sm overflow-hidden rounded-lg border border-white/10 bg-black/90 backdrop-blur-xl shadow-glow",
        variant === "success" && "border-green-500/50",
        variant === "error" && "border-red-500/50"
      )}
    >
      <div className="p-4">
        {title && (
          <div className="text-sm font-semibold text-white">{title}</div>
        )}
        {description && (
          <div className="mt-1 text-sm text-white/70">{description}</div>
        )}
      </div>
    </div>
  )
}

