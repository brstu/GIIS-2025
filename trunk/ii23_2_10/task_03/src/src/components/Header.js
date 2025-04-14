import React from "react";
import team from "../data/team";



const Header = () => (
    <div className="header">
        <img src="/assets/logo.png" alt="Динамо Брест" />
        <h1>ФК Динамо Брест</h1>
        <p>Состав команды:</p>
        <div className="team-grid">
            {team.map((player, index) => (
                <div className="player-card" key={index}>
                    <img src={player.image} alt={player.name} />
                    <p><strong>{player.name}</strong></p>
                    <p>{player.position}</p>
                </div>
            ))}
        </div>
    </div>
);

export default Header;