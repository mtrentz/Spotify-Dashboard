import React, { useContext, useState } from "react";
import { useForm } from "react-hook-form";

import ApiContext from "../Contexts/ApiContext";
import NotificationContext from "../Contexts/NotificationContext";

const OffcanvasFileUpload = () => {
  const { api } = useContext(ApiContext);
  const { addNotification } = useContext(NotificationContext);

  const { register, handleSubmit, getValues } = useForm();
  const [files, setFiles] = useState(0);

  const handleFileSelect = () => {
    const files = getValues("file");
    setFiles(Object.values(files));
  };

  const onSubmit = (values) => {
    let formData = new FormData();
    for (const file of values.file) {
      formData.append("file", file);
    }

    // It takes a while to process the files.
    // For this reason I'm setting a timeout of 10s per file
    const timeOut = files.length * 10000;

    api
      .post("/history/", formData, { timeout: timeOut })
      .then((res) => {
        console.log(res);
        addNotification({
          type: "success",
          msg: "Successfully uploaded files!",
          msg_muted: "It might take a while for everything to update.",
        });
      })
      .catch((err) => {
        console.log(err.response);
        addNotification({
          type: "danger",
          msg: "Something went wrong!",
          msg_muted: "Are you sure you uploaded the correct files?",
        });
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
            to request it through the official Spotify website.
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
          </div>
          <button
            type="submit"
            className="btn btn-primary w-32 h-8 font-bold"
            // If there was files, once the button is clicked the offcanvas will close
            data-bs-dismiss={files ? "offcanvas" : ""}
          >
            Submit
          </button>
        </form>
        <div className="mt-2">
          {files.length > 0 ? <h4>Selected Files</h4> : null}
          {files.length > 0
            ? files.map((f, index) => (
                <div className="my-1" key={index}>
                  {f.name}
                </div>
              ))
            : null}
        </div>
      </div>
    </div>
  );
};

export default OffcanvasFileUpload;
