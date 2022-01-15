import React from "react";
import SampleGraph from "../components/Charts/SampleGraph";
import TimePlayedChart from "../components/Charts/TimePlayedChart";
import UniqueAlbums from "../components/Charts/UniqueAlbums";
import UniqueArtistsKPI from "../components/Charts/UniqueArtistsKPI";
import UniqueTracks from "../components/Charts/UniqueTracks";
import RecentActivity from "../components/Charts/RecentActivity";
import TopArtists from "../components/Charts/TopArtists";
import TopTracks from "../components/Charts/TopTracks";

const Home = () => {
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
