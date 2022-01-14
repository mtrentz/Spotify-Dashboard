import React from "react";

const TimePlayedChart = () => {
  return (
    <div className="card">
      <div className="card-body">
        <div className="d-flex align-items-center">
          <div className="subheader">Revenue</div>
          <div className="ms-auto lh-1">
            <div className="dropdown">
              <a
                className="dropdown-toggle text-muted"
                href="#"
                data-bs-toggle="dropdown"
                aria-haspopup="true"
                aria-expanded="false"
              >
                Last 7 days
              </a>
              <div className="dropdown-menu dropdown-menu-end">
                <a className="dropdown-item active" href="#">
                  Last 7 days
                </a>
                <a className="dropdown-item" href="#">
                  Last 30 days
                </a>
                <a className="dropdown-item" href="#">
                  Last 3 months
                </a>
              </div>
            </div>
          </div>
        </div>
        <div className="d-flex align-items-baseline">
          <div className="h1 mb-0 me-2">$4,300</div>
          <div className="me-auto">
            <span className="text-green d-inline-flex align-items-center lh-1">
              8%
              {/* <!-- Download SVG icon from http://tabler-icons.io/i/trending-up --> */}
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="icon ms-1"
                width="24"
                height="24"
                viewBox="0 0 24 24"
                strokeWidth="2"
                stroke="currentColor"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
                <polyline points="3 17 9 11 13 15 21 7"></polyline>
                <polyline points="14 7 21 7 21 14"></polyline>
              </svg>
            </span>
          </div>
        </div>
      </div>
      <div
        id="chart-revenue-bg"
        className="chart-sm"
        style={{ minHeight: 40 + "px" }}
      >
        <div
          id="apexchartsamdn6jk"
          className="apexcharts-canvas apexchartsamdn6jk apexcharts-theme-light"
          style={{ width: 234 + "px", height: 40 + "px" }}
        >
          {/* TODO: PArei aqui */}
          <svg
            id="SvgjsSvg2352"
            width="234"
            height="40"
            xmlns="http://www.w3.org/2000/svg"
            version="1.1"
            // xmlns:xlink="http://www.w3.org/1999/xlink"
            // xmlns:svgjs="http://svgjs.dev"
            className="apexcharts-svg"
            // xmlns:data="ApexChartsNS"
            transform="translate(0, 0)"
            style="background: transparent;"
          >
            <g
              id="SvgjsG2354"
              className="apexcharts-inner apexcharts-graphical"
              transform="translate(0, 0)"
            >
              <defs id="SvgjsDefs2353">
                <clipPath id="gridRectMaskamdn6jk">
                  <rect
                    id="SvgjsRect2390"
                    width="240"
                    height="42"
                    x="-3"
                    y="-1"
                    rx="0"
                    ry="0"
                    opacity="1"
                    strokeWidth="0"
                    stroke="none"
                    strokeDasharray="0"
                    fill="#fff"
                  ></rect>
                </clipPath>
                <clipPath id="forecastMaskamdn6jk"></clipPath>
                <clipPath id="nonForecastMaskamdn6jk"></clipPath>
                <clipPath id="gridRectMarkerMaskamdn6jk">
                  <rect
                    id="SvgjsRect2391"
                    width="238"
                    height="44"
                    x="-2"
                    y="-2"
                    rx="0"
                    ry="0"
                    opacity="1"
                    strokeWidth="0"
                    stroke="none"
                    strokeDasharray="0"
                    fill="#fff"
                  ></rect>
                </clipPath>
              </defs>
              <line
                id="SvgjsLine2359"
                x1="0"
                y1="0"
                x2="0"
                y2="40"
                stroke="#b6b6b6"
                strokeDasharray="3"
                strokeLinecap="butt"
                className="apexcharts-xcrosshairs"
                x="0"
                y="0"
                width="1"
                height="40"
                fill="#b1b9c4"
                filter="none"
                fillOpacity="0.9"
                strokeWidth="1"
              ></line>
              <g
                id="SvgjsG2398"
                className="apexcharts-xaxis"
                transform="translate(0, 0)"
              >
                <g
                  id="SvgjsG2399"
                  className="apexcharts-xaxis-texts-g"
                  transform="translate(0, -4)"
                ></g>
              </g>
              <g id="SvgjsG2406" className="apexcharts-grid">
                <g
                  id="SvgjsG2407"
                  className="apexcharts-gridlines-horizontal"
                  style="display: none;"
                >
                  <line
                    id="SvgjsLine2409"
                    x1="0"
                    y1="0"
                    x2="234"
                    y2="0"
                    stroke="#e0e0e0"
                    strokeDasharray="4"
                    strokeLinecap="butt"
                    className="apexcharts-gridline"
                  ></line>
                  <line
                    id="SvgjsLine2410"
                    x1="0"
                    y1="8"
                    x2="234"
                    y2="8"
                    stroke="#e0e0e0"
                    strokeDasharray="4"
                    strokeLinecap="butt"
                    className="apexcharts-gridline"
                  ></line>
                  <line
                    id="SvgjsLine2411"
                    x1="0"
                    y1="16"
                    x2="234"
                    y2="16"
                    stroke="#e0e0e0"
                    strokeDasharray="4"
                    strokeLinecap="butt"
                    className="apexcharts-gridline"
                  ></line>
                  <line
                    id="SvgjsLine2412"
                    x1="0"
                    y1="24"
                    x2="234"
                    y2="24"
                    stroke="#e0e0e0"
                    strokeDasharray="4"
                    strokeLinecap="butt"
                    className="apexcharts-gridline"
                  ></line>
                  <line
                    id="SvgjsLine2413"
                    x1="0"
                    y1="32"
                    x2="234"
                    y2="32"
                    stroke="#e0e0e0"
                    strokeDasharray="4"
                    strokeLinecap="butt"
                    className="apexcharts-gridline"
                  ></line>
                  <line
                    id="SvgjsLine2414"
                    x1="0"
                    y1="40"
                    x2="234"
                    y2="40"
                    stroke="#e0e0e0"
                    strokeDasharray="4"
                    strokeLinecap="butt"
                    className="apexcharts-gridline"
                  ></line>
                </g>
                <g
                  id="SvgjsG2408"
                  className="apexcharts-gridlines-vertical"
                  style="display: none;"
                ></g>
                <line
                  id="SvgjsLine2416"
                  x1="0"
                  y1="40"
                  x2="234"
                  y2="40"
                  stroke="transparent"
                  strokeDasharray="0"
                  strokeLinecap="butt"
                ></line>
                <line
                  id="SvgjsLine2415"
                  x1="0"
                  y1="1"
                  x2="0"
                  y2="40"
                  stroke="transparent"
                  strokeDasharray="0"
                  strokeLinecap="butt"
                ></line>
              </g>
              <g
                id="SvgjsG2392"
                className="apexcharts-area-series apexcharts-plot-series"
              >
                <g
                  id="SvgjsG2393"
                  className="apexcharts-series"
                  seriesName="Profits"
                  // data:longestSeries="true"
                  rel="1"
                  // data:realIndex="0"
                >
                  <path
                    id="SvgjsPath2396"
                    d="M 0 40L 0 25.2C 2.8241379310344823 25.2 5.244827586206897 26 8.068965517241379 26C 10.89310344827586 26 13.313793103448276 22.4 16.137931034482758 22.4C 18.96206896551724 22.4 21.382758620689657 28.8 24.20689655172414 28.8C 27.03103448275862 28.8 29.451724137931034 25.6 32.275862068965516 25.6C 35.1 25.6 37.52068965517241 30.4 40.3448275862069 30.4C 43.16896551724138 30.4 45.58965517241379 14 48.41379310344828 14C 51.237931034482756 14 53.65862068965517 27.6 56.48275862068965 27.6C 59.30689655172414 27.6 61.72758620689655 25.2 64.55172413793103 25.2C 67.37586206896552 25.2 69.79655172413793 24.4 72.62068965517241 24.4C 75.4448275862069 24.4 77.86551724137931 15.2 80.6896551724138 15.2C 83.51379310344828 15.2 85.93448275862069 19.6 88.75862068965517 19.6C 91.58275862068966 19.6 94.00344827586207 26 96.82758620689656 26C 99.65172413793104 26 102.07241379310344 23.6 104.89655172413792 23.6C 107.72068965517241 23.6 110.14137931034482 26 112.9655172413793 26C 115.78965517241379 26 118.2103448275862 29.2 121.03448275862068 29.2C 123.85862068965517 29.2 126.27931034482758 2.799999999999997 129.10344827586206 2.799999999999997C 131.92758620689654 2.799999999999997 134.34827586206896 18.8 137.17241379310343 18.8C 139.99655172413793 18.8 142.41724137931033 15.600000000000001 145.24137931034483 15.600000000000001C 148.0655172413793 15.600000000000001 150.48620689655172 29.2 153.3103448275862 29.2C 156.1344827586207 29.2 158.5551724137931 18.4 161.3793103448276 18.4C 164.20344827586206 18.4 166.62413793103448 22.8 169.44827586206895 22.8C 172.27241379310345 22.8 174.69310344827585 32.4 177.51724137931035 32.4C 180.34137931034482 32.4 182.76206896551724 21.6 185.58620689655172 21.6C 188.41034482758621 21.6 190.8310344827586 24.4 193.6551724137931 24.4C 196.47931034482758 24.4 198.9 15.2 201.72413793103448 15.2C 204.54827586206895 15.2 206.96896551724137 19.6 209.79310344827584 19.6C 212.61724137931034 19.6 215.03793103448274 26 217.86206896551724 26C 220.6862068965517 26 223.10689655172413 23.6 225.9310344827586 23.6C 228.7551724137931 23.6 231.1758620689655 13.2 234 13.2C 234 13.2 234 13.2 234 40M 234 13.2z"
                    fill="rgba(32,107,196,0.16)"
                    fillOpacity="1"
                    strokeOpacity="1"
                    strokeLinecap="round"
                    strokeWidth="0"
                    strokeDasharray="0"
                    className="apexcharts-area"
                    index="0"
                    clipPath="url(#gridRectMaskamdn6jk)"
                    pathTo="M 0 40L 0 25.2C 2.8241379310344823 25.2 5.244827586206897 26 8.068965517241379 26C 10.89310344827586 26 13.313793103448276 22.4 16.137931034482758 22.4C 18.96206896551724 22.4 21.382758620689657 28.8 24.20689655172414 28.8C 27.03103448275862 28.8 29.451724137931034 25.6 32.275862068965516 25.6C 35.1 25.6 37.52068965517241 30.4 40.3448275862069 30.4C 43.16896551724138 30.4 45.58965517241379 14 48.41379310344828 14C 51.237931034482756 14 53.65862068965517 27.6 56.48275862068965 27.6C 59.30689655172414 27.6 61.72758620689655 25.2 64.55172413793103 25.2C 67.37586206896552 25.2 69.79655172413793 24.4 72.62068965517241 24.4C 75.4448275862069 24.4 77.86551724137931 15.2 80.6896551724138 15.2C 83.51379310344828 15.2 85.93448275862069 19.6 88.75862068965517 19.6C 91.58275862068966 19.6 94.00344827586207 26 96.82758620689656 26C 99.65172413793104 26 102.07241379310344 23.6 104.89655172413792 23.6C 107.72068965517241 23.6 110.14137931034482 26 112.9655172413793 26C 115.78965517241379 26 118.2103448275862 29.2 121.03448275862068 29.2C 123.85862068965517 29.2 126.27931034482758 2.799999999999997 129.10344827586206 2.799999999999997C 131.92758620689654 2.799999999999997 134.34827586206896 18.8 137.17241379310343 18.8C 139.99655172413793 18.8 142.41724137931033 15.600000000000001 145.24137931034483 15.600000000000001C 148.0655172413793 15.600000000000001 150.48620689655172 29.2 153.3103448275862 29.2C 156.1344827586207 29.2 158.5551724137931 18.4 161.3793103448276 18.4C 164.20344827586206 18.4 166.62413793103448 22.8 169.44827586206895 22.8C 172.27241379310345 22.8 174.69310344827585 32.4 177.51724137931035 32.4C 180.34137931034482 32.4 182.76206896551724 21.6 185.58620689655172 21.6C 188.41034482758621 21.6 190.8310344827586 24.4 193.6551724137931 24.4C 196.47931034482758 24.4 198.9 15.2 201.72413793103448 15.2C 204.54827586206895 15.2 206.96896551724137 19.6 209.79310344827584 19.6C 212.61724137931034 19.6 215.03793103448274 26 217.86206896551724 26C 220.6862068965517 26 223.10689655172413 23.6 225.9310344827586 23.6C 228.7551724137931 23.6 231.1758620689655 13.2 234 13.2C 234 13.2 234 13.2 234 40M 234 13.2z"
                    pathFrom="M -1 40L -1 40L 8.068965517241379 40L 16.137931034482758 40L 24.20689655172414 40L 32.275862068965516 40L 40.3448275862069 40L 48.41379310344828 40L 56.48275862068965 40L 64.55172413793103 40L 72.62068965517241 40L 80.6896551724138 40L 88.75862068965517 40L 96.82758620689656 40L 104.89655172413792 40L 112.9655172413793 40L 121.03448275862068 40L 129.10344827586206 40L 137.17241379310343 40L 145.24137931034483 40L 153.3103448275862 40L 161.3793103448276 40L 169.44827586206895 40L 177.51724137931035 40L 185.58620689655172 40L 193.6551724137931 40L 201.72413793103448 40L 209.79310344827584 40L 217.86206896551724 40L 225.9310344827586 40L 234 40"
                  ></path>
                  <path
                    id="SvgjsPath2397"
                    d="M 0 25.2C 2.8241379310344823 25.2 5.244827586206897 26 8.068965517241379 26C 10.89310344827586 26 13.313793103448276 22.4 16.137931034482758 22.4C 18.96206896551724 22.4 21.382758620689657 28.8 24.20689655172414 28.8C 27.03103448275862 28.8 29.451724137931034 25.6 32.275862068965516 25.6C 35.1 25.6 37.52068965517241 30.4 40.3448275862069 30.4C 43.16896551724138 30.4 45.58965517241379 14 48.41379310344828 14C 51.237931034482756 14 53.65862068965517 27.6 56.48275862068965 27.6C 59.30689655172414 27.6 61.72758620689655 25.2 64.55172413793103 25.2C 67.37586206896552 25.2 69.79655172413793 24.4 72.62068965517241 24.4C 75.4448275862069 24.4 77.86551724137931 15.2 80.6896551724138 15.2C 83.51379310344828 15.2 85.93448275862069 19.6 88.75862068965517 19.6C 91.58275862068966 19.6 94.00344827586207 26 96.82758620689656 26C 99.65172413793104 26 102.07241379310344 23.6 104.89655172413792 23.6C 107.72068965517241 23.6 110.14137931034482 26 112.9655172413793 26C 115.78965517241379 26 118.2103448275862 29.2 121.03448275862068 29.2C 123.85862068965517 29.2 126.27931034482758 2.799999999999997 129.10344827586206 2.799999999999997C 131.92758620689654 2.799999999999997 134.34827586206896 18.8 137.17241379310343 18.8C 139.99655172413793 18.8 142.41724137931033 15.600000000000001 145.24137931034483 15.600000000000001C 148.0655172413793 15.600000000000001 150.48620689655172 29.2 153.3103448275862 29.2C 156.1344827586207 29.2 158.5551724137931 18.4 161.3793103448276 18.4C 164.20344827586206 18.4 166.62413793103448 22.8 169.44827586206895 22.8C 172.27241379310345 22.8 174.69310344827585 32.4 177.51724137931035 32.4C 180.34137931034482 32.4 182.76206896551724 21.6 185.58620689655172 21.6C 188.41034482758621 21.6 190.8310344827586 24.4 193.6551724137931 24.4C 196.47931034482758 24.4 198.9 15.2 201.72413793103448 15.2C 204.54827586206895 15.2 206.96896551724137 19.6 209.79310344827584 19.6C 212.61724137931034 19.6 215.03793103448274 26 217.86206896551724 26C 220.6862068965517 26 223.10689655172413 23.6 225.9310344827586 23.6C 228.7551724137931 23.6 231.1758620689655 13.2 234 13.2"
                    fill="none"
                    fillOpacity="1"
                    stroke="#206bc4"
                    strokeOpacity="1"
                    strokeLinecap="round"
                    strokeWidth="2"
                    strokeDasharray="0"
                    className="apexcharts-area"
                    index="0"
                    clipPath="url(#gridRectMaskamdn6jk)"
                    pathTo="M 0 25.2C 2.8241379310344823 25.2 5.244827586206897 26 8.068965517241379 26C 10.89310344827586 26 13.313793103448276 22.4 16.137931034482758 22.4C 18.96206896551724 22.4 21.382758620689657 28.8 24.20689655172414 28.8C 27.03103448275862 28.8 29.451724137931034 25.6 32.275862068965516 25.6C 35.1 25.6 37.52068965517241 30.4 40.3448275862069 30.4C 43.16896551724138 30.4 45.58965517241379 14 48.41379310344828 14C 51.237931034482756 14 53.65862068965517 27.6 56.48275862068965 27.6C 59.30689655172414 27.6 61.72758620689655 25.2 64.55172413793103 25.2C 67.37586206896552 25.2 69.79655172413793 24.4 72.62068965517241 24.4C 75.4448275862069 24.4 77.86551724137931 15.2 80.6896551724138 15.2C 83.51379310344828 15.2 85.93448275862069 19.6 88.75862068965517 19.6C 91.58275862068966 19.6 94.00344827586207 26 96.82758620689656 26C 99.65172413793104 26 102.07241379310344 23.6 104.89655172413792 23.6C 107.72068965517241 23.6 110.14137931034482 26 112.9655172413793 26C 115.78965517241379 26 118.2103448275862 29.2 121.03448275862068 29.2C 123.85862068965517 29.2 126.27931034482758 2.799999999999997 129.10344827586206 2.799999999999997C 131.92758620689654 2.799999999999997 134.34827586206896 18.8 137.17241379310343 18.8C 139.99655172413793 18.8 142.41724137931033 15.600000000000001 145.24137931034483 15.600000000000001C 148.0655172413793 15.600000000000001 150.48620689655172 29.2 153.3103448275862 29.2C 156.1344827586207 29.2 158.5551724137931 18.4 161.3793103448276 18.4C 164.20344827586206 18.4 166.62413793103448 22.8 169.44827586206895 22.8C 172.27241379310345 22.8 174.69310344827585 32.4 177.51724137931035 32.4C 180.34137931034482 32.4 182.76206896551724 21.6 185.58620689655172 21.6C 188.41034482758621 21.6 190.8310344827586 24.4 193.6551724137931 24.4C 196.47931034482758 24.4 198.9 15.2 201.72413793103448 15.2C 204.54827586206895 15.2 206.96896551724137 19.6 209.79310344827584 19.6C 212.61724137931034 19.6 215.03793103448274 26 217.86206896551724 26C 220.6862068965517 26 223.10689655172413 23.6 225.9310344827586 23.6C 228.7551724137931 23.6 231.1758620689655 13.2 234 13.2"
                    pathFrom="M -1 40L -1 40L 8.068965517241379 40L 16.137931034482758 40L 24.20689655172414 40L 32.275862068965516 40L 40.3448275862069 40L 48.41379310344828 40L 56.48275862068965 40L 64.55172413793103 40L 72.62068965517241 40L 80.6896551724138 40L 88.75862068965517 40L 96.82758620689656 40L 104.89655172413792 40L 112.9655172413793 40L 121.03448275862068 40L 129.10344827586206 40L 137.17241379310343 40L 145.24137931034483 40L 153.3103448275862 40L 161.3793103448276 40L 169.44827586206895 40L 177.51724137931035 40L 185.58620689655172 40L 193.6551724137931 40L 201.72413793103448 40L 209.79310344827584 40L 217.86206896551724 40L 225.9310344827586 40L 234 40"
                  ></path>
                  <g
                    id="SvgjsG2394"
                    className="apexcharts-series-markers-wrap"
                    // data:realIndex="0"
                  >
                    <g className="apexcharts-series-markers">
                      <circle
                        id="SvgjsCircle2422"
                        r="0"
                        cx="0"
                        cy="0"
                        className="apexcharts-marker w27yzyxfsj no-pointer-events"
                        stroke="#ffffff"
                        fill="#206bc4"
                        fillOpacity="1"
                        strokeWidth="2"
                        strokeOpacity="0.9"
                        default-marker-size="0"
                      ></circle>
                    </g>
                  </g>
                </g>
                <g
                  id="SvgjsG2395"
                  className="apexcharts-datalabels"
                  // data:realIndex="0"
                ></g>
              </g>
              <line
                id="SvgjsLine2417"
                x1="0"
                y1="0"
                x2="234"
                y2="0"
                stroke="#b6b6b6"
                strokeDasharray="0"
                strokeWidth="1"
                strokeLinecap="butt"
                className="apexcharts-ycrosshairs"
              ></line>
              <line
                id="SvgjsLine2418"
                x1="0"
                y1="0"
                x2="234"
                y2="0"
                strokeDasharray="0"
                strokeWidth="0"
                strokeLinecap="butt"
                className="apexcharts-ycrosshairs-hidden"
              ></line>
              <g id="SvgjsG2419" className="apexcharts-yaxis-annotations"></g>
              <g id="SvgjsG2420" className="apexcharts-xaxis-annotations"></g>
              <g id="SvgjsG2421" className="apexcharts-point-annotations"></g>
            </g>
            <rect
              id="SvgjsRect2358"
              width="0"
              height="0"
              x="0"
              y="0"
              rx="0"
              ry="0"
              opacity="1"
              strokeWidth="0"
              stroke="none"
              strokeDasharray="0"
              fill="#fefefe"
            ></rect>
            <g
              id="SvgjsG2405"
              className="apexcharts-yaxis"
              rel="0"
              transform="translate(-18, 0)"
            ></g>
            <g id="SvgjsG2355" className="apexcharts-annotations"></g>
          </svg>
          <div className="apexcharts-legend" style="max-height: 20px;"></div>
          <div className="apexcharts-tooltip apexcharts-theme-light">
            <div
              className="apexcharts-tooltip-title"
              style="font-family: inherit; font-size: 12px;"
            ></div>
            <div className="apexcharts-tooltip-series-group" style="order: 1;">
              <span
                className="apexcharts-tooltip-marker"
                style="background-color: rgb(32, 107, 196);"
              ></span>
              <div
                className="apexcharts-tooltip-text"
                style="font-family: inherit; font-size: 12px;"
              >
                <div className="apexcharts-tooltip-y-group">
                  <span className="apexcharts-tooltip-text-y-label"></span>
                  <span className="apexcharts-tooltip-text-y-value"></span>
                </div>
                <div className="apexcharts-tooltip-goals-group">
                  <span className="apexcharts-tooltip-text-goals-label"></span>
                  <span className="apexcharts-tooltip-text-goals-value"></span>
                </div>
                <div className="apexcharts-tooltip-z-group">
                  <span className="apexcharts-tooltip-text-z-label"></span>
                  <span className="apexcharts-tooltip-text-z-value"></span>
                </div>
              </div>
            </div>
          </div>
          <div className="apexcharts-yaxistooltip apexcharts-yaxistooltip-0 apexcharts-yaxistooltip-left apexcharts-theme-light">
            <div className="apexcharts-yaxistooltip-text"></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TimePlayedChart;
