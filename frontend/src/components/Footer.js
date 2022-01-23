import React from "react";

const Footer = () => {
  return (
    <footer class="footer footer-transparent d-print-none">
      <div class="container-xl">
        <div class="row text-center align-items-center flex-row-reverse">
          <div class="col-lg-auto ms-lg-auto">
            <ul class="list-inline list-inline-dots mb-0">
              <li class="list-inline-item">
                <a
                  href="https://github.com/mtrentz/Spotify-Dashboard"
                  target="_blank"
                  class="link-secondary"
                  rel="noopener"
                >
                  Source code
                </a>
              </li>
              <li class="list-inline-item">
                <a href="https://mtrentz.com.br/aboutme" class="link-secondary">
                  About Me
                </a>
              </li>
              <li class="list-inline-item">
                <a href="https://github.com/mtrentz" class="link-secondary">
                  Github
                </a>
              </li>
              <li class="list-inline-item">
                <a
                  href="https://www.linkedin.com/in/mtrentz/"
                  target="_blank"
                  class="link-secondary"
                  rel="noopener"
                >
                  Linkedin
                </a>
              </li>
            </ul>
          </div>
        </div>
        <div class="mt-3 mt-lg-0 flex flex-row justify-center">
          <li class="list-inline-item">
            Website made with{" "}
            <a href="https://tabler.io" class="link-secondary">
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
