import axios from "../api/axios";
import { useEffect, useContext } from "react";
import { useNavigate } from "react-router-dom";

import AuthenticationContext from "../contexts/AuthenticationContext";

const useAxios = () => {
  const { token } = useContext(AuthenticationContext);

  const navigate = useNavigate();

  useEffect(() => {
    const requestIntercept = axios.interceptors.request.use(
      (config) => {
        config.headers["Authorization"] = `Token ${token}`;
        return config;
      },
      (error) => {
        Promise.reject(error);
      }
    );

    const responseIntercept = axios.interceptors.response.use(
      (response) => response,
      async (error) => {
        const prevRequest = error?.config;
        if (
          error?.response?.status === 403 ||
          error?.response?.status === 401
        ) {
          //  If this is the first fail, try again
          if (!prevRequest?.sent) {
            prevRequest.sent = true;
            // Try again
            prevRequest.headers["Authorization"] = `Token ${token}`;
            return axios(prevRequest);
          }
          // If this is the second fail, go to login
          navigate("/login");
        }
        return Promise.reject(error);
      }
    );

    return () => {
      axios.interceptors.request.eject(requestIntercept);
      axios.interceptors.response.eject(responseIntercept);
    };
  }, [token]);

  return axios;
};

export default useAxios;