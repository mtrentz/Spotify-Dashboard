import React from "react";
import CardKPI from "../Utilities/CardKPI";
import TrendingUp from "../Utilities/TrendingUp";
import TrendingDown from "../Utilities/TrendingDown";
import TrendingSideways from "../Utilities/TrendingSideways";

const UniqueAlbums = () => {
  return (
    <CardKPI
      value="10"
      text="Unique Albums (week)"
      trend={<TrendingSideways value="0%" />}
    />
  );
};

export default UniqueAlbums;
