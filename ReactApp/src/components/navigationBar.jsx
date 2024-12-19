import React from 'react'
import { Link, useLocation } from 'react-router-dom';

import { AiFillSetting } from "react-icons/ai";
import { AiFillHome } from "react-icons/ai";
import { BiSolidCategory } from "react-icons/bi";
import { AiFillBook } from "react-icons/ai";
import { RiBarChartFill } from "react-icons/ri";

function NavigationBar() {
  const location = useLocation(); 
  const currentPath = location.pathname;

    return (
      <div id="nav-container">
      <nav id="nav-panel">
          <div className={`nav-item ${currentPath === "/" ? "active" : ""}`}><Link to="/" ><AiFillHome /></Link></div>
          <div className={`nav-item ${currentPath === "/categories" ? "active" : ""}`}><Link to="/categories"><BiSolidCategory /></Link></div>
          <div className={`nav-item ${currentPath === "/reconcile" ? "active" : ""}`}><Link to="/reconcile"><AiFillBook /></Link></div>
          <div className={`nav-item ${currentPath === "/statistics" ? "active" : ""}`}><Link to="/statistics"><RiBarChartFill /></Link></div>
          <div className={`nav-item ${currentPath === "/settings" ? "active" : ""}`}><Link to="/settings"><AiFillSetting /></Link></div>
      </nav>
      </div>
    );
  }

export default NavigationBar