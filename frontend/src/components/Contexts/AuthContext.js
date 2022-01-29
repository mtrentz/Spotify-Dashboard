import { createContext, useState } from "react";
import { useNavigate } from "react-router-dom";

import ApiContext from "./ApiContext";

const AuthContext = createContext();

export default AuthContext;

export const AuthProvider = ({ children }) => {
  const [authToken, setAuthToken] = useState(() =>
    localStorage.getItem("authToken")
      ? JSON.parse(localStorage.getItem("authToken"))
      : null
  );

  const navigate = useNavigate();

  return (
    <AuthContext.Provider value={contextData}>{children}</AuthContext.Provider>
  );
};
