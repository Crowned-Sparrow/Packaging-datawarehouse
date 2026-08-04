import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Profile from "./pages/Profile";
import EmployeeList from "./pages/EmployeeList";
import AddEmployee from "./pages/AddEmployee";
import CustomerList from "./pages/CustomerList";
import AddCustomer from "./pages/AddCustomer";
import OrderList from "./pages/OrderList";
import AddOrder from "./pages/AddOrder";
import MaterialList from "./pages/MaterialList";
import AddMaterial from "./pages/AddMaterial";
import SupplierList from "./pages/SupplierList";
import AddSupplier from "./pages/AddSupplier";
import SupplyDetailList from "./pages/SupplyDetailList";
import MachineList from "./pages/MachineList";
import AddMachine from "./pages/AddMachine";
import ProductionLogList from "./pages/ProductionLogList";
import AddProductionLog from "./pages/AddProductionLog";
import BreakdownCodeList from "./pages/BreakdownCodeList";
import AddBreakdownCode from "./pages/AddBreakdownCode";
import BreakdownLogList from "./pages/BreakdownLogList";
import AddBreakdownLog from "./pages/AddBreakdownLog";
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

            <Route path="/materials/list" element={<MaterialList />} />
            <Route path="/materials/add" element={<AddMaterial />} />

            <Route path="/supplies/suppliers/list" element={<SupplierList />} />
            <Route path="/supplies/suppliers/add" element={<AddSupplier />} />
            <Route path="/supplies/details/list" element={<SupplyDetailList />} />

            <Route path="/corrugating/machines/list" element={<MachineList />} />
            <Route path="/corrugating/machines/add" element={<AddMachine />} />
            <Route path="/corrugating/logs/list" element={<ProductionLogList />} />
            <Route path="/corrugating/logs/add" element={<AddProductionLog />} />
            <Route path="/corrugating/breakdowns/codes/list" element={<BreakdownCodeList />} />
            <Route path="/corrugating/breakdowns/codes/add" element={<AddBreakdownCode />} />
            <Route path="/corrugating/breakdowns/logs/list" element={<BreakdownLogList />} />
            <Route path="/corrugating/breakdowns/logs/add" element={<AddBreakdownLog />} />
          </Route>
        </Route>

        <Route path="*" element={<Navigate to="/employees/profile" />} />
      </Routes>
    </BrowserRouter>
  );
}