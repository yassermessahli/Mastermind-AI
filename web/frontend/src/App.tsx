import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { HomePage } from './pages/HomePage'
import { SettingsPage } from './pages/SettingsPage'
import { CodebreakerPage } from './pages/CodebreakerPage'
import { CodekeeperPage } from './pages/CodekeeperPage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/settings/:mode" element={<SettingsPage />} />
        <Route path="/play/codebreaker" element={<CodebreakerPage />} />
        <Route path="/play/codekeeper" element={<CodekeeperPage />} />
      </Routes>
    </BrowserRouter>
  )
}
