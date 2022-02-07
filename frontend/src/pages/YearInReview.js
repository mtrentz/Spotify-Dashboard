import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import moment from "moment";

import useAxios from "../hooks/useAxios";

import TopAlbumsYear from "../components/Charts/YearReviewCharts/TopAlbumsYear";
import TopArtistsYear from "../components/Charts/YearReviewCharts/TopArtistsYear";
import TopTracksYear from "../components/Charts/YearReviewCharts/TopTracksYear";
import TimePlayedYear from "../components/Charts/YearReviewCharts/TimePlayedYear";
import StatsTableYear from "../components/Charts/YearReviewCharts/StatsTableYear";
import TimePlayedPerHourOfDay from "../components/Charts/YearReviewCharts/TimePlayedPerHourOfDay";
import TimePlayedPerDayOfWeek from "../components/Charts/YearReviewCharts/TimePlayedPerDayOfWeek";

const YearInReview = () => {
  const { year } = useParams();
  const navigate = useNavigate();

  const axios = useAxios();
  const [dateLimits, setDateLimits] = useState();

  function isPositiveInteger(str) {
    const num = Number(str);
    if (Number.isInteger(num) && num > 0) {
      return true;
    }
    return false;
  }

  const formateDate = (dateStr) => {
    return moment(dateStr, "YYYYY-MM-DD").format("MMM Do");
  };

  const browserTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

  useEffect(() => {
    //   Redirect to home page if year is not a valid number
    if (!isPositiveInteger(year)) {
      navigate("/");
    }

    axios
      .get("/first-and-last-day-year/", {
        params: { year: year, timezone: browserTimezone },
      })
      .then((res) => {
        setDateLimits(res.data);
      })
      .catch((err) => {
        console.log(err);
      });
  }, [year]);

  return (
    <div>
      <div className="flex flex-row md:w-4/6 lg:w-1/2">
        <div className="col mx-2 mb-3">
          <div className="page-pretitle">{year}</div>
          <h2 className="page-title">Year in Review</h2>
        </div>
        <div className="col ">
          <div className="page-pretitle text-center w-32">
            Data available from
          </div>
          <div className="flex flex-row gap-3 justify-start w-64">
            <h3 className="page-title">
              {dateLimits ? formateDate(dateLimits.first_day) : ""}
            </h3>
            <h3 className="page-title">-</h3>
            <h3 className="page-title">
              {dateLimits ? formateDate(dateLimits.last_day) : ""}
            </h3>
          </div>
        </div>
      </div>
      <div className="m-2 flex flex-col gap-2 md:grid md:grid-cols-2 md:grid-flow-row md:auto-rows-min">
        <div className="order-none md:order-1 row-span-1">
          <TimePlayedYear year={year} />
        </div>
        <div className="order-none md:order-3 row-span-2">
          <TopArtistsYear year={year} />
        </div>
        <div className="order-none md:order-2 row-span-4">
          <TopAlbumsYear year={year} />
        </div>
        <div className="order-none md:order-4 row-span-4">
          <TopTracksYear year={year} />
        </div>
        <div className="order-none md:order-7 row-span-4">
          <StatsTableYear year={year} />
        </div>
        <div className="order-none md:order-6 row-span-4">
          <TimePlayedPerHourOfDay year={year} />
        </div>
        <div className="order-none md:order-5 row-span-2">
          <TimePlayedPerDayOfWeek year={year} />
        </div>
      </div>
    </div>
  );
};

export default YearInReview;
