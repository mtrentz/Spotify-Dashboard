import { useEffect, useState } from "react";

import useAxios from "../../../hooks/useAxios";

const TopArtistsYear = ({ year }) => {
  const axios = useAxios();

  const [topArtistsData, setTopArtistsData] = useState([]);

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

  const browserTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

  useEffect(() => {
    axios
      .get("/top-played-artists/", {
        params: { qty: 7, year: year, timezone: browserTimezone },
      })
      .then((res) => {
        setTopArtistsData(processApiResponse(res.data));
      })
      .catch((err) => {
        console.log(err);
      });
  }, [year]);

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="card-title">Top Artists</h3>
      </div>
      <table className="table card-table table-vcenter">
        <thead>
          <tr>
            <th>Artist</th>
            <th colSpan="2">Hours Played</th>
          </tr>
        </thead>
        <tbody>
          {topArtistsData.map((item, index) => (
            <tr key={index} className="h-11">
              <td>{item.artistName}</td>
              <td>{(item.minutesPlayed / 60).toFixed(1)}</td>
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
export default TopArtistsYear;
