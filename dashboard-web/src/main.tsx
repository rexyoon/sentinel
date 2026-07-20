import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'

// StrictMode: 개발 중 부작용(잘못된 사이드 이펙트)을 이중 렌더링으로 조기에 드러내는 장치.
ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
