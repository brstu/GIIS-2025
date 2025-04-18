import React from "react";
import { Link } from "react-router-dom";

const NavBar = () => (
    <nav style={{ padding: '10px', background: '#002d72', color: 'white' }}>
        <Link to="/" style={{ margin: '0 15px', color: 'white' }}>Главная</Link>
        <Link to="/profile" style={{ margin: '0 15px', color: 'white' }}>Личный кабинет</Link>
    </nav>
);

export default NavBar;
