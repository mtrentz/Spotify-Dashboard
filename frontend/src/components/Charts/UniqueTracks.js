import React from "react";
import CardKPI from "../Utilities/CardKPI";
import TrendingUp from "../Utilities/TrendingUp";
import TrendingDown from "../Utilities/TrendingDown";
import TrendingSideways from "../Utilities/TrendingSideways";

const UniqueTracks = () => {
  return (
    <CardKPI
      value="315"
      text="Unique Tracks (week)"
      trend={<TrendingDown value="12%" />}
    />
  );
};

export default UniqueTracks;
