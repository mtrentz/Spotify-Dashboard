import { createContext, useState, useEffect } from "react";
import { axiosUsers } from "../api/axios";

const AuthenticationContext = createContext();

export default AuthenticationContext;

export const AuthenticationProvider = ({ children }) => {
  // const [authenticated, setAuthenticated] = useState(false);
  const [token, setToken] = useState("");
  const [authenticated, setAuthenticated] = useState(false);

  //   Make a request and check if auth is required
  useEffect(() => {
    const sessionToken = JSON.parse(sessionStorage.getItem("authToken")) || "";
    setToken(sessionToken);
  }, []);

  const contextData = {
    authenticated: authenticated,
    token: token,
    setAuthenticated: setAuthenticated,
    setToken: setToken,
  };

  return (
    <AuthenticationContext.Provider value={contextData}>
      {children}
    </AuthenticationContext.Provider>
  );
};
