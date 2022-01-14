import React from "react";
import SampleGraph from "../components/Charts/SampleGraph";
import TimePlayedChart from "../components/Charts/TimePlayedChart";
import UniqueAlbums from "../components/Charts/UniqueAlbums";
import UniqueArtistsKPI from "../components/Charts/UniqueArtistsKPI";
import UniqueTracks from "../components/Charts/UniqueTracks";
import RecentActivity from "../components/Charts/RecentActivity";

const Home = () => {
  return (
    <div>
      <SampleGraph />
      <TimePlayedChart />
      <UniqueArtistsKPI />
      <UniqueTracks />
      <UniqueAlbums />
      <RecentActivity />
    </div>
  );
};

export default Home;
