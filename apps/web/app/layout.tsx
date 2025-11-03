import type { Metadata } from "next"
import { Inter } from "next/font/google"
import { Nav } from "@/components/nav"
import "./globals.css"

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" })

export const metadata: Metadata = {
  title: "AI Stock Research Agent",
  description: "Autonomous stock research with multi-tool integration",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className={inter.variable}>
        <Nav />
        {children}
      </body>
    </html>
  )
}

