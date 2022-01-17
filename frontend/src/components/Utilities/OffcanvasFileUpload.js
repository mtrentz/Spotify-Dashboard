import React, { useRef, useContext, useEffect, useState } from "react";
import { useForm } from "react-hook-form";

import ApiContext from "../Contexts/ApiContext";

import UploadHistoryButton from "./UploadHistoryButton";

const OffcanvasFileUpload = () => {
  const { api } = useContext(ApiContext);

  const { register, handleSubmit, getValues } = useForm();
  const [fileCount, setFileCount] = useState(0);

  const handleFileSelect = (e) => {
    const files = getValues("file");
    setFileCount(files.length);
  };

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
        <div className="markdown">
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

        <form
          onSubmit={handleSubmit(onSubmit)}
          className="flex flex-col gap-3 justify-start items-center mt-3"
        >
          <div className="flex flex-row align-center">
            <label
              htmlFor="file"
              className="btn w-32 h-8"
              onChange={handleFileSelect}
            >
              Choose Files
              <input
                id="file"
                name="file"
                type="file"
                multiple
                hidden
                {...register("file", {
                  required: "Required",
                })}
              />
            </label>
            {fileCount > 0 ? (
              <p className="mt-2 ml-2">{fileCount} selected</p>
            ) : null}
          </div>
          <button type="submit" className="btn btn-primary w-32 h-8 font-bold">
            Submit
          </button>
        </form>
      </div>
    </div>
  );
};

export default OffcanvasFileUpload;
