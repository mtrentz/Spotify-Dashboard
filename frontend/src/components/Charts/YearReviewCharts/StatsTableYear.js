import React, { useState, useEffect } from "react";

import useAxios from "../../../hooks/useAxios";

const StatsTableYear = ({ year }) => {
  const axios = useAxios();

  const [generalStats, setGeneralStats] = useState({});
  const [uniqueTracks, setUniqueTracks] = useState();
  const [uniqueArtists, setUniqueArtists] = useState();
  const [uniqueAlbums, setUniqueAlbums] = useState();

  const browserTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

  useEffect(() => {
    //  Request Unique Tracks
    axios
      .get("/unique-tracks/", {
        params: { year: year, timezone: browserTimezone },
      })
      .then((res) => {
        setUniqueTracks(res.data.count);
      })
      .catch((err) => {
        console.log(err);
      });

    //  Request Unique Artists
    axios
      .get("/unique-artists/", {
        params: { year: year, timezone: browserTimezone },
      })
      .then((res) => {
        setUniqueArtists(res.data.count);
      })
      .catch((err) => {
        console.log(err);
      });

    //  Request Unique Albums
    axios
      .get("/unique-albums/", {
        params: { year: year, timezone: browserTimezone },
      })
      .then((res) => {
        setUniqueAlbums(res.data.count);
      })
      .catch((err) => {
        console.log(err);
      });

    //  Request General Stats
    axios
      .get("/user-activity-statistics/", {
        params: { year: year, timezone: browserTimezone },
      })
      .then((res) => {
        setGeneralStats(res.data);
        console.log(typeof res.data.total_time_played_in_days);
        console.log(res.data.total_time_played_in_days.toFixed(1));
      })
      .catch((err) => {
        console.log(err);
      });
  }, [year]);

  return (
    <div className="card md:-mt-6 lg:-mt-3 xl:-mt-4 2xl:-mt-5">
      <table className="table table-vcenter card-table">
        <thead>
          <tr>
            <th className="text-nowrap">Your stats</th>
            <th className="text-nowrap">Value</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Time listened</td>
            <td className="text-muted">
              {generalStats.total_time_played_in_days?.toFixed(1) || "0"} days
            </td>
          </tr>
          <tr>
            <td>Avg. per day</td>
            <td className="text-muted">
              {(generalStats.average_minutes_per_day / 24)?.toFixed(1) || "0"}{" "}
              hours
            </td>
          </tr>
          <tr>
            <td>Most active day of week</td>
            <td className="text-muted">
              {generalStats.day_of_week_most_activity || "N/A"}
            </td>
          </tr>
          <tr>
            <td>Most active hour of day</td>
            <td className="text-muted">
              {generalStats.hour_of_day_most_activity || "N/A"}
            </td>
          </tr>
          <tr>
            <td>Unique Tracks</td>
            <td className="text-muted">{uniqueTracks || "N/A"}</td>
          </tr>
          <tr>
            <td>Unique Albums</td>
            <td className="text-muted">{uniqueAlbums || "N/A"}</td>
          </tr>
          <tr>
            <td>Unique Artists</td>
            <td className="text-muted">{uniqueArtists || "N/A"}</td>
          </tr>
        </tbody>
      </table>
    </div>
  );
};

export default StatsTableYear;
