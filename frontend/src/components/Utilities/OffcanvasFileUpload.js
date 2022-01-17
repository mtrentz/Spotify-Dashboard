import React, { useRef, useContext, useEffect, useState } from "react";
import { useForm } from "react-hook-form";

import ApiContext from "../Contexts/ApiContext";

import UploadHistoryButton from "./UploadHistoryButton";

const OffcanvasFileUpload = () => {
  const { api } = useContext(ApiContext);

  const { register, handleSubmit } = useForm();

  const onSubmit = (values) => {
    // console.log("1>", values);
    let formData = new FormData();
    for (const file of values.file) {
      formData.append("file", file);
    }
    api
      .post("/history/", formData)
      .then((res) => {
        console.log(res);
      })
      .catch((err) => {
        console.log(err.response);
      });
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

        <form onSubmit={handleSubmit(onSubmit)}>
          <input
            name="file"
            type="file"
            multiple
            {...register("file", {
              required: "Required",
            })}
          />
          <input type="submit" />
        </form>

        <div className="mt-3">
          <button className="btn" type="button" data-bs-dismiss="offcanvas">
            Close Menu
          </button>
        </div>
      </div>
    </div>
  );
};

export default OffcanvasFileUpload;
