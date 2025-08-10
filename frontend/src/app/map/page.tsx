import dynamic from 'next/dynamic'

const LeafletMap = dynamic(() => import('@/components/LeafletMap'), { ssr: false })

export default function MapPage() {
  return (
    <main className="max-w-5xl mx-auto p-6 space-y-4">
      <h1 className="text-2xl font-bold">Live GIS Map</h1>
      <LeafletMap />
    </main>
  )
}