import React from "react";
import { useContext, useEffect, useState } from "react";

import ApiContext from "../Contexts/ApiContext";
import { generateTrendIcon } from "../helpers";

import CardKPI from "../Utilities/CardKPI";

const UniqueArtistsKPI = () => {
  const { api } = useContext(ApiContext);

  const [uniqueArtistsData, setUniqueArtistsData] = useState([]);

  useEffect(() => {
    api
      .get("/unique-artists/", { params: { days: 7 } })
      .then((res) => {
        setUniqueArtistsData(res.data);
      })
      .catch((err) => {
        console.log(err);
      });
  }, []);

  return (
    <CardKPI
      value={uniqueArtistsData.count}
      text="Unique Artists (week)"
      trend={generateTrendIcon(uniqueArtistsData.growth)}
    />
  );
};

export default UniqueArtistsKPI;
