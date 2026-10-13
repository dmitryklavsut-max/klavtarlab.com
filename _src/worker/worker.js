// klavtarlab-api: stores contact-form leads from klavtarlab.com in D1.
// POST /lead  {name, company, email, topic, message, lang, page, website(honeypot)}
// GET  /leads?key=ADMIN_KEY  -> latest 200 leads (JSON) ; add &format=html for a table
const ORIGINS = ["https://klavtarlab.com", "https://www.klavtarlab.com", "http://localhost:8765"];
const cors = (origin) => ({
  "Access-Control-Allow-Origin": ORIGINS.includes(origin) ? origin : ORIGINS[0],
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
  "Vary": "Origin",
});
const json = (data, status = 200, extra = {}) =>
  new Response(JSON.stringify(data), { status, headers: { "Content-Type": "application/json; charset=utf-8", ...extra } });
const clip = (v, n) => (typeof v === "string" ? v.trim().slice(0, n) : "");
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    const origin = req.headers.get("Origin") || "";
    if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: cors(origin) });

    if (url.pathname === "/lead" && req.method === "POST") {
      const h = cors(origin);
      if (origin && !ORIGINS.includes(origin)) return json({ ok: false, error: "origin" }, 403, h);
      let b;
      try { b = await req.json(); } catch { return json({ ok: false, error: "bad_json" }, 400, h); }
      if (b.website) return json({ ok: true }, 200, h); // honeypot: pretend success
      const lead = {
        name: clip(b.name, 120), company: clip(b.company, 160), email: clip(b.email, 160),
        topic: clip(b.topic, 120), message: clip(b.message, 4000), lang: clip(b.lang, 5), page: clip(b.page, 200),
      };
      if (!lead.name || !lead.message || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(lead.email)) return json({ ok: false, error: "invalid" }, 422, h);
      // simple rate limit: max 5 leads per email per day
      const { c } = await env.DB.prepare("SELECT COUNT(*) AS c FROM leads WHERE email = ? AND created_at > datetime('now','-1 day')").bind(lead.email).first();
      if (c >= 5) return json({ ok: false, error: "rate" }, 429, h);
      await env.DB.prepare("INSERT INTO leads (name, company, email, topic, message, lang, page, ip_country, user_agent) VALUES (?,?,?,?,?,?,?,?,?)")
        .bind(lead.name, lead.company, lead.email, lead.topic, lead.message, lead.lang, lead.page, req.cf?.country || "", clip(req.headers.get("User-Agent") || "", 300)).run();
      return json({ ok: true }, 200, h);
    }

    if (url.pathname === "/leads" && req.method === "GET") {
      if (!env.ADMIN_KEY || url.searchParams.get("key") !== env.ADMIN_KEY) return json({ ok: false }, 401);
      const { results } = await env.DB.prepare("SELECT * FROM leads ORDER BY id DESC LIMIT 200").all();
      if (url.searchParams.get("format") !== "html") return json(results);
      const rows = results.map((r) => `<tr><td>${esc(r.created_at)}</td><td>${esc(r.name)}<br><small>${esc(r.company)}</small></td><td><a href="mailto:${esc(r.email)}">${esc(r.email)}</a></td><td>${esc(r.topic)}</td><td style="white-space:pre-wrap">${esc(r.message)}</td><td>${esc(r.lang)} ${esc(r.ip_country)}</td></tr>`).join("");
      return new Response(`<!doctype html><meta charset="utf-8"><meta name="robots" content="noindex"><title>Leads</title><style>body{font:14px system-ui;margin:24px}table{border-collapse:collapse;width:100%}td,th{border-bottom:1px solid #ddd;padding:8px;text-align:left;vertical-align:top}</style><h1>Заявки klavtarlab.com</h1><table><tr><th>Дата (UTC)</th><th>Имя</th><th>Email</th><th>Тема</th><th>Сообщение</th><th>Язык</th></tr>${rows}</table>`, { headers: { "Content-Type": "text/html; charset=utf-8" } });
    }

    if (url.pathname === "/") return json({ service: "klavtarlab-api", ok: true });
    return json({ ok: false, error: "not_found" }, 404);
  },
};
