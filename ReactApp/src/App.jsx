import React, { useEffect, useRef, useState } from 'react'
import { Routes, Route, Link, useLocation, useNavigate } from 'react-router-dom'

import Login from './pages/login'
import Dashboard from './pages/dashboard'
import Categories from './pages/categories'
import Reconcile from './pages/reconcile'
import Statistics from './pages/statistics'
import Settings from './pages/settings'
import NotFound from './pages/notFound'
import LoadingAnimated from './components/loadingAnimated'
import NavigationBar from './components/navigationBar'
import Help from './pages/help'



function App() {
  const location = useLocation();
  const hideNav = location.pathname === '/login';
  const navigate = useNavigate();
  const [appData, setAppData] = useState(null);


  useEffect(() => {
    // Run auth verification only if not on the login page
      const verifyAuth = async (quick=false) => {
        try {
          const response = await fetch('/api/secure', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
          });
          const data = await response.json();
          if (response.status == 500) {
            throw response.statusText
          }
          console.log('Auth verified')
          if (!data.valid && !quick) {
            if (data.error.includes("expired")) alert(`Session expired. Please log in again.\n(${data.error})`);
            navigate('/login');
          } else if (data.valid) {
            setAppData(
              <>
              <Route path="/" element={<Dashboard />} />
              <Route path="/categories" element={<Categories />} />
              <Route path="/reconcile" element={<Reconcile />} />
              <Route path="/statistics" element={<Statistics />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="*" element={<NotFound />} />
              <Route path="/help" element={<Help />} />
            </> 
            )
            if (quick) navigate('/')
          }
        } catch (error) {
          if (!quick) {
            alert(`Failed to verify authentication: ${error}`);
            navigate('/login');
          }
        }
      };
      if (location.pathname !== '/login') verifyAuth();
      else {
        verifyAuth(true)
      }

      const intervalId = setInterval(verifyAuth, 300000) // Check every 5 minutes
      return () => clearInterval(intervalId);
    
    }, [location.pathname, navigate]);

  return (
    <>
      {!hideNav && appData && <NavigationBar/>}
      <Routes>
          <Route path="/login" element={<Login />} />
          {appData}
      </Routes>
    </>
  )
}

export default App;
