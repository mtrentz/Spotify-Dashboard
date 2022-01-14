import React from "react";
import CardKPI from "../Utilities/CardKPI";
import TrendingUp from "../Utilities/TrendingUp";
import TrendingDown from "../Utilities/TrendingDown";
import TrendingSideways from "../Utilities/TrendingSideways";

const UniqueArtistsKPI = () => {
  return (
    <CardKPI
      value="43"
      text="Unique Artists (week)"
      trend={<TrendingUp value="5%" />}
    />
  );
};

export default UniqueArtistsKPI;
