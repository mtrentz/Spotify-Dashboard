import React, { useContext } from "react";
import { Link } from "react-router-dom";
import ThemeContext from "../components/Contexts/ThemeContext";

const Login = () => {
  const { theme } = useContext(ThemeContext);
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
            action="."
            method="get"
            autocomplete="off"
            data-bitwarden-watching="1"
          >
            <div className="card-body">
              <h2 className="card-title text-center mb-4">Login to continue</h2>
              <div className="mb-3">
                <label className="form-label">Username</label>
                <input
                  type="text"
                  className="form-control"
                  placeholder="Enter username"
                />
              </div>
              <div className="mb-2">
                <label className="form-label">Password</label>
                <div className="input-group input-group-flat">
                  <input
                    type="password"
                    className="form-control"
                    placeholder="Password"
                    autocomplete="off"
                  />
                  <span className="input-group-text"></span>
                </div>
              </div>

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
