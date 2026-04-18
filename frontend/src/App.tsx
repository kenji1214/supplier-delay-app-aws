import { Route, Routes } from "react-router-dom";
import BackorderDetailPage from "./pages/BackorderDetailPage";
import BackorderListPage from "./pages/BackorderListPage";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<BackorderListPage />} />
      <Route path="/backorders/:shipmentKey" element={<BackorderDetailPage />} />
    </Routes>
  );
}
