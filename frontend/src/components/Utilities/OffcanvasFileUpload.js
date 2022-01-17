import React, { useRef, useContext } from "react";

import ApiContext from "../Contexts/ApiContext";

import UploadHistoryButton from "./UploadHistoryButton";

const OffcanvasFileUpload = () => {
  const { api } = useContext(ApiContext);

  const filesElement = useRef(null);

  const sendFile = () => {
    const formData = new FormData();
    for (const file of filesElement.current.files) {
      formData.append("file", file);
    }
    api
      .post("/history/", {
        data: formData,
      })
      .then((res) => {
        console.log(res);
      })
      .catch((err) => {
        console.log(err.response);
      });
    // console.log(dataForm);
  };

  return (
    <div
      className="offcanvas offcanvas-end"
      tabindex="-1"
      id="offcanvasEnd"
      ariaLabelledby="offcanvasEndLabel"
      style={{ visibility: "hidden" }}
      ariaHidden="true"
    >
      <div className="offcanvas-header">
        <h2 className="offcanvas-title" id="offcanvasEndLabel">
          Uploading your Spotify History
        </h2>
        <button
          type="button"
          className="btn-close text-reset"
          data-bs-dismiss="offcanvas"
          aria-label="Close"
        ></button>
      </div>
      {/* TODO: Lembrar que recem coloquei isso aq */}
      {/* <form> */}
      <div className="offcanvas-body flex flex-col justify-start gap-1">
        <div>
          <p>
            To upload your past listening activity from spotify you first need
            to request it through the official spotify website.
          </p>
          <p>
            You can then upload all <strong>streaming_history.json</strong>{" "}
            files here. Multiple files can be uploaded at once, but be mindful
            that going through one single file can take up to several minutes.
          </p>
        </div>
        <span>1. Select your files</span>
        <input ref={filesElement} type="file" multiple className="ml-3" />
        <UploadHistoryButton handleClick={sendFile} />
        <span>2. Confirm upload</span>
        <div className="ml-3"></div>

        <div className="mt-3">
          <button className="btn" type="button" data-bs-dismiss="offcanvas">
            Close Menu
          </button>
        </div>
      </div>
      {/* </form> */}
    </div>
  );
};

export default OffcanvasFileUpload;
