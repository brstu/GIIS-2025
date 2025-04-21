import React, { useEffect, useState } from "react";
import { carData } from "../RentPage/car.data.js";
import "./UserPage.css";

const UserPage = () => {
  const [bookings, setBookings] = useState([]);

  useEffect(() => {
    const stored = JSON.parse(localStorage.getItem("bookings")) || [];
    setBookings(stored);
  }, []);

  const handleDelete = (index) => {
    const updated = bookings.filter((_, i) => i !== index);
    localStorage.setItem("bookings", JSON.stringify(updated));
    setBookings(updated);
  };

  return (
    <div className="account-page">
      <h2>Мои бронирования</h2>

      {bookings.length === 0 ? (
        <p>У вас пока нет бронирований.</p>
      ) : (
        <div className="booking-list">
          {bookings.map((booking, index) => {
            const car = booking.car;
            return (
              <div key={index} className="booking-card">
                {car && (
                  <img src={car.image} alt={`${car.brand} ${car.model}`} />
                )}
                <div className="booking-info">
                  <h3>
                    {car?.brand} {car?.model}
                  </h3>
                  <p>
                    <strong>С:</strong> {booking.startDate}
                  </p>
                  <p>
                    <strong>По:</strong> {booking.endDate}
                  </p>
                  <p>
                    <strong>Имя:</strong> {booking.name}
                  </p>
                  <p>
                    <strong>Контакт:</strong> {booking.contact}
                  </p>
                  <button onClick={() => handleDelete(index)}>
                    Отменить бронирование
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default UserPage;
