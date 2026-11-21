import type { Config } from "@netlify/functions";
import { getStore } from "@netlify/blobs";

// One blob per voter per poll: polls/<POLL>/<choice>/<voter>.
// Tallies come from listing keys, so nothing is ever read-modify-written.
const POLL = "next-up-1";
const OPTIONS = [
  "dungeon-crawler-carl",
  "tower-of-jack",
  "the-wandering-inn",
  "cradle",
  "beware-of-chicken",
  "heretical-fishing",
  "iron-prince",
  "red-rising",
  "old-mans-war",
  "tolkien",
];
const VOTER = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/;
const MAX_BODY = 512;
const HEADERS = {
  "cache-control": "no-store",
  "x-content-type-options": "nosniff",
  "content-security-policy": "default-src 'none'; frame-ancestors 'none'",
  "referrer-policy": "no-referrer",
};
const json = (data: unknown, status = 200) => Response.json(data, { status, headers: HEADERS });

export default async (req: Request) => {
  const store = getStore({ name: "polls", consistency: "strong" });

  if (req.method === "POST") {
    if (!(req.headers.get("content-type") ?? "").startsWith("application/json")) {
      return json({ error: "Send JSON" }, 415);
    }
    const origin = req.headers.get("origin");
    if (origin && origin !== new URL(req.url).origin) {
      return json({ error: "Cross-site votes are not accepted" }, 403);
    }
    const raw = await req.text();
    if (raw.length > MAX_BODY) return json({ error: "Request too large" }, 413);
    let body: { choice?: unknown; voter?: unknown };
    try {
      body = JSON.parse(raw);
    } catch {
      return json({ error: "Bad request" }, 400);
    }
    const choice = String(body.choice ?? "");
    const voter = String(body.voter ?? "");
    if (!OPTIONS.includes(choice) || !VOTER.test(voter)) {
      return json({ error: "Unknown choice" }, 400);
    }
    await Promise.all(
      OPTIONS.filter((o) => o !== choice).map((o) => store.delete(`${POLL}/${o}/${voter}`)),
    );
    await store.set(`${POLL}/${choice}/${voter}`, "1");
  }

  const counts: Record<string, number> = Object.fromEntries(OPTIONS.map((o) => [o, 0]));
  const { blobs } = await store.list({ prefix: `${POLL}/` });
  for (const b of blobs) {
    const option = b.key.split("/")[1];
    if (option in counts) counts[option] += 1;
  }
  return json({ poll: POLL, counts });
};

export const config: Config = {
  path: "/api/vote",
  method: ["GET", "POST"],
  // Caps how fast one visitor can hit the endpoint, to slow ballot stuffing and storage abuse.
  rateLimit: { windowLimit: 30, windowSize: 60, aggregateBy: ["ip", "domain"] },
};
