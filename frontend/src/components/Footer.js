import React from "react";

const Footer = () => {
  return (
    <footer className="footer footer-transparent d-print-none">
      <div className="container-xl">
        <div className="row text-center align-items-center flex-row-reverse justify-center">
          <div className="col-lg-auto">
            <ul className="list-inline list-inline-dots mb-0">
              <li className="list-inline-item">
                <a
                  href="https://github.com/mtrentz/Spotify-Dashboard"
                  target="_blank"
                  className="link-secondary"
                  rel="noopener"
                >
                  Source code
                </a>
              </li>
              <li className="list-inline-item">
                <a
                  href="https://mtrentz.com.br/aboutme"
                  className="link-secondary"
                >
                  About Me
                </a>
              </li>
              <li className="list-inline-item">
                <a href="https://github.com/mtrentz" className="link-secondary">
                  Github
                </a>
              </li>
              <li className="list-inline-item">
                <a
                  href="https://www.linkedin.com/in/mtrentz/"
                  target="_blank"
                  className="link-secondary"
                  rel="noopener"
                >
                  Linkedin
                </a>
              </li>
            </ul>
          </div>
        </div>
        <div className="mt-3 mt-lg-0 flex flex-row justify-center">
          <li className="list-inline-item">
            Website made with{" "}
            <a href="https://tabler.io" className="link-secondary">
              Tabler
            </a>
            .
          </li>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
