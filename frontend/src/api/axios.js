import axios from "axios";
const BASE_URL = "http://localhost:8080/api";

export default axios.create({
  baseURL: `${BASE_URL}/spotify`,
});

export const axiosUsers = axios.create({
  baseURL: `${BASE_URL}/users`,
});
