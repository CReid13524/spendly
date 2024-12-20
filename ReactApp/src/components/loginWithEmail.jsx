import React, { useState } from 'react'
import bcrypt from "bcryptjs-react";
import { useNavigate } from 'react-router-dom';

function LoginWithEmail() {
    const [error, setError] = useState(<></>);
    const [email, setEmail] = useState('');
    const [password1, setPassword1] = useState('');
    const [showPasswordInput1, setShowPasswordInput1] = useState(false);
    const [password2, setPassword2] = useState('');
    const [showPasswordInput2, setShowPasswordInput2] = useState(false);
    const [isAccount, setIsAccount] = useState('M');
    const navigate = useNavigate();

    async function authenticate(email, password) {
        const response = await fetch('/api/secure', {
            method: 'POST',
            headers:  {'Content-Type' : 'application/json'},
            body: JSON.stringify({"type":'user', "email":email, "password":password})
        });
        const data = await response.json();
        if (!response.ok) {
            throw data.error
        }
    }

    async function handleLogin() {
        try {
            const response = await fetch(`/api/secure/${email}`, {
                method: 'GET'
            });
            const data = await response.json();
            if (!response.ok) {
                throw data.error
            }
            setShowPasswordInput1(true)
            if (data.isStored) {
                setIsAccount('Y')
                if (password1) {
                    authenticate(email,password1)
                    navigate('/')
                }
            } else {
                setIsAccount('N')
                if (password1 && password2) {
                    const hashedPassword = bcrypt.hash(password1, 10)
                    const response = await fetch('/api/user', {
                        method: 'POST',
                        headers:  {'Content-Type' : 'application/json'},
                        body: JSON.stringify({"email":email, "password":await hashedPassword})
                    });
                    const data = await response.json();
                    if (!response.ok) {
                        throw data.error
                    }
                    authenticate(email, password1)
                    navigate('/')
                } else if (password1) {
                    setShowPasswordInput2(true)
                } 
            }
            
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

    function handleSubmit(event) {
        event.preventDefault()
        const form = event.target.closest('form');
        if (form.checkValidity()) {
            handleLogin()
        } else {
            form.reportValidity();
        }
    }

  return (
    <>
    {error}
    <h4>{isAccount==='Y' && 'Login'}{isAccount==='M' && 'Login or Create an account'} {isAccount==='N' && 'Create an account'}</h4>
    <p id="help-text">Enter your email {isAccount==='Y' && 'and password'} {isAccount==='N' && 'and create a password'} to continue</p>
    <form>
    <input placeholder='Email' onChange={e => setEmail(e.target.value)} value={email} required type='email'/>
    {showPasswordInput1 && <input placeholder='Password' onChange={e => setPassword1(e.target.value)} value={password1} required type='password'/>}
    {showPasswordInput2 && <input placeholder='Re-enter Password' onChange={e => setPassword2(e.target.value)} value={password2} required type='password' pattern={password1} onInvalid={e => e.target.setCustomValidity('Passwords must match')} onInput={e => e.target.setCustomValidity('')}/>}
    <button id="continue-button" onClick={handleSubmit} >Continue</button>
    </form>
    </>
  )
}

export default LoginWithEmail