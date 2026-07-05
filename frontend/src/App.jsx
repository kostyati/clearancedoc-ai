import { useEffect, useState } from "react";
import { getHealth } from "./api/client";

function App() {
  const [health, setHealth] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    getHealth().then(setHealth).catch(() => setError("Backend unreachable"));
  }, []);

  return (
    <div className="app">
      <h1>ClearanceDoc AI</h1>
      {error && <p className="status status-error">{error}</p>}
      {health && (
        <p className="status status-ok">
          Backend: {health.status} ({health.environment})
        </p>
      )}
    </div>
  );
}

export default App;
