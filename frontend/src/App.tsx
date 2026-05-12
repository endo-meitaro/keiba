import { Routes, Route } from "react-router-dom";
import RaceList from "./pages/RaceList";
import RaceDetail from "./pages/RaceDetail";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<RaceList />} />
      <Route path="/races/:raceId" element={<RaceDetail />} />
    </Routes>
  );
}
