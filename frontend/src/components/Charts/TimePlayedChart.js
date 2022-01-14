import React from "react";
import { useState } from "react";
import Chart from "react-apexcharts";
import TrendingUp from "../Utilities/TrendingUp";
import TrendingDown from "../Utilities/TrendingDown";
import TrendingSideways from "../Utilities/TrendingSideways";
import PeriodDropdown from "../Utilities/PeriodDropdown";

const TimePlayedChart = () => {
  const status = {
    series: [
      {
        name: "Profits",
        data: [
          37, 35, 44, 28, 36, 24, 65, 31, 37, 39, 62, 51, 35, 41, 35, 27, 93,
          53, 61, 27, 54, 43, 19, 46, 39, 62, 51, 35, 41, 67,
        ],
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
      labels: [
        "2020-06-21",
        "2020-06-22",
        "2020-06-23",
        "2020-06-24",
        "2020-06-25",
        "2020-06-26",
        "2020-06-27",
        "2020-06-28",
        "2020-06-29",
        "2020-06-30",
        "2020-07-01",
        "2020-07-02",
        "2020-07-03",
        "2020-07-04",
        "2020-07-05",
        "2020-07-06",
        "2020-07-07",
        "2020-07-08",
        "2020-07-09",
        "2020-07-10",
        "2020-07-11",
        "2020-07-12",
        "2020-07-13",
        "2020-07-14",
        "2020-07-15",
        "2020-07-16",
        "2020-07-17",
        "2020-07-18",
        "2020-07-19",
        "2020-07-20",
      ],
      colors: ["#206bc4"],
      legend: {
        show: false,
      },
    },
  };

  const periodOptions = ["Last 7 days", "Last 30 days", "Last 3 months"];

  const [period, setPeriod] = useState(periodOptions[0]);

  const handlePeriodChange = (e) => {
    setPeriod(e.target.text);
    // TODO: Função que ajeita os dados
  };

  return (
    <div className="card mx-10">
      <div className="card-body">
        <div className="d-flex align-items-center">
          <div className="subheader">Revenue</div>
          <div className="ms-auto lh-1">
            <PeriodDropdown
              current={period}
              options={periodOptions}
              handleClick={handlePeriodChange}
            />
          </div>
        </div>
        <div className="d-flex align-items-baseline">
          <div className="h1 mb-0 me-2">$4,300</div>
          <div className="me-auto">
            <TrendingSideways value="8%" />
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
