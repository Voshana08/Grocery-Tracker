import { Route, Routes } from 'react-router'
import LocationPage from './pages/LocationPage.jsx'
import NotFoundPage from './pages/NotFoundPage.jsx'

// Route table (CLAUDE.md section 9). /t/:slug is written on the NFC tags: never change it.
export default function App() {
  return (
    <Routes>
      <Route path="/t/:slug" element={<LocationPage />} />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  )
}
