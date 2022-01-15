import React from "react";
import PeriodDropdown from "../Utilities/PeriodDropdown";

const TopTracks = () => {
  const data = [
    {
      name: "Good Enough",
      artists: ["Evanescence"],
      minutes: 435,
      art: "https://i.scdn.co/image/ab67616d000048517b8aabae10ab5bbe7c7f11c5",
    },
    {
      name: "Sweet Sacrifice",
      artists: ["Evanescence"],
      minutes: 328,
      art: "https://i.scdn.co/image/ab67616d000048517b8aabae10ab5bbe7c7f11c5",
    },
    {
      name: "I WANNA BE YOUR SLAVE",
      artists: ["Måneskin"],
      minutes: 300,
      art: "https://i.scdn.co/image/ab67616d000048515aa05015cfa7bd2943c29b21",
    },
  ];

  return (
    <div class="card mx-10">
      <div class="card-header flex justify-between">
        <h3 class="card-title">Top Played Tracks</h3>
        {/* TODO: Adicionar handle click */}
        <PeriodDropdown
          current="Last 7 days"
          options={["Last 7 days", "Last 30 days", "All Time"]}
        />
      </div>
      <div class="list-group card-list-group">
        {data.map((item, index) => (
          <div class="list-group-item">
            <div class="row g-2 align-items-center">
              <div class="col-auto fs-3">{index + 1}</div>
              <div class="col-auto">
                <img
                  src={item.art}
                  class="rounded"
                  alt={item.name}
                  width="40"
                  height="40"
                />
              </div>
              <div class="col">
                {item.name}
                <div class="text-muted">
                  {/* TODO: Preciso separar por virgula */}
                  {item.artists.map((artist) => artist)}
                </div>
              </div>
              <div class="col-auto text-muted">{item.minutes} mins</div>
              <div class="col-auto">
                <a href="#" class="link-secondary">
                  <button class="switch-icon" data-bs-toggle="switch-icon">
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
                  </button>
                </a>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TopTracks;
