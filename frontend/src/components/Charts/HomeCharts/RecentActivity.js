import React from "react";
import { useContext, useEffect, useState } from "react";
import TimeAgo from "javascript-time-ago";
import en from "javascript-time-ago/locale/en.json";

import useAxios from "../../../hooks/useAxios";
import NotificationContext from "../../../contexts/NotificationContext";

const RecentActivity = () => {
  const axios = useAxios();

  const { addNotification } = useContext(NotificationContext);

  const [recentlyPlayedData, setRecentlyPlayedData] = useState([]);
  const [refreshed, setRefreshed] = useState(false);

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

  const refreshRecentActivity = () => {
    axios
      .post("/refresh-recently-played/")
      .then((res) => {
        // Add a alert that the request its being refreshed
        addNotification({
          type: "info",
          msg: "Updating...",
          msg_muted: "Try refreshing the page if nothing happens.",
        });
        // Change state so the other useEffect runs
        // wait few seconds so API has time to update
        setInterval(() => setRefreshed(!refreshed), 3000);
      })
      .catch((err) => {
        console.log(err);
        addNotification({
          type: "danger",
          msg: "Something went wrong!",
          msg_muted:
            "Check if you authorized the app to access your Spotify data.",
        });
      });
  };

  useEffect(() => {
    axios
      .get("/recently-played/", { params: { qty: 25 } })
      .then((res) => {
        setRecentlyPlayedData(cleanApiResponse(res.data));
      })
      .catch((err) => {
        console.log(err);
      });
  }, [refreshed]);

  return (
    <div className="card" style={{ height: "calc(24rem + 10px)" }}>
      <div className="card-header flex justify-between">
        <h3 className="card-title">Your Recent Activity</h3>
        {/* Force activity recheck button */}
        <button onClick={refreshRecentActivity}>
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
                      className="avatar"
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
