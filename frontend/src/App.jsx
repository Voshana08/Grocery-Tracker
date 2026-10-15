import { Route, Routes } from 'react-router'
import AddItemPage from './pages/AddItemPage.jsx'
import LocationPage from './pages/LocationPage.jsx'
import NotFoundPage from './pages/NotFoundPage.jsx'

// Route table (CLAUDE.md section 9). /t/:slug is written on the NFC tags: never change it.
export default function App() {
  return (
    <Routes>
      <Route path="/t/:slug" element={<LocationPage />} />
      <Route path="/items/new" element={<AddItemPage />} />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  )
}
