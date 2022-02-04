import React, { useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";

import TopAlbums from "../components/Charts/TopAlbums";

const YearInReview = () => {
  const { year } = useParams();
  const navigate = useNavigate();

  function isPositiveInteger(str) {
    const num = Number(str);
    if (Number.isInteger(num) && num > 0) {
      return true;
    }
    return false;
  }

  useEffect(() => {
    //   Redirect to home page if year is not a valid number
    if (!isPositiveInteger(year)) {
      navigate("/");
    }
  }, []);

  return (
    <div>
      <TopAlbums />
    </div>
  );
};

export default YearInReview;
