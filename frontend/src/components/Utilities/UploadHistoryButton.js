import React, { useRef } from "react";

const UploadHistoryButton = ({ onFileSelect }) => {
  const filesElement = useRef(null);

  const sendFile = () => {
    const dataForm = new FormData();
    for (const file of filesElement.current.files) {
      dataForm.append("file", file);
    }
    console.log(dataForm);
  };

  return (
    <>
      <input
        ref={filesElement}
        type="file"
        // onChange={handleFileInput}
        multiple
      />
      <btn
        type="button"
        className="btn btn-outline-primary btn-sm"
        onClick={sendFile}
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="icon icon-tabler icon-tabler-plus"
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
          <line x1="12" y1="5" x2="12" y2="19"></line>
          <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
        Upload History
      </btn>
    </>
  );
};

export default UploadHistoryButton;
