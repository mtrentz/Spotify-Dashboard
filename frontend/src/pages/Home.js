import React from "react";
import { useEffect } from "react";
import SampleGraph from "../components/Charts/SampleGraph";
import TimePlayedChart from "../components/Charts/TimePlayedChart";
import UniqueAlbums from "../components/Charts/UniqueAlbums";
import UniqueArtistsKPI from "../components/Charts/UniqueArtistsKPI";
import UniqueTracks from "../components/Charts/UniqueTracks";
import RecentActivity from "../components/Charts/RecentActivity";
import TopArtists from "../components/Charts/TopArtists";
import TopTracks from "../components/Charts/TopTracks";

const Home = () => {
  const axios = require("axios");

  const instance = axios.create({
    // baseURL: "http://localhost:8000/api/spotify",
    baseURL: "https://jsonplaceholder.typicode.com/",
    timeout: 1000,
  });

  // // console.log(api.get("/recent"));
  // api.get("/recent").then((res) => {
  //   console.log("YOYOYOYO");
  //   console.log(res.data);
  // });

  useEffect(() => {
    instance
      .get("/posts/1")
      .then((res) => {
        console.log("YOYOYOYO");
        console.log(res.data);
      })
      .catch((err) => {
        console.log("sadge");
        console.log(err);
      });
  }, []);

  return (
    <div>
      <SampleGraph />
      <TimePlayedChart />
      <UniqueArtistsKPI />
      <UniqueTracks />
      <UniqueAlbums />
      <TopArtists />
      <TopTracks />
      <RecentActivity />
    </div>
  );
};

export default Home;
