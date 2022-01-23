import { createContext, useState } from "react";
import axios from "axios";

const ApiContext = createContext();

export default ApiContext;

export const ApiProvider = ({ children }) => {
  const api = axios.create({
    baseURL: "http://localhost:8080/api/spotify",
    timeout: 10000,
  });

  const contextData = {
    api: api,
  };

  return (
    <ApiContext.Provider value={contextData}>{children}</ApiContext.Provider>
  );
};
