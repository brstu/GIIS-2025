import React from "react";
import { carData } from "../RentPage/car.data";
import "./CarDetailPage.css";
import { useNavigate, useParams } from "react-router";

const CarDetailPage = () => {
  const { carId } = useParams();
  let navigate = useNavigate();

  const car = carData.find((car) => car.id === parseInt(carId));

  if (!car) {
    return <div>Автомобиль не найден.</div>;
  }

  return (
    <div className="car-detail-wrapper">
      <button
        className="back-button"
        onClick={() => {
          navigate(-1);
        }}
      >
        Назад
      </button>
      <div className="car-detail">
        <div className="car-image">
          <img src={car.image} alt={`${car.brand} ${car.model}`} />
        </div>
        <div className="car-info">
          <h1>
            {car.brand} {car.model}
          </h1>
          <p className="car-price">
            <strong>Цена:</strong> {car.price}$ / день
          </p>
          <p>
            <strong>Характеристики:</strong> {car.specs}
          </p>
          <p>
            <strong>Условия аренды:</strong> {car.rentTerms}
          </p>
          <p>
            <strong>Описание:</strong> {car.description}
          </p>
          <a href={`/car/${car.id}/booking`}>
            <button className="book-button">Забронировать</button>
          </a>
        </div>
      </div>
    </div>
  );
};

export default CarDetailPage;
