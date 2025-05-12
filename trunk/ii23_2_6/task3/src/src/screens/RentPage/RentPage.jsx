import React, { useState } from "react";
import { carData } from "./car.data";
import "./RentPage.css";

const RentPage = () => {
  const [selectedBrand, setSelectedBrand] = useState("");
  const [selectedModel, setSelectedModel] = useState("");
  const [minPrice, setMinPrice] = useState("");
  const [maxPrice, setMaxPrice] = useState("");
  const [selectedConditions, setSelectedConditions] = useState([]);

  const brands = [...new Set(carData.map((car) => car.brand))];
  const models = selectedBrand
    ? [
        ...new Set(
          carData.filter((c) => c.brand === selectedBrand).map((c) => c.model)
        ),
      ]
    : [];

  const handleConditionChange = (condition) => {
    if (selectedConditions.includes(condition)) {
      setSelectedConditions(selectedConditions.filter((c) => c !== condition));
    } else {
      setSelectedConditions([...selectedConditions, condition]);
    }
  };

  const filteredCars = carData.filter((car) => {
    const matchesBrand = selectedBrand ? car.brand === selectedBrand : true;
    const matchesModel = selectedModel ? car.model === selectedModel : true;
    const matchesMinPrice = minPrice ? car.price >= Number(minPrice) : true;
    const matchesMaxPrice = maxPrice ? car.price <= Number(maxPrice) : true;
    const matchesConditions = selectedConditions.length
      ? selectedConditions.every((cond) => car.conditions.includes(cond))
      : true;

    return (
      matchesBrand &&
      matchesModel &&
      matchesMinPrice &&
      matchesMaxPrice &&
      matchesConditions
    );
  });

  return (
    <div className="rent-wrapper">
      <div className="filter-panel">
        <h2>Фильтры</h2>

        <label>
          Марка:
          <select
            value={selectedBrand}
            onChange={(e) => {
              setSelectedBrand(e.target.value);
              setSelectedModel("");
            }}
          >
            <option value="">Все</option>
            {brands.map((brand) => (
              <option key={brand} value={brand}>
                {brand}
              </option>
            ))}
          </select>
        </label>

        <label>
          Модель:
          <select
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            disabled={!selectedBrand}
          >
            <option value="">Все</option>
            {models.map((model) => (
              <option key={model} value={model}>
                {model}
              </option>
            ))}
          </select>
        </label>

        <label>
          Цена:
          <div className="price-inputs">
            <input
              type="number"
              placeholder="от"
              value={minPrice}
              onChange={(e) => setMinPrice(e.target.value)}
            />
            <input
              type="number"
              placeholder="до"
              value={maxPrice}
              onChange={(e) => setMaxPrice(e.target.value)}
            />
          </div>
        </label>

        <fieldset className="checkboxes">
          <legend>Условия аренды:</legend>
          {["без залога", "минимум 1 день", "минимум 2 дня"].map((cond) => (
            <label key={cond}>
              <input
                type="checkbox"
                checked={selectedConditions.includes(cond)}
                onChange={() => handleConditionChange(cond)}
              />
              {cond}
            </label>
          ))}
        </fieldset>
      </div>

      <div className="cars-list">
        {filteredCars.map((car) => (
          <div key={car.id} className="car-card">
            <img src={car.image} alt={`${car.brand} ${car.model}`} />
            <h3>
              {car.brand} {car.model}
            </h3>
            <p>
              <strong>Цена:</strong> {car.price}$ / день
            </p>
            <p>
              <strong>Характеристики:</strong> {car.specs}
            </p>
            <p>
              <strong>Условия аренды:</strong> {car.rentTerms}
            </p>
            <a href={`/car/${car.id}/`}>
              <button className="book-button">Забронировать</button>
            </a>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RentPage;
