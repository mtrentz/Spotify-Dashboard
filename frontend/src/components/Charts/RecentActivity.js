import React from "react";
import { useContext, useEffect, useState } from "react";
import TimeAgo from "javascript-time-ago";
import en from "javascript-time-ago/locale/en.json";

import ApiContext from "../Contexts/ApiContext";

const RecentActivity = () => {
  // (new Date()).getTimezoneOffset()
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
        albumCover: placeholderAlbum,
      };
    });
    return cleanedData;
  };

  useEffect(() => {
    api
      .get("/recent/", { params: { qty: 25 } })
      .then((res) => {
        setRecentlyPlayedData(cleanApiResponse(res.data));
      })
      .catch((err) => {
        console.log(err);
      });
  }, []);

  // TODO: Quando tiver arte do album de vdd, trocar aqui
  const placeholderAlbum =
    "https://i.scdn.co/image/ab67616d00004851fa0ab3a28b5c52d8a5f97045";

  return (
    <div className="card mx-10" style={{ height: "calc(24rem + 10px)" }}>
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
