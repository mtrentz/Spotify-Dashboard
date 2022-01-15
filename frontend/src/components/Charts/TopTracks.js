import React from "react";
import { useContext, useEffect, useState } from "react";

import ApiContext from "../Contexts/ApiContext";

import PeriodDropdown from "../Utilities/PeriodDropdown";

const TopTracks = () => {
  const { api } = useContext(ApiContext);

  const placeholderAlbum =
    "https://i.scdn.co/image/ab67616d00004851fa0ab3a28b5c52d8a5f97045";

  const [topTracksData, setTopTracksData] = useState([]);

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

  const cleanApiResponse = (res) => {
    const cleanedData = res.map((item) => {
      return {
        trackName: item.track,
        artistsString: item.artists.join(", "),
        minutesPlayed: item.minutes_played,
        albumCover: placeholderAlbum,
      };
    });
    return cleanedData;
  };

  useEffect(() => {
    api
      .get("/top-played-tracks/", {
        params: { qty: 5, days: periodOptions[period] },
      })
      .then((res) => {
        setTopTracksData(cleanApiResponse(res.data));
      })
      .catch((err) => {
        console.log(err);
      });
  }, [period]);

  return (
    <div class="card mx-10">
      <div class="card-header flex justify-between">
        <h3 class="card-title">Top Played Tracks</h3>
        <PeriodDropdown
          current={period}
          options={Object.keys(periodOptions)}
          handleClick={handlePeriodChange}
        />
      </div>
      <div class="list-group card-list-group">
        {topTracksData.map((item, index) => (
          <div class="list-group-item" key={index}>
            <div class="row g-2 align-items-center">
              <div class="col-auto fs-3">{index + 1}</div>
              <div class="col-auto">
                <img
                  src={item.albumCover}
                  class="rounded"
                  alt={item.trackName}
                  width="40"
                  height="40"
                />
              </div>
              <div class="col">
                {item.trackName}
                <div class="text-muted">{item.artistsString}</div>
              </div>
              <div class="col-auto text-muted">{item.minutesPlayed} mins</div>
              <div class="col-auto">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="icon icon-tabler icon-tabler-clock"
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  stroke-width="2"
                  stroke="currentColor"
                  fill="none"
                  stroke-linecap="round"
                  stroke-linejoin="round"
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

export default TopTracks;
