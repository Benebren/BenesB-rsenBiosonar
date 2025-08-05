import { useEffect, useState } from 'react'
import axios from 'axios'

type Result = {
  symbol: string
  close?: number
  score?: number
  conditions?: Record<string, boolean>
  as_of?: string
  error?: string
}

export default function Home() {
  const [results, setResults] = useState<Result[]>([])
  const [symbols, setSymbols] = useState<string>('AAPL,MSFT,NVDA,TSLA,SPY,BTC-USD,ETH-USD,SOL-USD')
  const [loading, setLoading] = useState(false)
  const apiBase = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

  const fetchData = async () => {
    try {
      setLoading(true)
      const url = `${apiBase}/analyze?symbols=${encodeURIComponent(symbols)}`
      const { data } = await axios.get(url)
      setResults(data.results || [])
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return (
    <main className="min-h-screen p-6">
      <h1 className="text-3xl font-bold mb-4">BenesBörsenBiosonar</h1>
      <div className="mb-4 flex gap-2 flex-wrap">
        <input
          value={symbols}
          onChange={(e) => setSymbols(e.target.value)}
          className="px-3 py-2 border rounded w-full md:w-[600px]"
          placeholder="AAPL,MSFT,NVDA,TSLA,SPY,BTC-USD,ETH-USD,SOL-USD"
        />
        <button
          onClick={fetchData}
          className="px-4 py-2 bg-black text-white rounded disabled:opacity-50"
          disabled={loading}
        >
          {loading ? 'Analysiere…' : 'Analysieren'}
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full bg-white shadow-sm rounded">
          <thead>
            <tr className="bg-gray-100 text-left">
              <th className="px-4 py-2">Symbol</th>
              <th className="px-4 py-2">Kurs</th>
              <th className="px-4 py-2">Score</th>
              <th className="px-4 py-2">Signale</th>
              <th className="px-4 py-2">Zeitpunkt</th>
              <th className="px-4 py-2">Status</th>
            </tr>
          </thead>
          <tbody>
            {results.map((r, idx) => (
              <tr key={idx} className="border-t">
                <td className="px-4 py-2 font-mono">{r.symbol}</td>
                <td className="px-4 py-2">{r.close ? r.close.toFixed(2) : '-'}</td>
                <td className="px-4 py-2 font-semibold">{r.score ?? '-'}</td>
                <td className="px-4 py-2">
                  {r.conditions ? (
                    <ul className="text-sm list-disc pl-5">
                      {Object.entries(r.conditions).map(([k, v]) => (
                        <li key={k} className={v ? 'text-green-700' : 'text-gray-400'}>
                          {k} {v ? '✅' : '—'}
                        </li>
                      ))}
                    </ul>
                  ) : '-'}
                </td>
                <td className="px-4 py-2">{r.as_of ? new Date(r.as_of).toLocaleString() : '-'}</td>
                <td className="px-4 py-2">{r.error ? <span className="text-red-600">{r.error}</span> : 'OK'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="text-xs text-gray-500 mt-4">
        Hinweis: Score summiert erfüllte Bedingungen (max 7) nach deiner Formel.
      </p>
    </main>
  )
}