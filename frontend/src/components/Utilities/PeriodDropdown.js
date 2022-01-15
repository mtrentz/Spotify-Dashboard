import React from "react";

const PeriodDropdown = ({ current, options, handleClick }) => {
  return (
    <div className="dropdown">
      <a
        className="dropdown-toggle text-muted"
        href="#"
        data-bs-toggle="dropdown"
        aria-haspopup="true"
        aria-expanded="false"
      >
        {current}
      </a>
      <div className="dropdown-menu dropdown-menu-end">
        {options.map((option, index) =>
          option === current ? (
            <a
              className="dropdown-item active"
              onClick={handleClick}
              key={index}
            >
              {option}
            </a>
          ) : (
            <a className="dropdown-item" onClick={handleClick} key={index}>
              {option}
            </a>
          )
        )}
      </div>
    </div>
  );
};

export default PeriodDropdown;
