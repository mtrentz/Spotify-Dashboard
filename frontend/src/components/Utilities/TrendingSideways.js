import React from "react";

const TrendingSideways = ({ value }) => {
  return (
    <span
      className="text-orange d-inline-flex align-items-center lh-1"
      data-bs-toggle="tooltip"
      data-bs-placement="bottom"
      title="Trend calculated comparing with previous period of same length."
    >
      {value}
      <svg
        xmlns="http://www.w3.org/2000/svg"
        className="icon icon-tabler icon-tabler-minus"
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
        <line x1="5" y1="12" x2="19" y2="12"></line>
      </svg>
    </span>
  );
};

export default TrendingSideways;
