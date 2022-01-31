import { createContext, useState, useEffect } from "react";

const AuthenticationContext = createContext();

export default AuthenticationContext;

export const AuthenticationProvider = ({ children }) => {
  const [token, setToken] = useState("");
  const [authenticated, setAuthenticated] = useState(false);

  const storeToken = (token) => {
    localStorage.setItem("authToken", JSON.stringify(token));
    setToken(token);
    // Set expires at at 1 hour from now
    const expiresAt = new Date();
    expiresAt.setHours(expiresAt.getHours() + 1);
    localStorage.setItem("expiresAt", JSON.stringify(expiresAt));
    setAuthenticated(true);
  };

  const isExpired = () => {
    const expiresAt = new Date(localStorage.getItem("expiresAt"));
    return expiresAt < new Date();
  };

  const getToken = () => {
    const token = JSON.parse(localStorage.getItem("authToken"));
    return token;
  };

  useEffect(() => {
    // Check if token is expired
    if (isExpired()) {
      // Remove token from local storage
      localStorage.removeItem("authToken");
      localStorage.removeItem("expiresAt");
      setToken("");
      setAuthenticated(false);
    } else {
      // Set token
      setToken(getToken());
      setAuthenticated(true);
    }
  }, []);

  const contextData = {
    authenticated: authenticated,
    token: token,
    storeToken: storeToken,
    getToken: getToken,
    isExpired: isExpired,
  };

  return (
    <AuthenticationContext.Provider value={contextData}>
      {children}
    </AuthenticationContext.Provider>
  );
};
