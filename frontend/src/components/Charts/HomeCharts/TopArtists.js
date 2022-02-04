import React from "react";
import { useEffect, useState } from "react";

import useAxios from "../../../hooks/useAxios";

import PeriodDropdown from "../../Utilities/PeriodDropdown";

const TopArtists = () => {
  const axios = useAxios();

  const [topArtistsData, setTopArtistsData] = useState([]);

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

  const processApiResponse = (res) => {
    // I'll receive a response containing the artist name and minutes played.
    // From this I need to calculate the percentage of the progress bar.

    // I'll get the biggest value (first) and calculate progress based on it.
    let maxValue = res[0].minutes_played;

    let processedData = res.map((item) => {
      return {
        artistName: item.artist,
        minutesPlayed: item.minutes_played,
        progress: Math.round((item.minutes_played / maxValue) * 100),
      };
    });
    return processedData;
  };

  useEffect(() => {
    axios
      .get("/top-played-artists/", {
        params: { qty: 7, days: periodOptions[period] },
      })
      .then((res) => {
        setTopArtistsData(processApiResponse(res.data));
      })
      .catch((err) => {
        console.log(err);
      });
  }, [period]);

  return (
    <div className="card">
      <div className="card-header flex justify-between">
        <h3 className="card-title">Top Played Artists</h3>
        <PeriodDropdown
          current={period}
          options={Object.keys(periodOptions)}
          handleClick={handlePeriodChange}
        />
      </div>
      <table className="table card-table table-vcenter">
        <thead>
          <tr>
            <th>Artist</th>
            <th colSpan="2">Minutes Played</th>
          </tr>
        </thead>
        <tbody>
          {topArtistsData.map((item, index) => (
            <tr key={index} className="h-11">
              <td>{item.artistName}</td>
              <td>{item.minutesPlayed}</td>
              <td className="w-50">
                <div className="progress progress-xs">
                  <div
                    className="progress-bar bg-primary"
                    style={{ width: `${item.progress}%` }}
                  ></div>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default TopArtists;
