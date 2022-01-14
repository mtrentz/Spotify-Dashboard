import Home from "./pages/Home";
import Layout from "./components/Layout";

import "@tabler/core/dist/css/tabler.min.css";
import "@tabler/core/dist/js/tabler";

function App() {
  return (
    <div className="App">
      <Layout>
        <Home />
      </Layout>
    </div>
  );
}

export default App;
