import React, { useContext, useEffect } from "react";
import NotificationContext from "../Contexts/NotificationContext";

const Notifications = () => {
  const { notifications, removeNotification } = useContext(NotificationContext);

  // Remove notifications after a certain amount of time
  useEffect(() => {
    const timer = setTimeout(() => {
      removeNotification(notifications[0]);
    }, 5000);

    return () => clearTimeout(timer);
  }, [notifications, removeNotification]);

  //   Logic here is to show only the first notification on the list
  return (
    <>
      {notifications.length >= 1 ? (
        <div
          className={`alert alert-${notifications[0]["type"]} alert-dismissible position-fixed right-2 top-2 h-22 w-72 `}
          role="alert"
        >
          <div className="d-flex">
            <div></div>
            <div>
              <h4 className="alert-title">{notifications[0]["msg"]}</h4>
              <div className="text-muted">{notifications[0]["msg_muted"]}</div>
            </div>
          </div>
          <a
            className="btn-close"
            // data-bs-dismiss="alert"
            // aria-label="close"
            onClick={() => removeNotification(notifications[0])}
          ></a>
        </div>
      ) : null}
    </>
  );
};

export default Notifications;
