import React, { useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";

import TopAlbumsYear from "../components/Charts/YearReviewCharts/TopAlbumsYear";
import TopArtistsYear from "../components/Charts/YearReviewCharts/TopArtistsYear";
import TopTracksYear from "../components/Charts/YearReviewCharts/TopTracksYear";
import TimePlayedYear from "../components/Charts/YearReviewCharts/TimePlayedYear";

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
    <div className="flex flex-col gap-3">
      <TimePlayedYear year={year} />
      <TopAlbumsYear year={year} />
      <TopArtistsYear year={year} />
      <TopTracksYear year={year} />
    </div>
  );
};

export default YearInReview;
