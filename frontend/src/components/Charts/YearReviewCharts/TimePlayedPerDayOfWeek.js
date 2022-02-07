import React from "react";
import { useEffect, useState } from "react";

import useAxios from "../../../hooks/useAxios";

import Chart from "react-apexcharts";
import LoadingDots from "../../Utilities/LoadingDots";

const TimePlayedPerDayOfWeek = ({ year }) => {
  const startingGraphSettings = {
    series: [
      {
        name: "Hours Played",
        // Unpack data into array of hours
        data: [1, 2, 3],
      },
    ],
    options: {
      chart: {
        type: "bar",
        fontFamily: "inherit",
        // height: 240,
        toolbar: {
          show: false,
        },
        animations: {
          enabled: false,
        },
      },
      dataLabels: {
        enabled: false,
      },
      stroke: {
        show: true,
        width: 2,
        opacity: 0.3,
      },
      fill: {
        opacity: 0.55,
        type: "solid",
      },
      grid: {
        strokeDashArray: 4,
        padding: {
          top: -10,
          right: 0,
          left: 0,
          bottom: -10,
        },
      },
      xaxis: {
        type: "category",
        labels: {
          padding: 0,
        },
        tooltip: {
          enabled: false,
        },
        axisBorder: {
          show: false,
        },
        axisTicks: {
          show: false,
        },
      },
      yaxis: {
        labels: {
          padding: 4,
        },
      },
      labels: [
        "2018-09-19T00:00:00.000Z",
        "2018-09-19T01:30:00.000Z",
        "2018-09-19T02:30:00.000Z",
      ],
      colors: ["#206bc4"],
      legend: {
        horizontalAlign: "left",
      },
    },
  };

  const axios = useAxios();

  const [graphSettings, setGraphSettings] = useState(startingGraphSettings);
  const [isLoading, setIsLoading] = useState(true);

  const browserTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

  const updateGraphSettings = (data) => {
    // Make a copy of the previous status
    let netSettings = JSON.parse(JSON.stringify(startingGraphSettings));
    // Change the data points and labels
    netSettings.options.labels = data.map((item) =>
      // This cuts to 'Wed', 'Thu', etc...
      item.day_of_week.slice(0, 3)
    );
    netSettings.series[0].data = data.map((item) =>
      (item.minutes_played / 60).toFixed(0)
    );
    setGraphSettings(netSettings);
  };

  useEffect(() => {
    axios
      .get("/time-played-per-day-of-week/", {
        params: { year: year, timezone: browserTimezone },
      })
      .then((res) => {
        updateGraphSettings(res.data);
        setIsLoading(false);
      })
      .catch((err) => {
        console.log(err);
      });
  }, [year]);

  return (
    <div className="card">
      <div className="card-body">
        <div className="subheader">Most Active Weekdays</div>
        {isLoading ? (
          <LoadingDots />
        ) : (
          <Chart
            id="chart-revenue-bg"
            className="chart-md"
            style={{ minHeight: 240 + "px" }}
            series={graphSettings?.series}
            options={graphSettings?.options}
            type="bar"
            height="240"
          />
        )}
      </div>
    </div>
  );
};

export default TimePlayedPerDayOfWeek;
