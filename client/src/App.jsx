import { useState } from 'react'

function App() {
  const [gameId, setGameId] = useState('22200477')
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  const handleDraft = async () => {
    setLoading(true)
    setError(null)
    setData(null)

    try {
      const response = await fetch('http://localhost:8000/draft', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ game_id: gameId }),
      })

      if (!response.ok) {
        const errData = await response.json()
        throw new Error(errData.detail || 'Failed to fetch')
      }

      const result = await response.json()
      setData(result)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  // ROI Calculations
  const humanTimeSeconds = 15 * 60 // 15 mins
  const aiTime = data ? data.execution_time : 0
  const timeSaved = data ? (humanTimeSeconds - aiTime) : 0
  const costSaved = data ? (humanTimeSeconds / 3600) * 60 : 0 // $60/hr

  return (
    <div className="container">
      <header>
        <div className="title">🏀 SportsEdit-AI</div>
        <div style={{ color: '#94A3B8' }}>Agentic Newsroom</div>
      </header>

      <section className="metrics">
        <div className="card">
          <div className="metric-label">Writer Model</div>
          <div className="metric-value">Llama 3.2 (3B)</div>
        </div>
        <div className="card">
          <div className="metric-label">Judge Model</div>
          <div className="metric-value">Mistral (7B)</div>
        </div>
        <div className="card">
          <div className="metric-label">Est. Savings</div>
          <div className="metric-value" style={{ color: '#10B981' }}>
            ${costSaved > 0 ? costSaved.toFixed(2) : '0.00'}
          </div>
        </div>
      </section>

      <div className="grid">
        {/* Sidebar */}
        <div className="sidebar">
          <div className="card">
            <h3 style={{ marginTop: 0 }}>Mission Control</h3>
            <div style={{ marginBottom: '1rem' }}>
              <label className="metric-label" style={{ display: 'block', marginBottom: '0.5rem' }}>Game ID</label>
              <input
                value={gameId}
                onChange={(e) => setGameId(e.target.value)}
                placeholder="Ex: 22200477"
              />
            </div>
            <button onClick={handleDraft} disabled={loading}>
              {loading ? 'Agents Working...' : 'Draft Article'}
            </button>
            {error && <div style={{ color: 'var(--error)', marginTop: '1rem' }}>{error}</div>}
          </div>

          {data && (
            <div className="card">
              <div className="metric-label">Performance</div>
              <div style={{ marginTop: '1rem' }}>
                <div>Time: {data.execution_time.toFixed(2)}s</div>
                <div style={{ color: '#10B981' }}>Saved: {(timeSaved / 60).toFixed(1)} min</div>
              </div>
            </div>
          )}
        </div>

        {/* Main Content */}
        <div className="main">
          <div className="card" style={{ minHeight: '400px' }}>
            <h2 style={{ marginTop: 0 }}>Latest Draft</h2>
            {loading && (
              <div className="loader" style={{ textAlign: 'center', padding: '4rem' }}>
                Writing...
              </div>
            )}
            {data && (
              <div className="article-content">
                {data.draft}
              </div>
            )}
            {!data && !loading && (
              <div style={{ color: '#64748B', textAlign: 'center', marginTop: '4rem' }}>
                Select a game and click draft to begin.
              </div>
            )}
          </div>
        </div>

        {/* Verification Logic */}
        <div className="audit">
          <div className="card">
            <h3 style={{ marginTop: 0 }}>Verification Log</h3>
            {data ? (
              <div>
                <div className={`metric-value ${data.status === 'PASS' ? 'status-pass' : 'status-fail'}`}>
                  {data.status || 'UNKNOWN'}
                </div>
                <div className="metric-label" style={{ marginTop: '1rem' }}>Revisions: {data.revisions}</div>

                {data.errors && data.errors.length > 0 ? (
                  <div style={{ marginTop: '1rem' }}>
                    <div className="metric-label">Issues</div>
                    {data.errors.map((err, i) => (
                      <div key={i} className="log-entry status-fail">{err}</div>
                    ))}
                  </div>
                ) : (
                  <div style={{ marginTop: '1rem', color: 'var(--success)' }}>
                    No factual errors detected.
                  </div>
                )}
              </div>
            ) : (
              <div style={{ color: '#64748B' }}>Waiting for agents...</div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
