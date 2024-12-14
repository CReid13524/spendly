import React from 'react'
import LoginWithGoogle from '../components/loginWithGoogle'
import LoginWithEmail from '../components/loginWithEmail'


function Login() {
  return (
    <div id="login-container">
    <div id='login-page'>
      <h1 id="login-title">Spendly</h1>
      <LoginWithEmail/>
      <div id='seperator-horizontal-line'>
        <div className='seperator-horizontal-line-component'></div>
        <p>or</p>
        <div className="seperator-horizontal-line-component"></div>
      </div>
      <div id="login-special-buttons">
        <LoginWithGoogle/>
      </div>
      <p id="terms-privacy-text">By clicking continue, you agree to our <a href=''>Terms of Service</a> and <a href=''>Privacy Policy</a></p>
    </div>
    </div>
  )
}

export default Login