import { useState } from 'react'

function App() {
  const [gameId, setGameId] = useState('22200477')
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  const [mode, setMode] = useState('draft') // 'draft' or 'eval'
  const [evalData, setEvalData] = useState(null)
  const [gameType, setGameType] = useState('all')

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

  const handleEval = async () => {
    setLoading(true)
    setEvalData(null)
    try {
      const response = await fetch('http://localhost:8000/evaluate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ batch_size: 3, iterations: 1, game_type: gameType })
      })
      const res = await response.json()
      setEvalData(res)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  // ROI Calculations
  // If in draft mode, use single run data. If eval, aggregate.
  const humanTimeSeconds = 15 * 60
  let timeSaved = 0
  let costSaved = 0

  if (mode === 'draft' && data) {
    timeSaved = humanTimeSeconds - data.execution_time
    costSaved = (humanTimeSeconds / 3600) * 60
  } else if (mode === 'eval' && evalData) {
    // Total human time for N runs
    const totalHumanTime = evalData.total_runs * humanTimeSeconds
    timeSaved = totalHumanTime - evalData.total_duration
    costSaved = (totalHumanTime / 3600) * 60
  }

  return (
    <div className="container">
      <header>
        <div className="title">🏀 SportsEdit-AI</div>
        <div>
          <button
            onClick={() => setMode('draft')}
            style={{ width: 'auto', marginRight: '1rem', background: mode === 'draft' ? 'var(--primary)' : '#334155' }}
          >Newsroom</button>
          <button
            onClick={() => setMode('eval')}
            style={{ width: 'auto', background: mode === 'eval' ? 'var(--primary)' : '#334155' }}
          >Evaluation Lab</button>
        </div>
      </header>

      <section className="metrics">
        <div className="card">
          <div className="metric-label">Jury Systems</div>
          <div className="metric-value">Active (3 Agents)</div>
        </div>
        <div className="card">
          <div className="metric-label">Total Articles</div>
          <div className="metric-value">{mode === 'eval' && evalData ? evalData.total_runs : (data ? 1 : 0)}</div>
        </div>
        <div className="card">
          <div className="metric-label">Est. Savings</div>
          <div className="metric-value" style={{ color: '#10B981' }}>
            ${costSaved > 0 ? costSaved.toFixed(2) : '0.00'}
          </div>
        </div>
      </section>

      {mode === 'draft' ? (
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
              <h3 style={{ marginTop: 0 }}>Jury Verdict</h3>
              {data ? (
                <div>
                  <div className={`metric-value ${data.status === 'PASS' ? 'status-pass' : 'status-fail'}`}>
                    {data.status || 'UNKNOWN'}
                  </div>
                  <div className="metric-label" style={{ marginTop: '1rem' }}>Revisions: {data.revisions}</div>

                  {data.errors && data.errors.length > 0 ? (
                    <div style={{ marginTop: '1rem' }}>
                      <div className="metric-label">Jury Feedback</div>
                      {data.errors.map((err, i) => (
                        <div key={i} className="log-entry status-fail">{err}</div>
                      ))}
                    </div>
                  ) : (
                    <div style={{ marginTop: '1rem', color: 'var(--success)' }}>
                      Unanimous Pass.
                    </div>
                  )}
                </div>
              ) : (
                <div style={{ color: '#64748B' }}>Waiting for jury...</div>
              )}
            </div>
          </div>
        </div>
      ) : (
        /* EVALUATION MODE */
        <div className="card">
          <h2>Batch Evaluation (NeurIPS 2025 Protocol)</h2>
          <p>Run a random batch of 3 games to test Jury Consistency and ROI.</p>

          <div style={{ marginBottom: '1rem' }}>
            <label className="metric-label" style={{ marginRight: '0.5rem' }}>Game Type:</label>
            <select
              value={gameType}
              onChange={(e) => setGameType(e.target.value)}
              style={{ padding: '0.5rem', borderRadius: '4px', border: '1px solid #334155', background: '#1E293B', color: 'white' }}
            >
              <option value="all">Mixed (All)</option>
              <option value="regular">Regular Season</option>
              <option value="playoff">Playoffs (High Stakes)</option>
            </select>
          </div>

          <button onClick={handleEval} disabled={loading} style={{ width: '200px' }}>
            {loading ? 'Running Batch...' : 'Run Benchmark'}
          </button>

          {evalData && (
            <div style={{ marginTop: '2rem' }}>
              <h3>Results</h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: '1rem', marginBottom: '2rem' }}>
                <div className="card">
                  <div className="metric-label">Total Duration</div>
                  <div>{evalData.total_duration.toFixed(1)}s</div>
                </div>
                <div className="card">
                  <div className="metric-label">Safety Rate</div>
                  <div>{((evalData.results.filter(r => r.revisions === 0).length / evalData.total_runs) * 100).toFixed(0)}%</div>
                </div>
                <div className="card">
                  <div className="metric-label">Pass Rate</div>
                  <div>{((evalData.results.filter(r => r.status === "PASS").length / evalData.total_runs) * 100).toFixed(0)}%</div>
                </div>
                <div className="card">
                  <div className="metric-label">Throughput</div>
                  <div>{(evalData.total_runs / (evalData.total_duration / 60)).toFixed(1)} art/min</div>
                </div>
              </div>

              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ textAlign: 'left', borderBottom: '1px solid #334155' }}>
                    <th style={{ padding: '0.5rem' }}>Game ID</th>
                    <th>Iter</th>
                    <th>Verdict</th>
                    <th>Revisions</th>
                    <th>Time</th>
                  </tr>
                </thead>
                <tbody>
                  {evalData.results.map((r, i) => (
                    <tr key={i} style={{ borderBottom: '1px solid #1E293B' }}>
                      <td style={{ padding: '0.5rem' }}>{r.game_id}</td>
                      <td>{r.iteration}</td>
                      <td style={{ color: r.status === 'PASS' ? 'var(--success)' : 'var(--error)' }}>{r.status}</td>
                      <td>{r.revisions}</td>
                      <td>{r.duration.toFixed(1)}s</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default App
