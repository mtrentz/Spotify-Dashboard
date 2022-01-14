import React from "react";
import Chart from "react-apexcharts";

const SampleGraph = () => {
  const status = {
    series: [
      {
        name: "Session Duration",
        data: [117, 92, 94, 98, 75, 110, 69, 80, 109, 113, 115, 95],
      },
      {
        name: "Page Views",
        data: [59, 80, 61, 66, 70, 84, 87, 64, 94, 56, 55, 67],
      },
      {
        name: "Total Visits",
        data: [53, 51, 52, 41, 46, 60, 45, 43, 30, 50, 58, 59],
      },
    ],
    options: {
      chart: {
        type: "line",
        fontFamily: "inherit",
        height: 240,
        parentHeightOffset: 0,
        toolbar: {
          show: false,
        },
        animations: {
          enabled: false,
        },
      },
      fill: {
        opacity: 1,
      },
      stroke: {
        width: 2,
        lineCap: "round",
        curve: "straight",
      },
      grid: {
        padding: {
          top: -20,
          right: 0,
          left: -4,
          bottom: -4,
        },
        strokeDashArray: 4,
      },
      xaxis: {
        labels: {
          padding: 0,
        },
        tooltip: {
          enabled: false,
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
      ],
      colors: ["#fab005", "#5eba00", "#206bc4"],
      legend: {
        show: true,
        position: "bottom",
        offsetY: 12,
        markers: {
          width: 10,
          height: 10,
          radius: 100,
        },
        itemMargin: {
          horizontal: 8,
          vertical: 8,
        },
      },
    },
  };
  return (
    <div className="card mx-10">
      <div className="card-body">
        <Chart
          id="chart-demo-line"
          className="chart-lg"
          series={status.series}
          options={status.options}
        />
      </div>
    </div>
  );
};

export default SampleGraph;
