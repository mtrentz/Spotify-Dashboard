import React from "react";
import { useEffect } from "react";
import axios from "axios";

import SampleGraph from "../components/Charts/SampleGraph";
import TimePlayedChart from "../components/Charts/TimePlayedChart";
import UniqueAlbums from "../components/Charts/UniqueAlbums";
import UniqueArtistsKPI from "../components/Charts/UniqueArtistsKPI";
import UniqueTracks from "../components/Charts/UniqueTracks";
import RecentActivity from "../components/Charts/RecentActivity";
import TopArtists from "../components/Charts/TopArtists";
import TopTracks from "../components/Charts/TopTracks";

const api = axios.create({
  baseURL: "http://localhost:8000/api/spotify",
  timeout: 1000,
});

const Home = () => {
  useEffect(() => {
    api
      .get("/recent/")
      .then((res) => {
        console.log(res.data);
      })
      .catch((err) => {
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
