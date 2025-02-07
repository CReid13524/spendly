import React from 'react'
import { AiFillQuestionCircle } from "react-icons/ai";
import { Link } from 'react-router-dom';

function PageHeader() {
  return (
    <div id="page-header">
        <h1>Spendly</h1>
        <div id='header-help-button'><Link to="/help"><AiFillQuestionCircle /></Link></div>
    </div>
  )
}

export default PageHeader