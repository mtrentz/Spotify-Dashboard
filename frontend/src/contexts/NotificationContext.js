import { createContext, useState } from "react";

const NotificationContext = createContext();

export default NotificationContext;

export const NotificationProvider = ({ children }) => {
  const [notifications, setNotifications] = useState([]);

  const addNotification = (notification) => {
    setNotifications([...notifications, notification]);
  };

  const removeNotification = (notification) => {
    setNotifications(notifications.filter((n) => n !== notification));
  };

  const contextData = {
    notifications: notifications,
    addNotification: addNotification,
    removeNotification: removeNotification,
  };

  return (
    <NotificationContext.Provider value={contextData}>
      {children}
    </NotificationContext.Provider>
  );
};
