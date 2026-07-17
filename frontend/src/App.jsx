import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Profile from "./pages/Profile";
import EmployeeList from "./pages/EmployeeList";
import AddEmployee from "./pages/AddEmployee";
import CustomerList from "./pages/CustomerList";
import AddCustomer from "./pages/AddCustomer";
import OrderList from "./pages/OrderList";
import AddOrder from "./pages/AddOrder";
import ProtectedRoute from "./components/ProtectedRoute";
import DashboardLayout from "./layouts/DashboardLayout";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />

        <Route element={<ProtectedRoute />}>
          <Route element={<DashboardLayout />}>
            <Route path="/employees/profile" element={<Profile />} />
            <Route path="/employees/list" element={<EmployeeList />} />
            <Route path="/employees/add" element={<AddEmployee />} />
            
            <Route path="/customers/list" element={<CustomerList />} />
            <Route path="/customers/add" element={<AddCustomer />} />

            <Route path="/orders/list" element={<OrderList />} />
            <Route path="/orders/add" element={<AddOrder />} />
          </Route>
        </Route>

        <Route path="*" element={<Navigate to="/employees/profile" />} />
      </Routes>
    </BrowserRouter>
  );
}