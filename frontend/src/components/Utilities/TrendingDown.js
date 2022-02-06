import React from "react";

const TrendingDown = ({ value }) => {
  return (
    <span
      className="text-red d-inline-flex align-items-center lh-1"
      data-bs-toggle="tooltip"
      data-bs-placement="bottom"
      title="Trend calculated comparing with previous period of same length."
    >
      {value}
      <svg
        xmlns="http://www.w3.org/2000/svg"
        className="icon icon-tabler icon-tabler-trending-down"
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
        <polyline points="3 7 9 13 13 9 21 17"></polyline>
        <polyline points="21 10 21 17 14 17"></polyline>
      </svg>
    </span>
  );
};

export default TrendingDown;
