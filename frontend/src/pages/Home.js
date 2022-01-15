import React from "react";
import { useEffect, useContext } from "react";

import ApiContext from "../components/Contexts/ApiContext";

import SampleGraph from "../components/Charts/SampleGraph";
import TimePlayedChart from "../components/Charts/TimePlayedChart";
import UniqueAlbums from "../components/Charts/UniqueAlbums";
import UniqueArtistsKPI from "../components/Charts/UniqueArtistsKPI";
import UniqueTracks from "../components/Charts/UniqueTracks";
import RecentActivity from "../components/Charts/RecentActivity";
import TopArtists from "../components/Charts/TopArtists";
import TopTracks from "../components/Charts/TopTracks";

const Home = () => {
  const { api } = useContext(ApiContext);

  useEffect(() => {
    api
      .get("/recent/")
      .then((res) => {
        console.log("Print from Home.js");
        console.log(res.data);
      })
      .catch((err) => {
        console.log("Print from Home.js");
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
