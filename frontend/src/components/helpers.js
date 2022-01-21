import TrendingUp from "./Utilities/TrendingUp";
import TrendingDown from "./Utilities/TrendingDown";
import TrendingSideways from "./Utilities/TrendingSideways";

export const generateTrendComponent = (growth) => {
  let percentage = growth * 100;

  // How much it has to change to be considered a trend up or down
  // else it will be sideways.  In %
  let sidewaysThreshold = 0.5;

  let percentageString;

  // If the growth is between -1% and 1% (but not 0.0), I want it to have 1 decimal place.
  // Else it will have none.
  if (percentage >= -1 && percentage <= 1 && percentage !== 0) {
    percentageString = `${percentage.toFixed(1)}%`;
  } else {
    percentageString = `${percentage.toFixed(0)}%`;
  }

  if (percentage > sidewaysThreshold) {
    return <TrendingUp value={percentageString} />;
  } else if (percentage < -sidewaysThreshold) {
    return <TrendingDown value={percentageString} />;
  } else {
    return <TrendingSideways value={percentageString} />;
  }
};
