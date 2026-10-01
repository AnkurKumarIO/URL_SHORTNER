import React, { useState, useEffect } from 'react';

const API_BASE = "http://localhost:8000";

export default function App() {
  const [longUrl, setLongUrl] = useState('');
  const [shortenedResult, setShortenedResult] = useState(null);
  const [analytics, setAnalytics] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchAnalytics = async () => {
    try {
      const res = await fetch(`${API_BASE}/analytics`);
      if (res.ok) {
        const data = await res.json();
        setAnalytics(data);
      }
    } catch (err) {
      console.error("Failed to fetch analytics:", err);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const handleShorten = async (e) => {
    e.preventDefault();
    if (!longUrl) return;
    setLoading(true);
    setError('');

    try {
      const res = await fetch(`${API_BASE}/shorten`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: longUrl })
      });

      if (!res.ok) {
        throw new Error('Failed to shorten URL');
      }

      const data = await res.json();
      setShortenedResult(data);
      setLongUrl('');
      fetchAnalytics();
    } catch (err) {
      setError(err.message || 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="header">
        <h1>LinkPulse</h1>
        <p>High-Performance URL Shortener & Analytics Dashboard</p>
      </div>

      <div className="card">
        <h2>Shorten a Long Link</h2>
        <form onSubmit={handleShorten} style={{ marginTop: '1rem' }}>
          <div className="form-group">
            <input
              type="url"
              className="input-field"
              placeholder="Paste long URL here (e.g. https://example.com/long-page)..."
              value={longUrl}
              onChange={(e) => setLongUrl(e.target.value)}
              required
            />
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? 'Shortening...' : 'Shorten Link'}
            </button>
          </div>
        </form>

        {error && <p style={{ color: '#ef4444', marginTop: '1rem' }}>{error}</p>}

        {shortenedResult && (
          <div className="result-box">
            <div>
              <span style={{ fontSize: '0.875rem', color: '#94a3b8', display: 'block' }}>Shortened URL Ready:</span>
              <a href={shortenedResult.short_url} target="_blank" rel="noreferrer" className="result-url">
                {shortenedResult.short_url}
              </a>
            </div>
            <button 
              className="btn-primary"
              style={{ padding: '0.5rem 1rem', fontSize: '0.875rem' }}
              onClick={() => navigator.clipboard.writeText(shortenedResult.short_url)}
            >
              Copy Link
            </button>
          </div>
        )}
      </div>

      <div className="card">
        <div className="analytics-header">
          <h2>Analytics Dashboard</h2>
          <button onClick={fetchAnalytics} className="btn-primary" style={{ padding: '0.5rem 1rem', fontSize: '0.85rem' }}>
            Refresh Stats
          </button>
        </div>

        {analytics.length === 0 ? (
          <p style={{ color: '#94a3b8' }}>No shortened links created yet. Create one above to see analytics!</p>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Short Code</th>
                  <th>Original URL</th>
                  <th>Total Clicks</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {analytics.map((item) => (
                  <tr key={item.short_code}>
                    <td>
                      <span className="short-code-badge">{item.short_code}</span>
                    </td>
                    <td style={{ maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      <a href={item.long_url} target="_blank" rel="noreferrer" style={{ color: '#94a3b8', textDecoration: 'none' }}>
                        {item.long_url}
                      </a>
                    </td>
                    <td>
                      <span className="clicks-badge">{item.total_clicks} Clicks</span>
                    </td>
                    <td>
                      <a 
                        href={`${API_BASE}/r/${item.short_code}`} 
                        target="_blank" 
                        rel="noreferrer"
                        style={{ color: '#3b82f6', fontWeight: 600, textDecoration: 'none' }}
                      >
                        Visit Link
                      </a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
