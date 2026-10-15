import { Route, Routes } from 'react-router'
import AddItemPage from './pages/AddItemPage.jsx'
import LocationPage from './pages/LocationPage.jsx'
import NotFoundPage from './pages/NotFoundPage.jsx'
import TripDetailPage from './pages/TripDetailPage.jsx'
import TripFormPage from './pages/TripFormPage.jsx'
import TripSavedPage from './pages/TripSavedPage.jsx'
import TripsPage from './pages/TripsPage.jsx'

// Route table (CLAUDE.md section 9). /t/:slug is written on the NFC tags: never change it.
export default function App() {
  return (
    <Routes>
      <Route path="/t/:slug" element={<LocationPage />} />
      <Route path="/items/new" element={<AddItemPage />} />
      <Route path="/trips" element={<TripsPage />} />
      <Route path="/trips/new" element={<TripFormPage />} />
      <Route path="/trips/:id" element={<TripDetailPage />} />
      <Route path="/trips/:id/saved" element={<TripSavedPage />} />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  )
}
