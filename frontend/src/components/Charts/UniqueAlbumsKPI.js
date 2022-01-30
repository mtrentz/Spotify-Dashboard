import React from "react";
import { useContext, useEffect, useState } from "react";

import useAxios from "../../hooks/useAxios";
import { generateTrendComponent } from "../helpers";

import CardKPI from "../Utilities/CardKPI";

const UniqueAlbumsKPI = () => {
  const axios = useAxios();

  const [uniqueAlbumsData, setUniqueAlbumsData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    axios
      .get("/unique-albums/", { params: { days: 7 } })
      .then((res) => {
        setUniqueAlbumsData(res.data);
        setIsLoading(false);
      })
      .catch((err) => {
        console.log(err);
      });
  }, []);

  return (
    <CardKPI
      value={isLoading ? 0 : uniqueAlbumsData.count}
      text="Unique Albums (week)"
      trend={generateTrendComponent(isLoading ? 0 : uniqueAlbumsData.growth)}
    />
  );
};

export default UniqueAlbumsKPI;
