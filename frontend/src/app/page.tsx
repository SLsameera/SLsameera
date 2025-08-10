import Link from 'next/link'
import { fetchMoon } from '@/lib/api'

export default async function HomePage() {
  const moon = await fetchMoon()
  return (
    <main className="max-w-3xl mx-auto p-6 space-y-6">
      <h1 className="text-2xl font-bold">Pivisuma</h1>
      <p className="text-gray-600">Earth–Moon simulator (demo) and GIS foundation.</p>
      <section className="p-4 rounded border bg-gray-50">
        <h2 className="font-semibold mb-2">Moon (approximate)</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm">
          <div>UTC: <span className="font-mono">{moon.datetime_utc}</span></div>
          <div>X (km): <span className="font-mono">{moon.position_km.x.toFixed(0)}</span></div>
          <div>Y (km): <span className="font-mono">{moon.position_km.y.toFixed(0)}</span></div>
          <div>Z (km): <span className="font-mono">{moon.position_km.z.toFixed(0)}</span></div>
          <div>Force (norm): <span className="font-mono">{moon.tidal_force_normalized.toExponential(3)}</span></div>
        </div>
      </section>
      <Link className="inline-block px-4 py-2 rounded bg-green-600 text-white hover:bg-green-700" href="/map">Open Map</Link>
    </main>
  )
}