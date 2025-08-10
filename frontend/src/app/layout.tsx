import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Pivisuma',
  description: 'Tree planting records and GIS mapping',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased bg-white text-gray-900">{children}</body>
    </html>
  )
}