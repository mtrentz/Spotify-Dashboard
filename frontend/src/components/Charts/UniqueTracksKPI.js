import React from "react";
import { useContext, useEffect, useState } from "react";

import ApiContext from "../Contexts/ApiContext";
import { generateTrendIcon } from "../helpers";

import CardKPI from "../Utilities/CardKPI";

const UniqueTracksKPI = () => {
  const { api } = useContext(ApiContext);

  const [uniqueTracksData, setUniqueTracksData] = useState([]);

  useEffect(() => {
    api
      .get("/unique-tracks/", { params: { days: 7 } })
      .then((res) => {
        setUniqueTracksData(res.data);
      })
      .catch((err) => {
        console.log(err);
      });
  }, []);

  return (
    <CardKPI
      value={uniqueTracksData.count}
      text="Unique Tracks (week)"
      trend={generateTrendIcon(uniqueTracksData.growth)}
    />
  );
};

export default UniqueTracksKPI;
