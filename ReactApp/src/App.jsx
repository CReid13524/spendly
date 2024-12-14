import React from 'react'
import { Routes, Route, Link, useLocation } from 'react-router-dom'

// Example components
import Login from './pages/login'
import Dashboard from './pages/dashboard'
import Categories from './pages/categories'
import Reconcile from './pages/reconcile'
import Statistics from './pages/statistics'
import Settings from './pages/settings'
import NotFound from './pages/notFound'

function Navigation() {
  return (
    <nav id="nav-panel">
      <ul>
        <li><Link to="/login">Login</Link></li>
        <li><Link to="/">Dashboard</Link></li>
        <li><Link to="/categories">Categories</Link></li>
        <li><Link to="/reconcile">Reconcile</Link></li>
        <li><Link to="/statistics">Statistics</Link></li>
        <li><Link to="/settings">Settings</Link></li>
      </ul>
    </nav>
  );
}

function App() {
  const location = useLocation();
  const hideNav = location.pathname === '/login';

  return (
    <>
      {!hideNav && <Navigation/>}
      <Routes>
        <Route path="/login" element={<Login />} />
          <Route path="/" element={<Dashboard />} />
          <Route path="/categories" element={<Categories />} />
          <Route path="/reconcile" element={<Reconcile />} />
          <Route path="/statistics" element={<Statistics />} />
          <Route path="/settings" element={<Settings />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </>
  )
}

export default App
