import React, { useEffect, useState } from "react";

import useAxios from "../../../hooks/useAxios";

const TopAlbumsYear = ({ year }) => {
  const axios = useAxios();

  const [topAlbumsData, setTopAlbumsData] = useState([]);

  const processApiResponse = (res) => {
    let processedData = res.map((item) => {
      return {
        albumName: item.album,
        albumCover: item.album_cover,
        artistsNames: item.artists,
        minutesPlayed: item.minutes_played,
      };
    });
    return processedData;
  };

  const browserTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

  useEffect(() => {
    axios
      .get("/top-played-albums/", {
        params: { qty: 7, year: year, timezone: browserTimezone },
      })
      .then((res) => {
        setTopAlbumsData(processApiResponse(res.data));
        console.log(res.data);
      })
      .catch((err) => {
        console.log(err);
        console.log(err.response.data);
      });
  }, [year]);

  return (
    <div className="col-lg-4">
      <h3 className="mb-3">Top Albums</h3>
      <div className="row row-cards">
        {topAlbumsData.map((item, index) => {
          return (
            <div className="col-md-6 col-lg-12" key={index}>
              <div className="card">
                <div className="row row-0 ">
                  <div className="col-auto">
                    <img
                      src={item.albumCover}
                      className="rounded-start"
                      alt={item.albumName}
                      width="80"
                      height="80"
                    />
                  </div>
                  <div className="col">
                    <div className="card-body">
                      {item.albumName}
                      <div className="text-muted">
                        {item.artistsNames.join(", ")}
                      </div>
                    </div>
                  </div>
                  <div className="col-auto">
                    {/* Center text */}
                    <div className="card-body h-full flex flex-col justify-center">
                      <medium className="text-muted h-3">
                        {(item.minutesPlayed / 60).toFixed(1)} hours
                      </medium>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default TopAlbumsYear;
