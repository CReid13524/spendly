import React, { useEffect, useState } from 'react'
import Select from 'react-select'
import { GoogleLogin } from '@react-oauth/google';
import bcrypt from "bcryptjs-react";
import { useNavigate } from 'react-router-dom';

function DeleteCSV() {
  const [userData, setUserData] = useState({})
  const [error, setError] = useState(<></>)
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState('')
  const [passwordNew, setPasswordNew] = useState('')
  const navigate = useNavigate();


  function handleError(error) {
    setError(
      <div className='error-message'>
      <h1 className="error-head">The following error has occured:</h1>
      {String(error)}
      <button className="error-dismiss" onClick={() => setError(<></>)}>Dismiss</button>
      </div>
    );
  }


  async function getUserData() {
    try {
      const response = await fetch('/api/user', {
        method: 'GET',
      });

      const data = await response.json();
      if (!response.ok) {
        throw data.error
      } else {
        setUserData(data.data)
      }
    } catch (error) {
      handleError(error)
    }
  }

  useEffect(() => {
    getUserData()
  },[])

  useEffect(() => {
    setEmail(userData.email)
  },[userData])

  async function handleSubmit(e) {
    e.preventDefault()
      try {
        const hashedPasswrod = bcrypt.hash(passwordNew, 10)
        const response = await fetch('/api/user', {
          method: 'PUT',
          headers:  {'Content-Type' : 'application/json'},
          body: JSON.stringify({type:'user', password:password, passwordNew: await hashedPasswrod})
        });
  
        const data = await response.json();
        if (!response.ok) {
          throw data.error
        } else {
          alert("Password has been updated")
          setPassword('')
          setPasswordNew('')
        }
      } catch (error) {
        handleError(error)
      }
  }

  async function connectGoogle(credential) {
    try {
      const response = await fetch('/api/user', {
        method: 'PUT',
        headers: {'Content-Type' : 'application/json'},
        body: JSON.stringify({'type': 'cred', 'credential' : credential})
      });
      const data = await response.json();
      if (!response.ok) {
        throw data.error
      } else {
        getUserData()
      }
    } catch (error) {
      handleError(error)
    }
  }

  async function handleReset(type) {

    if (!window.confirm(`Are you sure? All account data will be ${type==='reset' ? 'reset. Login data will remain' : 'lost forever'}.`)) return
    try {
      const response = await fetch('/api/user', {
        method: 'DELETE',
        headers: {'Content-Type' : 'application/json'},
        body: JSON.stringify({type: type})
      });
      const data = await response.json();
      if (!response.ok) {
        throw data.error
      } else {
        alert("Account deleted successfully")
        navigate('/login')
        
      }
    } catch (error) {
      handleError(error)
    }
  }
  
  return (
    <div id='user-settings'>
      {error}
      {userData ? userData.googleID ? <div className="gsi-material-button">
        <div className="gsi-material-button-state"></div>
        <div className="gsi-material-button-content-wrapper">
          <div className="gsi-material-button-icon">
            <svg version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" xmlnsXlink="http://www.w3.org/1999/xlink" style={{display: 'block'}}>
              <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"></path>
              <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"></path>
              <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"></path>
              <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"></path>
              <path fill="none" d="M0 0h48v48H0z"></path>
            </svg>
          </div>
          <span className="gsi-material-button-contents">Connected as {userData.name}</span>
        </div>
      </div>
      : <GoogleLogin
      onSuccess={connectGoogle}
      theme="filled_black"
      width={300}
      logo_alignment="left"
    /> : null}
    <form onSubmit={handleSubmit}>
      <div className='form-item'>Email <input type='email' disabled value={email} onChange={(e) => setEmail(e.target.value)}/></div>
      <div className='form-item'>Current Password <input type='password' required value={password} onChange={(e) => setPassword(e.target.value)}/></div>
      <div className='form-item'>New Password <input type='password' required value={passwordNew} onChange={(e) => setPasswordNew(e.target.value)}/></div>
      <button type='submit'>Change Password</button>
    </form>
    <button className='hazard-button' onClick={() => handleReset('reset')}>Reset Account Data</button>
    <button className='hazard-button' onClick={() => handleReset('delete')}>Delete Account</button>

    </div>
  )
}

export default DeleteCSV