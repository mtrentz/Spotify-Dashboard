import "@tabler/core/dist/css/tabler.min.css";
import "@tabler/core/dist/js/tabler";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import { NotificationProvider } from "./contexts/NotificationContext";
import { ThemeProvider } from "./contexts/ThemeContext";
import { AuthenticationProvider } from "./contexts/AuthenticationContext";

import Home from "./pages/Home";
import Login from "./pages/Login";
import Layout from "./components/Layout";

function App() {
  return (
    <div className="App">
      <AuthenticationProvider>
        <ThemeProvider>
          <NotificationProvider>
            <BrowserRouter>
              <Routes>
                <Route element={<Layout />}>
                  <Route path="/" element={<Home />} />
                </Route>
                <Route path="/login" element={<Login />} />
              </Routes>
            </BrowserRouter>
          </NotificationProvider>
        </ThemeProvider>
      </AuthenticationProvider>
    </div>
  );
}

export default App;
