import React from "react";
import { useContext, useEffect, useState } from "react";

import useAxios from "../../hooks/useAxios";
import { generateTrendComponent } from "../helpers";

import CardKPI from "../Utilities/CardKPI";

const UniqueTracksKPI = () => {
  const axios = useAxios();

  const [uniqueTracksData, setUniqueTracksData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    axios
      .get("/unique-tracks/", { params: { days: 7 } })
      .then((res) => {
        setUniqueTracksData(res.data);
        setIsLoading(false);
      })
      .catch((err) => {
        console.log(err);
      });
  }, []);

  return (
    <CardKPI
      value={isLoading ? 0 : uniqueTracksData.count}
      text="Unique Tracks (week)"
      trend={generateTrendComponent(isLoading ? 0 : uniqueTracksData.growth)}
    />
  );
};

export default UniqueTracksKPI;
