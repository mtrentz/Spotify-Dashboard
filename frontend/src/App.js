import "@tabler/core/dist/css/tabler.min.css";
import "@tabler/core/dist/js/tabler";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import { NotificationProvider } from "./contexts/NotificationContext";
import { ThemeProvider } from "./contexts/ThemeContext";
import { AuthenticationProvider } from "./contexts/AuthenticationContext";

import Home from "./pages/Home";
import YearInReview from "./pages/YearInReview";
import Login from "./pages/Login";
import Layout from "./components/Layout";
import NotFound from "./pages/NotFound";
import RequireAuth from "./components/RequireAuth";

function App() {
  return (
    <div className="App">
      <AuthenticationProvider>
        <ThemeProvider>
          <NotificationProvider>
            <BrowserRouter>
              <Routes>
                <Route element={<RequireAuth />}>
                  <Route element={<Layout />}>
                    <Route path="/" element={<Home />} />
                    <Route
                      path="/year-in-review/:year"
                      element={<YearInReview />}
                    />
                  </Route>
                </Route>
                <Route path="/login" element={<Login />} />
                <Route path="*" element={<NotFound />} />
              </Routes>
            </BrowserRouter>
          </NotificationProvider>
        </ThemeProvider>
      </AuthenticationProvider>
    </div>
  );
}

export default App;
