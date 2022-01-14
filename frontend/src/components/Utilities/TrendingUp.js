import React from "react";

const TrendingUp = ({ value }) => {
  return (
    <span className="text-green d-inline-flex align-items-center lh-1">
      {value}
      {/* <!-- Download SVG icon from http://tabler-icons.io/i/trending-up --> */}
      <svg
        xmlns="http://www.w3.org/2000/svg"
        className="icon ms-1"
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
        <polyline points="3 17 9 11 13 15 21 7"></polyline>
        <polyline points="14 7 21 7 21 14"></polyline>
      </svg>
    </span>
  );
};

export default TrendingUp;
