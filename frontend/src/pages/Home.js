import React from "react";

import TimePlayedChart from "../components/Charts/TimePlayedChart";
import UniqueAlbumsKPI from "../components/Charts/UniqueAlbumsKPI";
import UniqueArtistsKPI from "../components/Charts/UniqueArtistsKPI";
import UniqueTracksKPI from "../components/Charts/UniqueTracksKPI";
import RecentActivity from "../components/Charts/RecentActivity";
import TopArtists from "../components/Charts/TopArtists";
import TopTracks from "../components/Charts/TopTracks";

const Home = () => {
  return (
    <div>
      <TimePlayedChart />
      <UniqueArtistsKPI />
      <UniqueTracksKPI />
      <UniqueAlbumsKPI />
      <TopArtists />
      <TopTracks />
      <RecentActivity />
    </div>
  );
};

export default Home;
