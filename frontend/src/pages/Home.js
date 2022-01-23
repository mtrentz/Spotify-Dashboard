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
    const code = searchParams.get("code");
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
      <div class="col mx-2 mb-3">
        <div class="page-pretitle">Overview</div>
        <h2 class="page-title">Home Dashboard</h2>
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
