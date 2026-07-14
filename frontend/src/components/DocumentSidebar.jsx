import UploadZone from "./UploadZone";

function DocumentSidebar({ documents, selectedIds, onToggleSelect, onDelete, onUploaded }) {
  return (
    <aside className="sidebar">
      <h2 className="sidebar-title">Documents</h2>
      <UploadZone onUploaded={onUploaded} />
      <ul className="document-list">
        {documents.map((doc) => (
          <li key={doc.id} className="document-item">
            <label className="document-label">
              <input
                type="checkbox"
                checked={selectedIds.includes(doc.id)}
                disabled={doc.status !== "ready"}
                onChange={() => onToggleSelect(doc.id)}
              />
              <span className="document-filename" title={doc.filename}>
                {doc.filename}
              </span>
              <span className={`document-status document-status-${doc.status}`}>
                {doc.status}
              </span>
            </label>
            <button
              type="button"
              className="document-delete"
              aria-label={`Delete ${doc.filename}`}
              onClick={() => onDelete(doc.id)}
            >
              ×
            </button>
          </li>
        ))}
        {documents.length === 0 && <li className="document-empty">No documents yet</li>}
      </ul>
    </aside>
  );
}

export default DocumentSidebar;
