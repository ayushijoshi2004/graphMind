export async function uploadCsv(files: File[]) {
  const form = new FormData();
  files.forEach((file) => form.append("files", file));

  const response = await fetch("http://localhost:8000/upload-csv", {
    method: "POST",
    body: form,
  });
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

export async function sendPrompt(prompt: string) {
  const response = await fetch("http://localhost:8000/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt }),
  });
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}
