import React, { useState, useEffect, useContext } from "react";

import useAxios from "../../hooks/useAxios";

const AuthorizeButton = () => {
  const [authUrl, setAuthUrl] = useState("/");

  const axios = useAxios();

  useEffect(() => {
    axios
      .get("/auth/")
      .then((res) => {
        setAuthUrl(res.data.url);
      })
      .catch((err) => {
        console.log(err);
      });
  }, []);

  return (
    <a
      href={authUrl}
      target="_blank"
      className="btn btn-outline-teal w-32 h-7 btn-sm"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        className="icon icon-tabler icon-tabler-brand-spotify"
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
        <circle cx="12" cy="12" r="9"></circle>
        <path d="M8 11.973c2.5 -1.473 5.5 -.973 7.5 .527"></path>
        <path d="M9 15c1.5 -1 4 -1 5 .5"></path>
        <path d="M7 9c2 -1 6 -2 10 .5"></path>
      </svg>
      Authorize
    </a>
  );
};

export default AuthorizeButton;
