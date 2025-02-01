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



function App() {
  const location = useLocation();
  const hideNav = location.pathname === '/login';
  const navigate = useNavigate();
  const hasCheckedAuth = useRef(false);
  const [isAuthVerified, setIsAuthVerified] = useState(false);
  const [isAuthLoading, setIsAuthLoading] = useState(true);


  useEffect(() => {
    // Run auth verification only if not on the login page
    if (location.pathname !== '/login') {
      const verifyAuth = async () => {
        try {
          const response = await fetch('/api/secure', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
          });
          if (response.status == 500) {
            throw response.statusText
          }
          const data = await response.json();
          console.log('Auth verified')
          if (!data.valid) {
            alert(`Session expired. Please log in again.\n(${data.error})`);
            navigate('/login');
            setIsAuthVerified(false);
          } else {
            setIsAuthVerified(true);
          }
        } catch (error) {
          alert(`Failed to verify authentication: ${error}`);
          navigate('/login');
          setIsAuthVerified(false);
        } finally {
          setIsAuthLoading(false);
        }
      };

      if (hasCheckedAuth.current) {
      verifyAuth();
      } else {
        setIsAuthVerified(false)
      }
      hasCheckedAuth.current = true

      const intervalId = setInterval(verifyAuth, 300000) // Check every 5 minutes
      return () => clearInterval(intervalId);
      

    } else {setIsAuthLoading(false)}
    
  }, [location.pathname, navigate]);

  if (isAuthLoading && hideNav) {
    return <LoadingAnimated />;
  }

  return (
    <>
      {!hideNav && isAuthVerified && <NavigationBar/>}
      <Routes>
          <Route path="/login" element={<Login />} />
          {isAuthVerified ? 
            <>
              <Route path="/" element={<Dashboard />} />
              <Route path="/categories" element={<Categories />} />
              <Route path="/reconcile" element={<Reconcile />} />
              <Route path="/statistics" element={<Statistics />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="*" element={<NotFound />} />
            </> 
            :<></> }
      </Routes>
    </>
  )
}

export default App;
