import React from "react";

const TrendingDown = ({ value }) => {
  return (
    <span className="text-red d-inline-flex align-items-center lh-1">
      {value}
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="icon icon-tabler icon-tabler-trending-down"
        width="24"
        height="24"
        viewBox="0 0 24 24"
        stroke-width="2"
        stroke="currentColor"
        fill="none"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
        <polyline points="3 7 9 13 13 9 21 17"></polyline>
        <polyline points="21 10 21 17 14 17"></polyline>
      </svg>
    </span>
  );
};

export default TrendingDown;
