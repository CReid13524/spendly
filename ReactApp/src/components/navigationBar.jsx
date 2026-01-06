import React, { useEffect, useState } from 'react'
import { Link, useLocation } from 'react-router-dom';

import { AiFillSetting } from "react-icons/ai";
import { AiFillHome } from "react-icons/ai";
import { BiSolidCategory } from "react-icons/bi";
import { AiFillBook } from "react-icons/ai";
import { RiBarChart2Fill } from "react-icons/ri";
import { MdRoute } from "react-icons/md";
import { MdOutlineLightMode } from "react-icons/md";

import { AiOutlineSetting } from "react-icons/ai";
import { AiOutlineHome } from "react-icons/ai";
import { BiCategory } from "react-icons/bi";
import { AiOutlineBook } from "react-icons/ai";
import { RiBarChart2Line } from "react-icons/ri";
import { MdOutlineRoute } from "react-icons/md";
import { MdOutlineDarkMode } from "react-icons/md";
import { useTheme } from './theme-context';

function NavigationBar() {
  const location = useLocation(); 
  const currentPath = location.pathname;
  const { theme, toggleTheme } = useTheme();

    return (
      <div className="nav-container">
      <nav className="nav-panel">
          <div className='logo optional'>S</div>
          <div data-label="Home" className={`nav-item ${currentPath === "/" ? "active" : ""}`}><Link to="/" >{currentPath === "/" ? <AiFillHome /> : <AiOutlineHome/>}</Link></div>
          <div data-label="Categories" className={`nav-item ${currentPath === "/categories" ? "active" : ""}`}><Link to="/categories">{currentPath === "/categories" ? <BiSolidCategory/> : <BiCategory/>}</Link></div>
          <div data-label="Reconcile" className={`nav-item ${currentPath === "/reconcile" ? "active" : ""}`}><Link to="/reconcile">{currentPath === "/reconcile" ? <AiFillBook /> : <AiOutlineBook/>}</Link></div>
          <div data-label="Statistics" className={`nav-item ${currentPath === "/statistics" ? "active" : ""}`}><Link to="/statistics">{currentPath === "/statistics" ? <RiBarChart2Fill /> : <RiBarChart2Line/>}</Link></div>
          <div data-label="Map" className={`nav-item ${currentPath === "/map" ? "active" : ""}`}><Link to="/map">{currentPath === "/map" ? <MdRoute/> : <MdOutlineRoute/>}</Link></div>
          <div data-label="Theme" className={`nav-item optional bottom`}><a onClick={toggleTheme}>{ theme === "dark" ? <MdOutlineLightMode /> : <MdOutlineDarkMode />}</a></div>
          <div data-label="Settings" className={`nav-item end ${currentPath === "/settings" ? "active" : ""}`}><Link to="/settings">{currentPath === "/settings" ? <AiFillSetting /> : <AiOutlineSetting/>}</Link></div>
      </nav>
      </div>
    );
  }

export default NavigationBar