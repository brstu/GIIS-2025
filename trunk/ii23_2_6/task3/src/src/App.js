import { Route, Routes } from "react-router-dom";
import RentPage from "./screens/RentPage/RentPage";
import CarDetailPage from "./screens/CarDetailPage/CarDetailPage";
import BookingPage from "./screens/BookingPage/BookingPage";
import UserPage from "./screens/UserPage/UserPage";
import Header from "./components/header/Header";

function App() {
  return (
    <Routes>
      <Route
        path="/"
        element={
          <>
            <Header />
            <RentPage />
          </>
        }
      />
      <Route path="/car/:carId" element={<CarDetailPage />} />
      <Route path="/car/:id/booking" element={<BookingPage />} />
      <Route path="/account" element={<UserPage />} />
    </Routes>
  );
}

export default App;
