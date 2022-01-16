import React from "react";
import { useContext, useEffect, useState } from "react";

import ApiContext from "../Contexts/ApiContext";
import { generateTrendIcon } from "../helpers";

import Chart from "react-apexcharts";
import TrendingUp from "../Utilities/TrendingUp";
import TrendingDown from "../Utilities/TrendingDown";
import TrendingSideways from "../Utilities/TrendingSideways";
import PeriodDropdown from "../Utilities/PeriodDropdown";

const TimePlayedChart = () => {
  const { api } = useContext(ApiContext);

  const [timePlayedData, setTimePlayedData] = useState([]);

  const [period, setPeriod] = useState("Last 7 days");

  // Map the text option to the value to API Call
  const periodOptions = {
    "Last 7 days": 7,
    "Last 30 days": 30,
    "Last 90 days": 90,
    "All Time": 99999,
  };

  const handlePeriodChange = (e) => {
    setPeriod(e.target.text);
  };

  useEffect(() => {
    api
      .get("/time-played/", { params: { days: periodOptions[period] } })
      .then((res) => {
        setTimePlayedData(res.data);
      })
      .catch((err) => {
        console.log(err);
      });
  }, [period]);

  const status = {
    series: [
      {
        name: "Hours Played",
        // Unpack data into array of hours
        data: timePlayedData.map((item) =>
          (item.minutes_played / 60).toFixed(2)
        ),
      },
    ],
    options: {
      chart: {
        type: "area",
        fontFamily: "inherit",
        height: 40,
        sparkline: {
          enabled: true,
        },
        animations: {
          enabled: false,
        },
      },
      dataLabels: {
        enabled: false,
      },
      fill: {
        opacity: 0.25,
        type: "solid",
      },
      stroke: {
        width: 2,
        lineCap: "round",
        curve: "smooth",
      },
      grid: {
        strokeDashArray: 4,
      },
      xaxis: {
        labels: {
          padding: 0,
        },
        tooltip: {
          enabled: false,
        },
        axisBorder: {
          show: false,
        },
        type: "datetime",
      },
      yaxis: {
        labels: {
          padding: 4,
        },
      },
      labels: timePlayedData.map((item) => item.date),
      colors: ["#206bc4"],
      legend: {
        show: false,
      },
    },
  };

  return (
    <div className="card mx-10">
      <div className="card-body">
        <div className="d-flex align-items-center">
          <div className="subheader">Hours Played</div>
          <div className="ms-auto lh-1">
            <PeriodDropdown
              current={period}
              options={Object.keys(periodOptions)}
              handleClick={handlePeriodChange}
            />
          </div>
        </div>
        <div className="d-flex align-items-baseline">
          <div className="h1 mb-0 me-2">240</div>
          <div className="me-auto">
            <TrendingUp value="8%" />
          </div>
        </div>
      </div>
      <Chart
        id="chart-revenue-bg"
        className="chart-sm"
        style={{ minHeight: 40 + "px" }}
        series={status.series}
        options={status.options}
        type="area"
        height="40"
      />
    </div>
  );
};

export default TimePlayedChart;
