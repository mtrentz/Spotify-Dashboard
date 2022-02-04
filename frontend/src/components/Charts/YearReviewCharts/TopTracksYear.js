import React from "react";

import { useEffect, useState } from "react";

import useAxios from "../../../hooks/useAxios";

const TopTracksYear = ({ year }) => {
  const axios = useAxios();

  const [topTracksData, setTopTracksData] = useState([]);

  const cleanApiResponse = (res) => {
    const cleanedData = res.map((item) => {
      return {
        trackName: item.track,
        artistsString: item.artists.join(", "),
        minutesPlayed: item.minutes_played,
        albumCover: item.album_cover,
      };
    });
    return cleanedData;
  };

  const browserTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

  useEffect(() => {
    axios
      .get("/top-played-tracks/", {
        params: { qty: 7, year: year, timezone: browserTimezone },
      })
      .then((res) => {
        setTopTracksData(cleanApiResponse(res.data));
      })
      .catch((err) => {
        console.log(err);
      });
  }, [year]);

  return (
    <div className="card">
      <div className="card-header flex justify-between">
        <h3 className="card-title">Top Tracks</h3>
      </div>
      <div className="list-group card-list-group">
        {topTracksData.map((item, index) => (
          <div className="list-group-item" key={index}>
            <div className="row g-2 align-items-center">
              <div className="col-auto fs-3">{index + 1}</div>
              <div className="col-auto">
                <img
                  src={item.albumCover}
                  className="rounded"
                  alt={item.trackName}
                  width="40"
                  height="40"
                />
              </div>
              <div className="col">
                {item.trackName}
                <div className="text-muted">{item.artistsString}</div>
              </div>
              <div className="col-auto text-muted">
                {(item.minutesPlayed / 60).toFixed(1)} hours
              </div>
              <div className="col-auto">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="icon icon-tabler icon-tabler-clock"
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  strokeWidth="2"
                  stroke="currentColor"
                  fill="none"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
                  <circle cx="12" cy="12" r="9"></circle>
                  <polyline points="12 7 12 12 15 15"></polyline>
                </svg>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TopTracksYear;
