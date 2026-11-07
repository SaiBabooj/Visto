import React, { useEffect, useState } from 'react'

export default function App() {
  const [status, setStatus] = useState<string>('Connecting to gateway...')

  useEffect(() => {
    fetch('/api/languages')
      .then((res) => res.json())
      .then((data) => {
        setStatus(`Gateway online (${data.languages?.length || 0} languages configured)`)
      })
      .catch(() => {
        setStatus('Gateway not reached (run make dev)')
      })
  }, [])

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-xl shadow-md p-6 text-center space-y-4">
        <h1 className="text-2xl font-bold tracking-tight text-blue-600">Voicebridge</h1>
        <p className="text-slate-600 text-sm">
          Chennai Traveller ⇄ Local Driver Voice Translation
        </p>
        <div className="p-3 bg-slate-100 rounded text-xs font-mono text-slate-700">
          Status: {status}
        </div>
      </div>
    </div>
  )
}
