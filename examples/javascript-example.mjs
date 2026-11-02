// Run with Node.js 22+; no additional dependencies.
for (const name of ["OPENAI_BASE_URL", "OPENAI_API_KEY", "OPENAI_MODEL"]) {
  if (!process.env[name]) throw new Error(`Set ${name} first.`);
}
const response = await fetch(
  `${process.env.OPENAI_BASE_URL.replace(/\/+$/, "")}/chat/completions`,
  {
    method: "POST",
    headers: {
      Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: process.env.OPENAI_MODEL,
      messages: [
        { role: "system", content: "Be concise and do not invent details." },
        { role: "user", content: "Summarise: The course was useful, but I wanted more exercises." },
      ],
    }),
    signal: AbortSignal.timeout(120000),
  },
);
if (!response.ok) throw new Error(`Request failed: HTTP ${response.status}`);
const result = await response.json();
console.log(result.choices[0].message.content);
