import { useRef, useState } from "react";
import { uploadDocument } from "../api/client";

function UploadZone({ onUploaded }) {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState(null);
  const inputRef = useRef(null);

  async function handleFiles(files) {
    const file = files?.[0];
    if (!file) return;

    if (file.type !== "application/pdf") {
      setError("Only PDF files are supported");
      return;
    }

    setError(null);
    setIsUploading(true);
    try {
      const document = await uploadDocument(file);
      onUploaded(document);
    } catch {
      setError("Upload failed. Please try again.");
    } finally {
      setIsUploading(false);
    }
  }

  return (
    <div
      className={`upload-zone${isDragging ? " upload-zone-dragging" : ""}`}
      onDragOver={(event) => {
        event.preventDefault();
        setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={(event) => {
        event.preventDefault();
        setIsDragging(false);
        handleFiles(event.dataTransfer.files);
      }}
      onClick={() => inputRef.current?.click()}
      role="button"
      tabIndex={0}
    >
      <input
        ref={inputRef}
        type="file"
        accept="application/pdf"
        hidden
        onChange={(event) => handleFiles(event.target.files)}
      />
      <p className="upload-zone-label">
        {isUploading ? "Uploading…" : "Drop a PDF here or click to upload"}
      </p>
      {error && <p className="status status-error">{error}</p>}
    </div>
  );
}

export default UploadZone;
