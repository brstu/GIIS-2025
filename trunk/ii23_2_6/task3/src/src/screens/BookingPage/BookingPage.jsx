import React from "react";
import { useParams } from "react-router-dom";
import { useForm } from "react-hook-form";
import { carData } from "../RentPage/car.data.js";
import "./BookingPage.css";

const BookingPage = () => {
  const { id } = useParams();
  const car = carData.find((c) => c.id === parseInt(id));

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm();

  const onSubmit = (values) => {
    const existing = JSON.parse(localStorage.getItem("bookings")) || [];

    const booking = {
      name: values.name,
      contact: values.contact,
      startDate: values.startDate,
      endDate: values.endDate,
      car: car, // Весь объект машины сохраняем как есть
    };

    existing.push(booking);
    localStorage.setItem("bookings", JSON.stringify(existing));

    alert(`Заявка отправлена! Спасибо, ${values.name}`);
    console.log("Booking Data:", booking);
  };

  if (!car) {
    return <p>Автомобиль не найден</p>;
  }

  return (
    <div className="booking-page">
      <div className="booking-car-info">
        <img src={car.image} alt={`${car.brand} ${car.model}`} />
        <h2>
          {car.brand} {car.model}
        </h2>
        <p>{car.specs}</p>
        <p>
          <strong>Цена:</strong> {car.price}$ / день
        </p>
        <p>
          <strong>Условия:</strong> {car.rentTerms}
        </p>
      </div>

      <form className="booking-form" onSubmit={handleSubmit(onSubmit)}>
        <h3>Бронирование</h3>

        <label>
          Имя:
          <input
            {...register("name", { required: "Введите имя" })}
            type="text"
          />
          {errors.name && <span className="error">{errors.name.message}</span>}
        </label>

        <label>
          Контакт (телефон или email):
          <input
            {...register("contact", {
              required: "Укажите контактные данные",
              minLength: 5,
            })}
            type="text"
          />
          {errors.contact && (
            <span className="error">{errors.contact.message}</span>
          )}
        </label>

        <label>
          Дата начала аренды:
          <input
            {...register("startDate", { required: "Выберите дату начала" })}
            type="date"
          />
          {errors.startDate && (
            <span className="error">{errors.startDate.message}</span>
          )}
        </label>

        <label>
          Дата завершения аренды:
          <input
            {...register("endDate", { required: "Выберите дату окончания" })}
            type="date"
          />
          {errors.endDate && (
            <span className="error">{errors.endDate.message}</span>
          )}
        </label>

        <button type="submit">Подтвердить бронирование</button>
      </form>
    </div>
  );
};

export default BookingPage;
