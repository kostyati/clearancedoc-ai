import { useState } from "react";
import { askQuestion } from "../api/client";

function ChatPanel({ selectedDocumentIds }) {
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState("");
  const [isAsking, setIsAsking] = useState(false);
  const [error, setError] = useState(null);

  const canAsk = selectedDocumentIds.length > 0 && question.trim() && !isAsking;

  async function handleSubmit(event) {
    event.preventDefault();
    if (!canAsk) return;

    const askedQuestion = question.trim();
    setMessages((prev) => [...prev, { role: "user", text: askedQuestion }]);
    setQuestion("");
    setError(null);
    setIsAsking(true);

    try {
      const response = await askQuestion(selectedDocumentIds, askedQuestion);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: response.answer, citations: response.citations },
      ]);
    } catch {
      setError("Something went wrong answering that question.");
    } finally {
      setIsAsking(false);
    }
  }

  return (
    <section className="chat-panel">
      <div className="chat-messages">
        {messages.length === 0 && (
          <p className="chat-empty">
            {selectedDocumentIds.length === 0
              ? "Select one or more documents to start asking questions."
              : "Ask a question about the selected documents."}
          </p>
        )}
        {messages.map((message, index) => (
          <div key={index} className={`chat-message chat-message-${message.role}`}>
            <p>{message.text}</p>
            {message.citations?.length > 0 && (
              <ul className="chat-citations">
                {message.citations.map((citation, citationIndex) => (
                  <li key={citationIndex} className="chat-citation">
                    Page {citation.page_number}: {citation.text}
                  </li>
                ))}
              </ul>
            )}
          </div>
        ))}
        {isAsking && <p className="chat-pending">Thinking…</p>}
        {error && <p className="status status-error">{error}</p>}
      </div>
      <form className="chat-input-row" onSubmit={handleSubmit}>
        <input
          type="text"
          value={question}
          placeholder="Ask a question about the selected documents…"
          disabled={selectedDocumentIds.length === 0}
          onChange={(event) => setQuestion(event.target.value)}
        />
        <button type="submit" disabled={!canAsk}>
          Ask
        </button>
      </form>
    </section>
  );
}

export default ChatPanel;
