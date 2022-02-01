import axios from "../api/axios";
import { useEffect, useContext } from "react";
import { useNavigate } from "react-router-dom";

import AuthenticationContext from "../contexts/AuthenticationContext";

const useAxios = () => {
  const { getToken, isExpired, refreshExpiration, removeToken } = useContext(
    AuthenticationContext
  );

  const navigate = useNavigate();

  useEffect(() => {
    const requestIntercept = axios.interceptors.request.use(
      (config) => {
        // If token is expired, redirect to login
        if (isExpired()) {
          navigate("/login");
        }
        let token = getToken();
        config.headers["Authorization"] = `Token ${token}`;
        return config;
      },
      (error) => {
        Promise.reject(error);
      }
    );

    const responseIntercept = axios.interceptors.response.use(
      (response) => {
        // If request was successful refresh the token expiration
        refreshExpiration();
        return response;
      },
      async (error) => {
        // const prevRequest = error?.config;
        if (
          error?.response?.status === 403 ||
          error?.response?.status === 401
        ) {
          // If failed through authentication error:
          // Delete token from local storage
          removeToken();
          // Redirect to login
          navigate("/login");
        }
        return Promise.reject(error);
      }
    );

    return () => {
      axios.interceptors.request.eject(requestIntercept);
      axios.interceptors.response.eject(responseIntercept);
    };
  }, []);

  return axios;
};

export default useAxios;
