import React, { useContext, useEffect, useState } from "react";
import { Link, Navigate, Outlet } from "react-router-dom";

import useAxios from "../hooks/useAxios";
import ThemeContext from "../contexts/ThemeContext";
import AuthenticationContext from "../contexts/AuthenticationContext";

import OffcanvasFileUpload from "./Utilities/OffcanvasFileUpload";
import UploadHistoryButton from "./Utilities/UploadHistoryButton";
import AuthorizeButton from "./Utilities/AuthorizeButton";
import Notifications from "./Utilities/Notifications";
import ThemeSwitch from "./Utilities/ThemeSwitch";
import Footer from "./Footer";

const Layout = ({ children }) => {
  const axios = useAxios();
  const { theme } = useContext(ThemeContext);
  const { removeToken } = useContext(AuthenticationContext);

  // Authorized for spotify API, not login
  const [isAuthorized, setIsAuthorized] = useState(true);
  const [years, setYears] = useState([]);

  const browserTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

  const logout = () => {
    removeToken();
    Navigate("/login");
  };

  useEffect(() => {
    // Request Authorization Status (for spotify api)
    axios
      .get("/is-authorized/")
      .then((res) => {
        setIsAuthorized(res.data.is_authorized);
      })
      .catch((err) => {
        console.log(err);
      });

    // Request Available Years
    axios
      .get("/available-years/", { timezone: browserTimezone })
      .then((res) => {
        setYears(res.data.map((year) => year.year).reverse());
      })
      .catch((err) => {
        console.log(err);
      });
  }, []);

  return (
    <div
      className={`page relative ${
        theme === "dark" ? "theme-dark" : "theme-light"
      }`}
    >
      <header className="navbar navbar-expand-md navbar-light d-print-none">
        <div className="container-xl">
          <button
            className="navbar-toggler"
            type="button"
            data-bs-toggle="collapse"
            data-bs-target="#navbar-menu"
          >
            <span className="navbar-toggler-icon"></span>
          </button>
          <h1 className="navbar-brand navbar-brand-autodark d-none-navbar-horizontal pe-0 pe-md-3">
            <Link to="/">
              <img
                src="/spotify_dashboard_logo.png"
                width="110"
                height="32"
                alt="Tabler"
                className="navbar-brand-image scale-90"
              />
            </Link>
          </h1>
          <div className="navbar-nav flex-row order-md-last">
            <div className="nav-item d-none d-md-flex me-3">
              <div className="btn-list">
                <a
                  href="https://github.com/mtrentz/Spotify-Dashboard"
                  className="btn"
                  target="_blank"
                  rel="noreferrer"
                >
                  {/* <!-- Download SVG icon from http://tabler-icons.io/i/brand-github --> */}
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="icon"
                    width="24"
                    height="24"
                    viewBox="0 0 24 24"
                    strokeWidth="2"
                    stroke="currentColor"
                    fill="none"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
                    <path d="M9 19c-4.3 1.4 -4.3 -2.5 -6 -3m12 5v-3.5c0 -1 .1 -1.4 -.5 -2c2.8 -.3 5.5 -1.4 5.5 -6a4.6 4.6 0 0 0 -1.3 -3.2a4.2 4.2 0 0 0 -.1 -3.2s-1.1 -.3 -3.5 1.3a12.3 12.3 0 0 0 -6.2 0c-2.4 -1.6 -3.5 -1.3 -3.5 -1.3a4.2 4.2 0 0 0 -.1 3.2a4.6 4.6 0 0 0 -1.3 3.2c0 4.6 2.7 5.7 5.5 6c-.6 .6 -.6 1.2 -.5 2v3.5"></path>
                  </svg>
                  Github
                </a>
              </div>
            </div>
            <ThemeSwitch />
          </div>
        </div>
      </header>
      <div className="navbar-expand-md">
        <div className="collapse navbar-collapse" id="navbar-menu">
          <div className="navbar navbar-light">
            <div className="container-xl">
              <ul className="navbar-nav">
                <li className="nav-item">
                  <Link to="/" className="nav-link">
                    <span className="nav-link-icon d-md-none d-lg-inline-block">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        className="icon icon-tabler icon-tabler-chart-bar"
                        width="24"
                        height="24"
                        viewBox="0 0 24 24"
                        strokeWidth="2"
                        stroke="currentColor"
                        fill="none"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <path
                          stroke="none"
                          d="M0 0h24v24H0z"
                          fill="none"
                        ></path>
                        <rect x="3" y="12" width="6" height="8" rx="1"></rect>
                        <rect x="9" y="8" width="6" height="12" rx="1"></rect>
                        <rect x="15" y="4" width="6" height="16" rx="1"></rect>
                        <line x1="4" y1="20" x2="18" y2="20"></line>
                      </svg>
                    </span>
                    <span className="nav-link-title">Home</span>
                  </Link>
                </li>

                <li className="nav-item">
                  <a className="nav-link disabled" href="./docs/index.html">
                    <span className="nav-link-icon d-md-none d-lg-inline-block">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        className="icon icon-tabler icon-tabler-music"
                        width="24"
                        height="24"
                        viewBox="0 0 24 24"
                        strokeWidth="2"
                        stroke="currentColor"
                        fill="none"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <path
                          stroke="none"
                          d="M0 0h24v24H0z"
                          fill="none"
                        ></path>
                        <circle cx="6" cy="17" r="3"></circle>
                        <circle cx="16" cy="17" r="3"></circle>
                        <polyline points="9 17 9 4 19 4 19 17"></polyline>
                        <line x1="9" y1="8" x2="19" y2="8"></line>
                      </svg>
                    </span>
                    <span className="nav-link-title">Tracks</span>
                  </a>
                </li>
                <li className="nav-item">
                  <a className="nav-link disabled" href="./docs/index.html">
                    <span className="nav-link-icon d-md-none d-lg-inline-block">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        className="icon icon-tabler icon-tabler-disc"
                        width="24"
                        height="24"
                        viewBox="0 0 24 24"
                        strokeWidth="2"
                        stroke="currentColor"
                        fill="none"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <path
                          stroke="none"
                          d="M0 0h24v24H0z"
                          fill="none"
                        ></path>
                        <circle cx="12" cy="12" r="9"></circle>
                        <circle cx="12" cy="12" r="1"></circle>
                        <path d="M7 12a5 5 0 0 1 5 -5"></path>
                        <path d="M12 17a5 5 0 0 0 5 -5"></path>
                      </svg>
                    </span>
                    <span className="nav-link-title">Albums</span>
                  </a>
                </li>
                <li className="nav-item">
                  <a className="nav-link disabled" href="./docs/index.html">
                    <span className="nav-link-icon d-md-none d-lg-inline-block">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        className="icon icon-tabler icon-tabler-microphone-2"
                        width="24"
                        height="24"
                        viewBox="0 0 24 24"
                        strokeWidth="2"
                        stroke="currentColor"
                        fill="none"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <path
                          stroke="none"
                          d="M0 0h24v24H0z"
                          fill="none"
                        ></path>
                        <path d="M15.002 12.9a5 5 0 1 0 -3.902 -3.9"></path>
                        <path d="M15.002 12.9l-3.902 -3.899l-7.513 8.584a2 2 0 1 0 2.827 2.83l8.588 -7.515z"></path>
                      </svg>
                    </span>
                    <span className="nav-link-title">Artists</span>
                  </a>
                </li>
                <li className="nav-item dropdown">
                  <a
                    className="nav-link dropdown-toggle"
                    href="#navbar-base"
                    data-bs-toggle="dropdown"
                    data-bs-auto-close="outside"
                    role="button"
                    aria-expanded="false"
                  >
                    <span className="nav-link-icon d-md-none d-lg-inline-block">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        className="icon icon-tabler icon-tabler-calendar"
                        width="24"
                        height="24"
                        viewBox="0 0 24 24"
                        strokeWidth="2"
                        stroke="currentColor"
                        fill="none"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <path
                          stroke="none"
                          d="M0 0h24v24H0z"
                          fill="none"
                        ></path>
                        <rect x="4" y="5" width="16" height="16" rx="2"></rect>
                        <line x1="16" y1="3" x2="16" y2="7"></line>
                        <line x1="8" y1="3" x2="8" y2="7"></line>
                        <line x1="4" y1="11" x2="20" y2="11"></line>
                        <line x1="11" y1="15" x2="12" y2="15"></line>
                        <line x1="12" y1="15" x2="12" y2="18"></line>
                      </svg>
                    </span>
                    <span className="nav-link-title">Year in Review</span>
                  </a>
                  <div className="dropdown-menu">
                    <div className="dropdown-menu-columns">
                      <div className="dropdown-menu-column">
                        {years
                          ? years.map((year, index) => {
                              return (
                                <a
                                  key={index}
                                  className="dropdown-item disabled"
                                  href="./empty.html"
                                >
                                  {year}
                                </a>
                              );
                            })
                          : null}
                      </div>
                    </div>
                  </div>
                </li>
              </ul>
              <ul className="navbar-nav">
                {isAuthorized ? null : (
                  <li className="nav-link">
                    <AuthorizeButton />
                  </li>
                )}
                <li className="nav-link">
                  <UploadHistoryButton />
                </li>
                <li className="nav-link">
                  <button className="flex" type="button" onClick={logout}>
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      className="icon icon-tabler icon-tabler-logout"
                      width="24"
                      height="24"
                      viewBox="0 0 24 24"
                      strokeWidth="2"
                      stroke="currentColor"
                      fill="none"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
                      <path d="M14 8v-2a2 2 0 0 0 -2 -2h-7a2 2 0 0 0 -2 2v12a2 2 0 0 0 2 2h7a2 2 0 0 0 2 -2v-2"></path>
                      <path d="M7 12h14l-3 -3m0 6l3 -3"></path>
                    </svg>
                    <span className="md:hidden ml-2">Logout</span>
                  </button>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
      <div className="page-wrapper">
        <div className="page-body">
          <div className="container-xl">
            <Outlet />
          </div>
        </div>
      </div>
      <OffcanvasFileUpload />
      <Notifications />
      <Footer />
    </div>
  );
};

export default Layout;
