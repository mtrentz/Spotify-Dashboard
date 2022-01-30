import React from "react";
import { useContext, useEffect, useState } from "react";

import useAxios from "../../hooks/useAxios";
import { generateTrendComponent } from "../helpers";

import CardKPI from "../Utilities/CardKPI";

const UniqueArtistsKPI = () => {
  const axios = useAxios();

  const [uniqueArtistsData, setUniqueArtistsData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    axios
      .get("/unique-artists/", { params: { days: 7 } })
      .then((res) => {
        setUniqueArtistsData(res.data);
        setIsLoading(false);
      })
      .catch((err) => {
        console.log(err);
      });
  }, []);

  return (
    <CardKPI
      value={isLoading ? 0 : uniqueArtistsData.count}
      text="Unique Artists (week)"
      trend={generateTrendComponent(isLoading ? 0 : uniqueArtistsData.growth)}
    />
  );
};

export default UniqueArtistsKPI;
