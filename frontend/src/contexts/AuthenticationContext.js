import { createContext, useState, useEffect } from "react";

const AuthenticationContext = createContext();

export default AuthenticationContext;

export const AuthenticationProvider = ({ children }) => {
  const [authenticated, setAuthenticated] = useState(false);

  const storeToken = (token) => {
    localStorage.setItem("authToken", JSON.stringify(token));
    // Set expires at at 1 hour from now
    refreshExpiration();
    setAuthenticated(true);
  };

  const removeToken = () => {
    localStorage.removeItem("authToken");
    localStorage.removeItem("expiresAt");
    setAuthenticated(false);
  };

  const refreshExpiration = () => {
    // Set expires at at 1 hour from now
    const expiresAt = new Date();
    expiresAt.setHours(expiresAt.getHours() + 1);
    localStorage.setItem("expiresAt", JSON.stringify(expiresAt));
  };

  const isExpired = () => {
    const expiresAt = new Date(JSON.parse(localStorage.getItem("expiresAt")));
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
      setAuthenticated(false);
    } else {
      setAuthenticated(true);
    }
  }, []);

  const contextData = {
    authenticated: authenticated,
    storeToken: storeToken,
    getToken: getToken,
    removeToken: removeToken,
    isExpired: isExpired,
    refreshExpiration: refreshExpiration,
  };

  return (
    <AuthenticationContext.Provider value={contextData}>
      {children}
    </AuthenticationContext.Provider>
  );
};
