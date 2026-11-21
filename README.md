# Lore & Loot Club

Fan-run hangout site for LitRPG, fantasy and sci-fi readers: https://loreandlootclub.com

- `public/` is the static site (home page with the vote, authors, narrators, creators, community).
- `netlify/functions/vote.mts` is the vote endpoint (`/api/vote`), stored in Netlify Blobs.
- `netlify.toml` sets the publish folder and security headers.

Run locally: `npm install`, then `npx netlify-cli dev`.

Hosted on Netlify (project `loreandlootclub`). Domain registered at Namecheap.
