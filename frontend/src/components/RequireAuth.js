import { Navigate, Outlet } from "react-router-dom";
import useAuth from "../hooks/useAuth";

const RequireAuth = () => {
  const { authenticated } = useAuth();

  return authenticated ? <Outlet /> : <Navigate to="/login" />;
};

export default RequireAuth;
