import "@tabler/core/dist/css/tabler.min.css";
import "@tabler/core/dist/js/tabler";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import { ApiProvider } from "./components/Contexts/ApiContext";
import { NotificationProvider } from "./components/Contexts/NotificationContext";
import { ThemeProvider } from "./components/Contexts/ThemeContext";

import Home from "./pages/Home";
import Login from "./pages/Login";
import Layout from "./components/Layout";

function App() {
  return (
    <div className="App">
      <ThemeProvider>
        <ApiProvider>
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
        </ApiProvider>
      </ThemeProvider>
    </div>
  );
}

export default App;
