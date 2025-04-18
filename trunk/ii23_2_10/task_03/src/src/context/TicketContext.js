import React, { createContext, useState, useEffect } from "react";

export const TicketContext = createContext();

export const TicketProvider = ({ children }) => {
    const [tickets, setTickets] = useState([]);
    const [profileInfo, setProfileInfo] = useState(() => {
        // Загружаем из localStorage при инициализации
        const saved = localStorage.getItem('profileInfo');
        return saved ? JSON.parse(saved) : {
            phone: "",
            fullName: "",
            age: ""
        };
    });

    // Сохраняем в localStorage при изменении
    useEffect(() => {
        localStorage.setItem('profileInfo', JSON.stringify(profileInfo));
    }, [profileInfo]);

    const buyTicket = (ticketData) => {
        const newTicket = {
            ...ticketData,
            id: `${ticketData.id}-${Date.now()}` // Уникальный ID
        };
        setTickets([...tickets, newTicket]);
    };

    const cancelTicket = (ticketId) => {
        setTickets(tickets.filter((ticket) => ticket.id !== ticketId));
    };

    const updateProfile = (newInfo) => {
        setProfileInfo(newInfo);
    };

    return (
        <TicketContext.Provider value={{
            tickets,
            buyTicket,
            cancelTicket,
            profileInfo,
            updateProfile
        }}>
            {children}
        </TicketContext.Provider>
    );
};