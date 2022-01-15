import Home from "./pages/Home";
import Layout from "./components/Layout";
import { ApiProvider } from "./components/Contexts/ApiContext";

import "@tabler/core/dist/css/tabler.min.css";
import "@tabler/core/dist/js/tabler";

function App() {
  return (
    <div className="App">
      <ApiProvider>
        <Layout>
          <Home />
        </Layout>
      </ApiProvider>
    </div>
  );
}

export default App;
