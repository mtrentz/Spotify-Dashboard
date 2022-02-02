import React from "react";

const Footer = () => {
  return (
    <footer className="footer footer-transparent d-print-none">
      <div className="container-xl">
        <div className="row text-center align-items-center flex-row-reverse justify-center">
          <ol
            className="breadcrumb breadcrumb-dots flex flex-row justify-center"
            aria-label="breadcrumbs"
          >
            <li className="breadcrumb-item">
              <a
                href="https://github.com/mtrentz/Spotify-Dashboard"
                target="_blank"
                className="link-secondary"
                rel="noopener"
              >
                Source code
              </a>
            </li>
            <li className="breadcrumb-item">
              <a
                href="https://mtrentz.com.br/aboutme"
                target="_blank"
                className="link-secondary"
                rel="noopener"
              >
                About Me
              </a>
            </li>
            <li className="breadcrumb-item">
              <a
                href="https://github.com/mtrentz"
                target="_blank"
                className="link-secondary"
                rel="noopener"
              >
                Github
              </a>
            </li>
            <li className="breadcrumb-item">
              <a
                href="https://www.linkedin.com/in/mtrentz/"
                target="_blank"
                className="link-secondary"
                rel="noopener"
              >
                Linkedin
              </a>
            </li>
          </ol>
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
