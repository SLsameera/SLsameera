export const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000'

export async function fetchMoon(dt?: string) {
  const url = new URL('/astro/moon', apiBase)
  if (dt) url.searchParams.set('dt', dt)
  const res = await fetch(url.toString(), { next: { revalidate: 60 } })
  if (!res.ok) throw new Error(`API error ${res.status}`)
  return res.json() as Promise<{
    datetime_utc: string
    position_km: { x: number; y: number; z: number }
    tidal_force_normalized: number
  }>
}