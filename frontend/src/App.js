import "@tabler/core/dist/css/tabler.min.css";
import "@tabler/core/dist/js/tabler";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";

import { ApiProvider } from "./components/Contexts/ApiContext";

import Home from "./pages/Home";
import Layout from "./components/Layout";

function App() {
  return (
    <div className="App">
      <ApiProvider>
        <BrowserRouter>
          <Layout>
            <Routes>
              <Route path="/" element={<Home />} />
            </Routes>
          </Layout>
        </BrowserRouter>
      </ApiProvider>
    </div>
  );
}

export default App;
