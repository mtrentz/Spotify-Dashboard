import React from "react";
import { useContext, useEffect, useState } from "react";

import useAxios from "../../hooks/useAxios";
import { generateTrendComponent } from "../helpers";

import Chart from "react-apexcharts";
import PeriodDropdown from "../Utilities/PeriodDropdown";
import LoadingDots from "../Utilities/LoadingDots";

const TimePlayedChart = () => {
  const axios = useAxios();

  const startingGraphStatus = {
    series: [
      {
        name: "Hours Played",
        // Unpack data into array of hours
        data: [1, 2, 3],
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
      // // Check if its gonna look ugly when I have a lot of data
      // markers: {
      //   size: 2,
      //   strokeWidth: 1,
      // },
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
      labels: ["2020-01-01", "2020-01-02", "2020-01-03"],
      colors: ["#206bc4"],
      legend: {
        show: false,
      },
    },
  };

  const [timePlayedData, setTimePlayedData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [graphStatus, setGraphStatus] = useState(startingGraphStatus);

  const [period, setPeriod] = useState("Last 7 days");

  // Map the text option to the value to API Call
  const periodOptions = {
    "Last 7 days": 7,
    "Last 30 days": 30,
    "Last 90 days": 90,
    "Last 180 days": 180,
  };

  const handlePeriodChange = (e) => {
    setPeriod(e.target.text);
  };

  const browserTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

  useEffect(() => {
    axios
      .get("/time-played/", {
        params: { days: periodOptions[period], timezone: browserTimezone },
      })
      .then((res) => {
        setTimePlayedData(res.data);
        updateGraphStatus(res.data);
        setIsLoading(false);
      })
      .catch((err) => {
        console.log(err);
      });
  }, [period]);

  const updateGraphStatus = (res) => {
    // Make a copy of the previous status
    let newStatus = JSON.parse(JSON.stringify(startingGraphStatus));
    // Change the data points and labels
    newStatus.options.labels = res.items.map((item) => item.date);
    newStatus.series[0].data = res.items.map((item) =>
      (item.minutes_played / 60).toFixed(1)
    );
    setGraphStatus(newStatus);
  };

  return (
    <div className="card">
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
          <div className="h1 mb-0 me-2">
            {isLoading
              ? 0
              : (timePlayedData.total_minutes_played / 60).toFixed(0)}
          </div>
          <div className="me-auto">
            {/* Trend component */}
            {generateTrendComponent(isLoading ? 0 : timePlayedData.growth)}
          </div>
        </div>
      </div>
      {isLoading ? (
        <LoadingDots />
      ) : (
        <Chart
          id="chart-revenue-bg"
          className="chart-sm"
          style={{ minHeight: 40 + "px" }}
          series={graphStatus.series}
          options={graphStatus.options}
          type="area"
          height="40"
        />
      )}
    </div>
  );
};

export default TimePlayedChart;
