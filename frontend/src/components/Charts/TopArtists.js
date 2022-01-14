import React from "react";

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
    <div class="card mx-10">
      {/* TODO: Add dropdown */}
      <div class="card-header">
        <h3 class="card-title">Top Played Artists</h3>
      </div>
      <table class="table card-table table-vcenter">
        <thead>
          <tr>
            <th>Artist</th>
            <th colspan="2">Minutes Played</th>
          </tr>
        </thead>
        <tbody>
          {data.map((item, index) => (
            <tr>
              <td>{item.name}</td>
              <td>{item.minutes}</td>
              <td class="w-50">
                <div class="progress progress-xs">
                  <div
                    class="progress-bar bg-primary"
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
