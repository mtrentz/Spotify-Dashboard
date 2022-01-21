import "@tabler/core/dist/css/tabler.min.css";
import "@tabler/core/dist/js/tabler";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";

import { ApiProvider } from "./components/Contexts/ApiContext";
import { NotificationProvider } from "./components/Contexts/NotificationContext";

import Home from "./pages/Home";
import Layout from "./components/Layout";

function App() {
  return (
    <div className="App">
      <ApiProvider>
        <NotificationProvider>
          <BrowserRouter>
            <Layout>
              <Routes>
                <Route path="/" element={<Home />} />
              </Routes>
            </Layout>
          </BrowserRouter>
        </NotificationProvider>
      </ApiProvider>
    </div>
  );
}

export default App;
