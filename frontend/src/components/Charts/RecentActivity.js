import React from "react";
import { useContext, useEffect, useState } from "react";
import TimeAgo from "javascript-time-ago";
import en from "javascript-time-ago/locale/en.json";

import ApiContext from "../Contexts/ApiContext";

const RecentActivity = () => {
  const { api } = useContext(ApiContext);

  const [recentlyPlayedData, setRecentlyPlayedData] = useState([]);

  const createTableText = (trackName, artistList) => {
    // Join artists by comma
    let artistsString = artistList.join(", ");

    return (
      <span>
        You've listened to <strong>{trackName}</strong> by{" "}
        <strong>{artistsString}</strong>.
      </span>
    );
  };

  const parseUTCDate = (dateString) => {
    // Date string is in UTC. This automatically uses system/browser timezone.
    return new Date(dateString);
  };

  const createTimeAgoText = (dateString) => {
    // Get a time ago text from the date string. For example (5 mins ago, 1 day ago, etc...)
    const time = parseUTCDate(dateString);
    TimeAgo.addLocale(en);
    const timeAgo = new TimeAgo("en-US");
    return timeAgo.format(time);
  };

  const cleanApiResponse = (res) => {
    const cleanedData = res.map((item) => {
      return {
        text: createTableText(item.track, item.artists),
        timeAgo: createTimeAgoText(item.played_at),
        albumCover: item.album_cover,
      };
    });
    return cleanedData;
  };

  useEffect(() => {
    api
      .get("/recently-played/", { params: { qty: 25 } })
      .then((res) => {
        setRecentlyPlayedData(cleanApiResponse(res.data));
      })
      .catch((err) => {
        console.log(err);
      });
  }, []);

  return (
    <div className="card mx-10" style={{ height: "calc(24rem + 10px)" }}>
      <div class="card-header flex justify-between">
        <h3 class="card-title">Your Recent Activity</h3>
        {/* TODO: Force activity recheck call */}
        <button>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="icon icon-tabler icon-tabler-refresh text-muted"
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
            <path d="M20 11a8.1 8.1 0 0 0 -15.5 -2m-.5 -4v4h4"></path>
            <path d="M4 13a8.1 8.1 0 0 0 15.5 2m.5 4v-4h-4"></path>
          </svg>
        </button>
      </div>
      <div className="card-body card-body-scrollable card-body-scrollable-shadow">
        <div className="divide-y">
          {recentlyPlayedData.map((item, index) => (
            <div key={index}>
              <div className="row">
                <div className="col-auto">
                  <span className="avatar">
                    {" "}
                    <span
                      class="avatar"
                      style={{
                        backgroundImage: `url(${item.albumCover})` || "",
                      }}
                    ></span>
                  </span>
                </div>
                <div className="col">
                  <div className="text-truncate">{item.text}</div>
                  <div className="text-muted">{item.timeAgo}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default RecentActivity;
