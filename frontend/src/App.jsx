import { useCallback, useEffect, useState } from "react";
import { deleteDocument, getHealth, listDocuments } from "./api/client";
import DocumentSidebar from "./components/DocumentSidebar";
import ChatPanel from "./components/ChatPanel";

function App() {
  const [health, setHealth] = useState(null);
  const [healthError, setHealthError] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [selectedIds, setSelectedIds] = useState([]);

  const refreshDocuments = useCallback(async () => {
    const docs = await listDocuments();
    setDocuments(docs);
  }, []);

  useEffect(() => {
    getHealth().then(setHealth).catch(() => setHealthError("Backend unreachable"));
    refreshDocuments().catch(() => setHealthError("Backend unreachable"));
  }, [refreshDocuments]);

  function handleUploaded(document) {
    setDocuments((prev) => [...prev, document]);
    if (document.status === "ready") {
      setSelectedIds((prev) => [...prev, document.id]);
    }
  }

  async function handleDelete(documentId) {
    await deleteDocument(documentId);
    setDocuments((prev) => prev.filter((doc) => doc.id !== documentId));
    setSelectedIds((prev) => prev.filter((id) => id !== documentId));
  }

  function handleToggleSelect(documentId) {
    setSelectedIds((prev) =>
      prev.includes(documentId) ? prev.filter((id) => id !== documentId) : [...prev, documentId],
    );
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>ClearanceDoc AI</h1>
        {healthError && <p className="status status-error">{healthError}</p>}
        {health && (
          <p className="status status-ok">
            Backend: {health.status} ({health.environment})
          </p>
        )}
      </header>
      <div className="app-body">
        <DocumentSidebar
          documents={documents}
          selectedIds={selectedIds}
          onToggleSelect={handleToggleSelect}
          onDelete={handleDelete}
          onUploaded={handleUploaded}
        />
        <ChatPanel selectedDocumentIds={selectedIds} />
      </div>
    </div>
  );
}

export default App;
