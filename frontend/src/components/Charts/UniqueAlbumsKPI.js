import React from "react";
import { useContext, useEffect, useState } from "react";

import ApiContext from "../Contexts/ApiContext";
import { generateTrendComponent } from "../helpers";

import CardKPI from "../Utilities/CardKPI";

const UniqueAlbumsKPI = () => {
  const { api } = useContext(ApiContext);

  const [uniqueAlbumsData, setUniqueAlbumsData] = useState([]);

  useEffect(() => {
    api
      .get("/unique-albums/", { params: { days: 7 } })
      .then((res) => {
        setUniqueAlbumsData(res.data);
      })
      .catch((err) => {
        console.log(err);
      });
  }, []);

  return (
    <CardKPI
      value={uniqueAlbumsData.count}
      text="Unique Albums (week)"
      trend={generateTrendComponent(uniqueAlbumsData.growth)}
    />
  );
};

export default UniqueAlbumsKPI;
