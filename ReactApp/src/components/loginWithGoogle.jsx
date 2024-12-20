import React, { useState } from "react";
import { GoogleLogin } from '@react-oauth/google';
import { useNavigate } from 'react-router-dom';

function LoginWithGoogle() {
  const [error, setError] = useState(<></>);
  const navigate = useNavigate();

  async function handleLogin(res) {
    try {
      const response = await fetch('/api/secure', {
        method: 'POST',
        headers: {'Content-Type' : 'application/json'},
        body: JSON.stringify({'type': 'cred', 'credential' : res.credential})
      });
      const data = await response.json();
      if (!response.ok) {
        throw data.error
    }
    navigate('/')
    } catch (error) {
      setError(
        <div className='error-message'>
            <h1 className="error-head">The following error has occured:</h1>
            {String(error)}
            <button className="error-dismiss" onClick={(e) => setError(<></>)}>Dismiss</button>
        </div>
    );
    }
  }
  
  return (
    <>
    {error}
    <GoogleLogin
      onSuccess={(credentialResponse) => handleLogin(credentialResponse)}
      onError={() => {
        console.log('Login Failed');
      }}
      useOneTap
      theme="filled_blue"
      width={300}
      logo_alignment="left"
    />
    </>
  )
}

export default LoginWithGoogle