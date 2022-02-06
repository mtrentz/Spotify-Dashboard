import { useEffect, useState } from "react";

import useAxios from "../../../hooks/useAxios";

import Chart from "react-apexcharts";
import LoadingDots from "../../Utilities/LoadingDots";

const TimePlayedYear = ({ year }) => {
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

  const browserTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

  useEffect(() => {
    axios
      .get("/time-played/", {
        params: {
          year: year,
          timezone: browserTimezone,
          periodicity: "weekly",
        },
      })
      .then((res) => {
        setTimePlayedData(res.data);
        updateGraphStatus(res.data);
        setIsLoading(false);
      })
      .catch((err) => {
        console.log(err);
      });
  }, [year]);

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
          <div className="ms-auto lh-1"></div>
        </div>
        <div className="d-flex align-items-baseline">
          <div className="h1 mb-0 me-2">
            {isLoading
              ? 0
              : (timePlayedData.total_minutes_played / 60).toFixed(0)}
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

export default TimePlayedYear;
