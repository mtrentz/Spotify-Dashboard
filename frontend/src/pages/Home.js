import React, { useEffect, useContext } from "react";
import { useSearchParams } from "react-router-dom";

import ApiContext from "../components/Contexts/ApiContext";

import TimePlayedChart from "../components/Charts/TimePlayedChart";
import UniqueAlbumsKPI from "../components/Charts/UniqueAlbumsKPI";
import UniqueArtistsKPI from "../components/Charts/UniqueArtistsKPI";
import UniqueTracksKPI from "../components/Charts/UniqueTracksKPI";
import RecentActivity from "../components/Charts/RecentActivity";
import TopArtists from "../components/Charts/TopArtists";
import TopTracks from "../components/Charts/TopTracks";

const Home = () => {
  const { api } = useContext(ApiContext);
  const [searchParams, setSearchParams] = useSearchParams();

  useEffect(() => {
    let code = searchParams.get("code");
    if (code) {
      api
        .post("/token/", { code: code })
        .then((res) => {
          console.log(res);
        })
        .catch((err) => {
          console.log(err);
        });
    }
  }, []);

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
