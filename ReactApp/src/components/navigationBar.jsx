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
      <div id="nav-container">
      <nav id="nav-panel">
          <div className={`nav-item ${currentPath === "/" ? "active" : ""}`}><Link to="/" >{currentPath === "/" ? <AiOutlineHome/> : <AiFillHome />}</Link>Dashboard</div>
          <div className={`nav-item ${currentPath === "/categories" ? "active" : ""}`}><Link to="/categories">{currentPath === "/categories" ? <BiCategory/> : <BiSolidCategory />}</Link>Categories</div>
          <div className={`nav-item ${currentPath === "/reconcile" ? "active" : ""}`}><Link to="/reconcile">{currentPath === "/reconcile" ? <AiOutlineBook/> : <AiFillBook />}</Link>Reconcile</div>
          <div className={`nav-item ${currentPath === "/statistics" ? "active" : ""}`}><Link to="/statistics">{currentPath === "/statistics" ? <RiBarChart2Line/> : <RiBarChart2Fill />}</Link>Statistics</div>
          <div className={`nav-item ${currentPath === "/settings" ? "active" : ""}`}><Link to="/settings">{currentPath === "/settings" ? <AiOutlineSetting/> : <AiFillSetting />}</Link>Settings</div>
      </nav>
      </div>
    );
  }

export default NavigationBar