import React, { useEffect } from "react";
import { useSearchParams } from "react-router-dom";

import useAxios from "../hooks/useAxios";

import TimePlayedChart from "../components/Charts/TimePlayedChart";
import UniqueAlbumsKPI from "../components/Charts/UniqueAlbumsKPI";
import UniqueArtistsKPI from "../components/Charts/UniqueArtistsKPI";
import UniqueTracksKPI from "../components/Charts/UniqueTracksKPI";
import RecentActivity from "../components/Charts/RecentActivity";
import TopArtists from "../components/Charts/TopArtists";
import TopTracks from "../components/Charts/TopTracks";

const Home = () => {
  const axios = useAxios();
  const [searchParams, setSearchParams] = useSearchParams();

  useEffect(() => {
    // This is for the redirect from the Spotify Login page
    // which sends the code that will be used for oauth on the backend
    const code = searchParams.get("code");
    if (code) {
      axios
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
      <div className="col mx-2 mb-3">
        <div className="page-pretitle">Overview</div>
        <h2 className="page-title">Home Dashboard</h2>
      </div>
      <div className="m-2 flex flex-col gap-2 md:grid md:grid-cols-2 md:grid-flow-row md:auto-rows-min">
        <div className="order-none md:order-1 md:col-span-2">
          <TimePlayedChart />
        </div>
        <div className="order-none md:order-2">
          <UniqueTracksKPI />
        </div>
        <div className="order-none md:order-3">
          <UniqueAlbumsKPI />
        </div>
        <div className="order-none md:order-4">
          <UniqueArtistsKPI />
        </div>
        <div className="order-none md:order-6">
          <TopArtists />
        </div>
        <div className="order-none md:order-5 row-span-2">
          <TopTracks />
        </div>
        <div className="order-none md:order-7 col-span-2">
          <RecentActivity />
        </div>
      </div>
    </div>
  );
};

export default Home;
