import React from 'react'
import { Routes, Route, Link } from 'react-router-dom'

// Example components
import Dashboard from './pages/dashboard'
import Categories from './pages/categories'
import Reconcile from './pages/reconcile'
import Statistics from './pages/statistics'
import Settings from './pages/settings'
import NotFound from './pages/notFound'

function App() {
  return (
    <>
      <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/categories" element={<Categories />} />
          <Route path="/reconcile" element={<Reconcile />} />
          <Route path="/statistics" element={<Statistics />} />
          <Route path="/settings" element={<Settings />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
      <nav>
        <ul>
          <li><Link to="/">Dashboard</Link></li>
          <li><Link to="/categories">Categories</Link></li>
          <li><Link to="/reconcile">Reconcile</Link></li>
          <li><Link to="/statistics">Statistics</Link></li>
          <li><Link to="/settings">Settings</Link></li>
        </ul>
      </nav>
    </>
  )
}

export default App
