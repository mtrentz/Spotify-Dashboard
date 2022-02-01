import React, { useContext, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { axiosUsers } from "../api/axios";

import ThemeContext from "../contexts/ThemeContext";
import AuthenticationContext from "../contexts/AuthenticationContext";

const Login = () => {
  const navigate = useNavigate();

  const { theme } = useContext(ThemeContext);
  const { storeToken } = useContext(AuthenticationContext);

  const [errorMessage, setErrorMessage] = useState("");

  const login = async (e) => {
    e.preventDefault();
    axiosUsers
      .post("/login/", {
        username: e.target.username.value,
        password: e.target.password.value,
      })
      .then((response) => {
        // Also sets authenticated and everything
        storeToken(response.data.token);
        navigate("/");
      })
      .catch((error) => {
        console.log(error);
        setErrorMessage("Invalid username or password");
      });
  };

  return (
    <body
      className={`border-top-wide border-primary d-flex flex-column ${
        theme === "dark" ? "theme-dark" : "theme-light"
      }`}
    >
      <div className="page page-center">
        <div className="container-tight py-4">
          <div class="text-center mb-4">
            <Link to="/">
              <h1 className="navbar-brand navbar-brand-autodark d-none-navbar-horizontal pe-0 pe-md-3">
                <img
                  src="/spotify_dashboard_logo.png"
                  width="110"
                  height="32"
                  alt="Tabler"
                  className="navbar-brand-image scale-90"
                />
              </h1>
            </Link>
          </div>
          <form
            className="card card-md"
            // action="."
            // method="get"
            // autocomplete="off"
            onSubmit={login}
          >
            <div className="card-body">
              {/* <h2 className="card-title text-center mb-4">Login to continue</h2> */}
              <div className="mb-3">
                <label htmlFor="username" className="form-label">
                  Username
                </label>
                <input
                  type="text"
                  id="username"
                  className={`form-control ${errorMessage ? "is-invalid" : ""}`}
                  aria-describedby="username"
                  placeholder="Enter username"
                />
              </div>

              <div className="mb-2">
                <label htmlFor="password" className="form-label">
                  Password
                </label>
                <div className="input-group input-group-flat">
                  <input
                    type="password"
                    id="password"
                    className={`form-control ${
                      errorMessage ? "is-invalid" : ""
                    }`}
                    placeholder="Password"
                    autocomplete="off"
                    aria-describedby="Password"
                  />
                </div>
              </div>
              {errorMessage ? (
                <h6 class="text-danger">{errorMessage}</h6>
              ) : null}
              <div className="form-footer">
                <button type="submit" className="btn btn-primary w-100">
                  Sign in
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </body>
  );
};

export default Login;
