import React from "react";

const UploadHistoryButton = () => {
  return (
    <>
      <button
        type="button"
        className="btn btn-outline-primary btn-sm h-7"
        data-bs-toggle="offcanvas"
        href="#offcanvasEnd"
        aria-controls="offcanvasEnd"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="icon icon-tabler icon-tabler-plus"
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
          <line x1="12" y1="5" x2="12" y2="19"></line>
          <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
        Upload History
      </button>
    </>
  );
};

export default UploadHistoryButton;
