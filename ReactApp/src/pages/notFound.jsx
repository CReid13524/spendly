import React from 'react'

function notFound() {
  return (
    <div id='notFound-container'>
      <div id='notFound-page'>
        <div className="page-title">404 | Page not found</div>
        <div id='page-notification'>The requested page could not be located. <a href='/'>Return to dashboard</a></div>
      </div>
    </div>
  )
}

export default notFound