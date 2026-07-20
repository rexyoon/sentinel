import { useEffect, useState } from 'react'

// 서버 /api/latest 가 돌려주는 한 항목의 모양.
type LatestEntry = {
  host: string
  name: string
  value: number
}

const API = 'http://localhost:8082'

function App() {
  const [entries, setEntries] = useState<LatestEntry[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // 2초마다 최신값을 다시 받아온다 (폴링). 나중에 WebSocket으로 바꿀 자리.
    const load = async () => {
      try {
        const res = await fetch(`${API}/api/latest`)
        setEntries(await res.json())
        setError(null)
      } catch (e) {
        setError('서버에 연결할 수 없습니다 (8082 실행 중인가요?)')
      }
    }
    load()
    const timer = setInterval(load, 2000)
    // 컴포넌트가 사라질 때 타이머를 정리한다 (누수 방지).
    return () => clearInterval(timer)
  }, [])

  return (
      <div style={{ fontFamily: 'system-ui, sans-serif', padding: 24, maxWidth: 720, margin: '0 auto' }}>
        <h1>Sentinel</h1>
        {error && <p style={{ color: '#c0392b' }}>{error}</p>}
        {!error && entries.length === 0 && <p style={{ color: '#888' }}>지표 수신 대기 중…</p>}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', gap: 12 }}>
          {entries.map((e) => (
              <div key={`${e.host}:${e.name}`} style={{ border: '1px solid #ddd', borderRadius: 10, padding: 16 }}>
                <div style={{ fontSize: 12, color: '#888', textTransform: 'uppercase' }}>{e.host}</div>
                <div style={{ fontSize: 14, fontWeight: 600 }}>{e.name}</div>
                <div style={{ fontSize: 28, fontWeight: 700 }}>{e.value.toFixed(1)}<span style={{ fontSize: 14, color: '#888' }}> %</span></div>
              </div>
          ))}
        </div>
      </div>
  )
}

export default App