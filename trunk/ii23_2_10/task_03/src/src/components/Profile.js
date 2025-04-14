import React, { useContext, useState, useEffect } from "react";
import { TicketContext } from "../context/TicketContext";

const Profile = () => {
    const { tickets, cancelTicket, profileInfo, updateProfile } = useContext(TicketContext);
    const [expandedTicket, setExpandedTicket] = useState(null);
    const [localProfile, setLocalProfile] = useState(profileInfo);
    const [showConfirm, setShowConfirm] = useState(null);

    // Сохраняем данные профиля при изменении
    useEffect(() => {
        const timer = setTimeout(() => {
            if (JSON.stringify(localProfile) !== JSON.stringify(profileInfo)) {
                updateProfile(localProfile);
            }
        }, 500);
        return () => clearTimeout(timer);
    }, [localProfile, profileInfo, updateProfile]);

    const handleProfileChange = (e) => {
        const { name, value } = e.target;
        setLocalProfile(prev => ({ ...prev, [name]: value }));
    };

    const toggleTicketDetails = (ticketId) => {
        setExpandedTicket(expandedTicket === ticketId ? null : ticketId);
    };

    const handleCancelTicket = (ticketId) => {
        setShowConfirm(ticketId);
    };

    const confirmCancel = () => {
        cancelTicket(showConfirm);
        setShowConfirm(null);
    };

    return (
        <div style={{ padding: "20px" }}>
            <h2>Личный кабинет</h2>

            <div style={{ marginBottom: "30px", border: "1px solid #ccc", padding: "15px", borderRadius: "8px" }}>
                <h3>Персональные данные</h3>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "15px" }}>
                    <div>
                        <label>ФИО:</label>
                        <input
                            type="text"
                            name="fullName"
                            value={localProfile.fullName}
                            onChange={handleProfileChange}
                            style={{ width: "100%", padding: "8px" }}
                        />
                    </div>
                    <div>
                        <label>Телефон:</label>
                        <input
                            type="tel"
                            name="phone"
                            value={localProfile.phone}
                            onChange={handleProfileChange}
                            style={{ width: "100%", padding: "8px" }}
                        />
                    </div>
                    <div>
                        <label>Возраст:</label>
                        <input
                            type="number"
                            name="age"
                            value={localProfile.age}
                            onChange={handleProfileChange}
                            style={{ width: "100%", padding: "8px" }}
                        />
                    </div>
                </div>
            </div>

            <h3>Мои билеты</h3>
            {tickets.length === 0 ? (
                <p>Нет купленных билетов</p>
            ) : (
                <ul style={{ listStyle: "none", padding: 0 }}>
                    {tickets.map((ticket) => (
                        <li key={ticket.id} style={{ marginBottom: "15px", border: "1px solid #eee", padding: "15px", borderRadius: "8px" }}>
                            <div style={{ display: "flex", justifyContent: "space-between" }}>
                                <div>
                                    <strong>{ticket.date} {ticket.time}</strong>
                                    <p>{ticket.team} vs Динамо Брест</p>
                                    <p>Место: {ticket.location}, Сектор: {ticket.sector}</p>
                                </div>
                                <div>
                                    <button
                                        onClick={() => toggleTicketDetails(ticket.id)}
                                        style={{ marginRight: "10px" }}
                                    >
                                        {expandedTicket === ticket.id ? "Свернуть" : "Подробнее"}
                                    </button>
                                    <button
                                        onClick={() => handleCancelTicket(ticket.id)}
                                        style={{ background: "#ff4444", color: "white" }}
                                    >
                                        Отменить
                                    </button>
                                </div>
                            </div>

                            {expandedTicket === ticket.id && (
                                <div style={{ marginTop: "15px", padding: "10px", background: "#f5f5f5", borderRadius: "4px" }}>
                                    <p><strong>Детали билета:</strong></p>
                                    <p>Телефон: {ticket.phone}</p>
                                    <p>Способ оплаты: {ticket.payment}</p>
                                    <p>Количество билетов: {ticket.count}</p>
                                    <p>Сектор: {ticket.sector}</p>
                                    <p>Ряд: {ticket.row || "Не указан"}</p>
                                    <p>Место: {ticket.seat || "Не указано"}</p>
                                </div>
                            )}
                        </li>
                    ))}
                </ul>
            )}

            {/* Модальное окно подтверждения */}
            {showConfirm && (
                <div style={{
                    position: "fixed",
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    background: "rgba(0,0,0,0.5)",
                    display: "flex",
                    justifyContent: "center",
                    alignItems: "center",
                    zIndex: 1000
                }}>
                    <div style={{
                        background: "white",
                        padding: "20px",
                        borderRadius: "8px",
                        width: "300px"
                    }}>
                        <h3>Подтверждение</h3>
                        <p>Вы уверены, что хотите отменить этот билет?</p>
                        <div style={{ display: "flex", justifyContent: "space-between", marginTop: "20px" }}>
                            <button
                                onClick={() => setShowConfirm(null)}
                                style={{ padding: "8px 15px" }}
                            >
                                Нет
                            </button>
                            <button
                                onClick={confirmCancel}
                                style={{ padding: "8px 15px", background: "#ff4444", color: "white" }}
                            >
                                Да, отменить
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Profile;