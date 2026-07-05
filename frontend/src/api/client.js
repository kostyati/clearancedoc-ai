import axios from "axios";

const client = axios.create({
  baseURL: "/api",
});

export async function getHealth() {
  const { data } = await client.get("/health");
  return data;
}

export default client;
