(() => {
  const doc = document.documentElement;
  doc.classList.add("js");
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* header: border on scroll + mobile menu */
  const header = document.querySelector(".site-header");
  if (header) {
    const onScroll = () => header.classList.toggle("scrolled", window.scrollY > 8);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    const btn = header.querySelector(".menu-btn");
    if (btn) {
      btn.addEventListener("click", () => {
        const open = header.classList.toggle("open");
        btn.setAttribute("aria-expanded", String(open));
      });
      header.querySelectorAll(".nav a").forEach((a) => a.addEventListener("click", () => {
        header.classList.remove("open");
        btn.setAttribute("aria-expanded", "false");
      }));
    }
  }

  /* reveal on scroll (screenshots wipe in, process line fills) */
  const io = "IntersectionObserver" in window ? new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
    });
  }, { threshold: 0.25 }) : null;
  document.querySelectorAll(".reveal, .steps").forEach((el) => io ? io.observe(el) : el.classList.add("in"));

  /* count-up for fact numbers */
  const fmt = (n, lang) => n.toLocaleString(lang === "en" ? "en-US" : lang === "pl" ? "pl-PL" : "ru-RU");
  const lang = doc.lang || "en";
  const counters = document.querySelectorAll("[data-count]");
  const runCount = (el) => {
    const target = Number(el.dataset.count);
    const plain = el.dataset.plain === "1";
    const suffix = el.dataset.suffix || "";
    if (reduce) { el.textContent = (plain ? target : fmt(target, lang)) + suffix; return; }
    const t0 = performance.now(), dur = 1400;
    const step = (t) => {
      const p = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - p, 3);
      const v = Math.round(target * e);
      el.textContent = (plain ? v : fmt(v, lang)) + suffix;
      if (p < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  };
  if (counters.length) {
    const cio = io ? new IntersectionObserver((entries) => entries.forEach((e) => {
      if (e.isIntersecting) { runCount(e.target); cio.unobserve(e.target); }
    }), { threshold: 0.6 }) : null;
    counters.forEach((el) => cio ? cio.observe(el) : runCount(el));
  }

  /* order wheel */
  const wheel = document.getElementById("wheel");
  if (wheel) {
    const data = JSON.parse(wheel.dataset.orders);
    const months = JSON.parse(wheel.dataset.months);
    const start = new Date(Date.UTC(2025, 9, 13));
    const NS = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(NS, "svg");
    svg.setAttribute("viewBox", "-284 -284 568 568");
    svg.setAttribute("role", "img");
    svg.setAttribute("aria-label", wheel.dataset.label);
    const max = Math.max(...data);
    const sorted = [...data].sort((a, b) => b - a);
    const peakMin = sorted[Math.floor(data.length * 0.06)];
    const r0 = 148, span = 132;
    const ring = document.createElementNS(NS, "circle");
    ring.setAttribute("r", r0 - 6); ring.setAttribute("class", "ring");
    svg.appendChild(ring);
    const rays = [];
    const g = document.createElementNS(NS, "g");
    const hits = document.createElementNS(NS, "g");
    data.forEach((v, i) => {
      const a = (i / data.length) * Math.PI * 2 - Math.PI / 2;
      const len = 4 + (v / max) * span;
      const cos = Math.cos(a), sin = Math.sin(a);
      const x1 = cos * r0, y1 = sin * r0, x2 = cos * (r0 + len), y2 = sin * (r0 + len);
      const ln = document.createElementNS(NS, "line");
      ln.setAttribute("x1", x1.toFixed(2)); ln.setAttribute("y1", y1.toFixed(2));
      ln.setAttribute("x2", x2.toFixed(2)); ln.setAttribute("y2", y2.toFixed(2));
      ln.setAttribute("pathLength", "1");
      ln.setAttribute("class", "ray" + (v >= peakMin && v > 0 ? " peak" : ""));
      ln.style.animationDelay = (reduce ? 0 : 200 + i * 3.2) + "ms";
      g.appendChild(ln); rays.push(ln);
      const hit = document.createElementNS(NS, "line");
      hit.setAttribute("x1", (cos * (r0 - 10)).toFixed(2)); hit.setAttribute("y1", (sin * (r0 - 10)).toFixed(2));
      hit.setAttribute("x2", (cos * (r0 + span + 10)).toFixed(2)); hit.setAttribute("y2", (sin * (r0 + span + 10)).toFixed(2));
      hit.setAttribute("class", "hit"); hit.dataset.i = i;
      hits.appendChild(hit);
    });
    svg.appendChild(g);
    // month ticks
    for (let i = 0; i < data.length; i++) {
      const d = new Date(start.getTime() + i * 864e5);
      if (d.getUTCDate() !== 1) continue;
      const a = (i / data.length) * Math.PI * 2 - Math.PI / 2;
      const t = document.createElementNS(NS, "line");
      t.setAttribute("x1", (Math.cos(a) * (r0 - 12)).toFixed(2)); t.setAttribute("y1", (Math.sin(a) * (r0 - 12)).toFixed(2));
      t.setAttribute("x2", (Math.cos(a) * (r0 - 3)).toFixed(2)); t.setAttribute("y2", (Math.sin(a) * (r0 - 3)).toFixed(2));
      t.setAttribute("class", "tick"); svg.appendChild(t);
      const lb = document.createElementNS(NS, "text");
      const am = a + (Math.PI * 2 / data.length) * 14;
      lb.setAttribute("x", (Math.cos(am) * (r0 - 24)).toFixed(2)); lb.setAttribute("y", (Math.sin(am) * (r0 - 24)).toFixed(2));
      lb.setAttribute("class", "mlabel"); lb.textContent = months[d.getUTCMonth()];
      svg.appendChild(lb);
    }
    svg.appendChild(hits);
    wheel.prepend(svg);

    const big = wheel.querySelector(".wheel-center b");
    const small = wheel.querySelector(".wheel-center span");
    const big0 = big.textContent, small0 = small.textContent;
    const dfmt = new Intl.DateTimeFormat(lang === "en" ? "en-GB" : lang, { day: "numeric", month: "short", year: "numeric", timeZone: "UTC" });
    let active = null;
    const show = (i) => {
      if (active) active.classList.remove("on");
      active = rays[i]; active.classList.add("on");
      big.textContent = data[i];
      small.textContent = wheel.dataset.ordersWord + ", " + dfmt.format(new Date(start.getTime() + i * 864e5));
    };
    const clear = () => {
      if (active) active.classList.remove("on");
      active = null; big.textContent = big0; small.textContent = small0;
    };
    hits.addEventListener("pointerover", (e) => { if (e.target.dataset.i) show(+e.target.dataset.i); });
    svg.addEventListener("pointerleave", clear);
  }

  /* lead form */
  const form = document.getElementById("lead-form");
  if (form) {
    const status = form.querySelector(".form-status");
    const btn = form.querySelector("button[type=submit]");
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      if (!form.reportValidity()) return;
      const fd = new FormData(form);
      const payload = Object.fromEntries(fd.entries());
      payload.lang = lang; payload.page = location.pathname;
      btn.disabled = true; const label = btn.textContent; btn.textContent = form.dataset.sending;
      status.className = "form-status"; status.textContent = "";
      try {
        const res = await fetch(form.action, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
        if (!res.ok) throw new Error(String(res.status));
        form.reset();
        status.classList.add("ok"); status.textContent = form.dataset.ok;
      } catch (err) {
        status.classList.add("err"); status.textContent = form.dataset.err;
      } finally {
        btn.disabled = false; btn.textContent = label;
      }
    });
  }
})();
