import React from "react";
import "./Header.css";

const Header = () => {
  return (
    <header className="header">
      <h2>CarSharing</h2>
      <a href="/account">
        <button>Личный кабинет</button>
      </a>
    </header>
  );
};

export default Header;
