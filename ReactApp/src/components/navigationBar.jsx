import React from 'react'
import { Link, useLocation } from 'react-router-dom';

import { AiFillSetting } from "react-icons/ai";
import { AiFillHome } from "react-icons/ai";
import { BiSolidCategory } from "react-icons/bi";
import { AiFillBook } from "react-icons/ai";
import { RiBarChart2Fill } from "react-icons/ri";

import { AiOutlineSetting } from "react-icons/ai";
import { AiOutlineHome } from "react-icons/ai";
import { BiCategory } from "react-icons/bi";
import { AiOutlineBook } from "react-icons/ai";
import { RiBarChart2Line } from "react-icons/ri";

function NavigationBar() {
  const location = useLocation(); 
  const currentPath = location.pathname;

    return (
      <div className="nav-container">
      <nav className="nav-panel">
          <div className='logo'>S</div>
          <div data-label="Home" className={`nav-item ${currentPath === "/" ? "active" : ""}`}><Link to="/" >{currentPath === "/" ? <AiFillHome /> : <AiOutlineHome/>}</Link></div>
          <div data-label="Categories" className={`nav-item ${currentPath === "/categories" ? "active" : ""}`}><Link to="/categories">{currentPath === "/categories" ? <BiSolidCategory/> : <BiCategory/>}</Link></div>
          <div data-label="Reconcile" className={`nav-item ${currentPath === "/reconcile" ? "active" : ""}`}><Link to="/reconcile">{currentPath === "/reconcile" ? <AiFillBook /> : <AiOutlineBook/>}</Link></div>
          <div data-label="Statistics" className={`nav-item ${currentPath === "/statistics" ? "active" : ""}`}><Link to="/statistics">{currentPath === "/statistics" ? <RiBarChart2Fill /> : <RiBarChart2Line/>}</Link></div>
          <div data-label="Settings" className={`nav-item bottom ${currentPath === "/settings" ? "active" : ""}`}><Link to="/settings">{currentPath === "/settings" ? <AiFillSetting /> : <AiOutlineSetting/>}</Link></div>
      </nav>
      </div>
    );
  }

export default NavigationBar