import React from "react";

const CardKPI = ({ value, text, trend }) => {
  return (
    <div className="card mx-10">
      <div className="card-body p-2 text-center">
        <div className="text-end text-green">{trend}</div>
        <div className="h1 m-0">{value}</div>
        <div className="text-muted mb-3">{text}</div>
      </div>
    </div>
  );
};

export default CardKPI;
