import React, { useState, useContext } from "react";
import matches from "../data/matches";
import { TicketContext } from "../context/TicketContext";
import MatchModal from "./MatchModal";
import "../matches.css";
import dynamoLogo from "../assets/logo.png";

const MatchList = () => {
    const { buyTicket } = useContext(TicketContext);
    const [selectedMatch, setSelectedMatch] = useState(null);

    const getOpponentLogo = (teamName) => {
        // В реальном проекте нужно добавить логотипы команд
        return dynamoLogo; // Заглушка - используем лого Динамо для всех
    };

    return (
        <div className="matches-container">
            <div className="matches-header">
                <h2>БЛИЖАЙШИЕ МАТЧИ</h2>
                <p>Купить билеты на официальном сайте ФК Динамо-Брест</p>
            </div>

            <div className="match-cards">
                {matches.map((match) => (
                    <div className="match-card" key={match.id}>
                        <div className="match-card-header">
                            <h3>{match.date} • {match.time}</h3>
                            <p>{match.location}</p>
                        </div>
                        <div className="match-card-body">
                            <div className="teams-container">
                                <div className="team">
                                    <img
                                        src={dynamoLogo}
                                        alt="Динамо Брест"
                                        className="team-logo"
                                    />
                                    <p>Динамо Брест</p>
                                </div>
                                <div className="vs">VS</div>
                                <div className="team">
                                    <img
                                        src={getOpponentLogo(match.team)}
                                        alt={match.team}
                                        className="team-logo"
                                    />
                                    <p>{match.team}</p>
                                </div>
                            </div>

                            <div className="match-details">
                                <div className="detail-row">
                                    <span>Турнир:</span>
                                    <span>{match.competition}</span>
                                </div>
                                <div className="detail-row">
                                    <span>Дата:</span>
                                    <span>{match.date}</span>
                                </div>
                                <div className="detail-row">
                                    <span>Время:</span>
                                    <span>{match.time}</span>
                                </div>
                                <div className="detail-row">
                                    <span>Стадион:</span>
                                    <span>{match.location}</span>
                                </div>
                            </div>

                            <button
                                className="buy-button"
                                onClick={() => setSelectedMatch(match)}
                            >
                                КУПИТЬ БИЛЕТ
                            </button>
                        </div>
                    </div>
                ))}
            </div>

            {selectedMatch && (
                <MatchModal
                    match={selectedMatch}
                    onClose={() => setSelectedMatch(null)}
                    onConfirm={(ticketData) => {
                        buyTicket(ticketData);
                        setSelectedMatch(null);
                    }}
                />
            )}
        </div>
    );
};

export default MatchList;