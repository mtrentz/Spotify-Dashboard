import React from "react";

const LoadingDots = () => {
  return (
    <div className="flex justify-center h-[40px]">
      <div className="spinner-grow text-blue mx-1 w-2 h-2" role="status"></div>
      <div
        className="spinner-grow text-blue delay-100 mx-1 w-2 h-2"
        role="status"
      ></div>
      <div
        className="spinner-grow text-blue delay-200 mx-1 w-2 h-2"
        role="status"
      ></div>
    </div>
  );
};

export default LoadingDots;
