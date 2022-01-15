import React from "react";
import PeriodDropdown from "../Utilities/PeriodDropdown";

const TopArtists = () => {
  // This gonna need some logic to get the progress
  //  I have to get the top progress, round by a even number up.
  //  Then base everything on that
  const data = [
    {
      name: "Måneskin",
      minutes: 320,
      progress: "81.0%",
    },
    {
      name: "Led Zeppelin",
      minutes: 249,
      progress: "73.0%",
    },
    {
      name: "Pink Floyd",
      minutes: 150,
      progress: "51.0%",
    },
    {
      name: "Linkin Park",
      minutes: 120,
      progress: "40.0%",
    },
    {
      name: "Sabotage",
      minutes: 89,
      progress: "27.5%",
    },
    {
      name: "Eagles",
      minutes: 43,
      progress: "11.0%",
    },
    {
      name: "Audioslave",
      minutes: 21,
      progress: "5.0%",
    },
  ];

  return (
    <div className="card mx-10">
      {/* TODO: Add dropdown */}
      <div className="card-header flex justify-between">
        <h3 className="card-title">Top Played Artists</h3>
        {/* TODO: Adicionar handle click */}
        <PeriodDropdown
          current="Last 7 days"
          options={["Last 7 days", "Last 30 days", "All Time"]}
        />
      </div>
      <table className="table card-table table-vcenter">
        <thead>
          <tr>
            <th>Artist</th>
            <th colspan="2">Minutes Played</th>
          </tr>
        </thead>
        <tbody>
          {data.map((item, index) => (
            <tr key={index}>
              <td>{item.name}</td>
              <td>{item.minutes}</td>
              <td className="w-50">
                <div className="progress progress-xs">
                  <div
                    className="progress-bar bg-primary"
                    style={{ width: item.progress }}
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
