import axios from "axios";

const client = axios.create({
  baseURL: "/api",
});

export async function getHealth() {
  const { data } = await client.get("/health");
  return data;
}

export async function listDocuments() {
  const { data } = await client.get("/documents");
  return data;
}

export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await client.post("/documents", formData);
  return data;
}

export async function deleteDocument(documentId) {
  await client.delete(`/documents/${documentId}`);
}

export async function askQuestion(documentIds, question) {
  const { data } = await client.post("/chat", {
    document_ids: documentIds,
    question,
  });
  return data;
}

export default client;
