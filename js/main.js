(() => {
  const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const S = window.SITE || {};
  $("[data-year]").textContent = new Date().getFullYear();

  // Mobile menu
  const burger = $(".burger"), nav = $("#nav");
  const setMenu = o => { burger.setAttribute("aria-expanded", o); nav.classList.toggle("open", o); document.body.style.overflow = o ? "hidden" : ""; };
  burger.addEventListener("click", () => setMenu(burger.getAttribute("aria-expanded") !== "true"));
  nav.addEventListener("click", e => e.target.closest("a") && setMenu(false));
  addEventListener("keydown", e => e.key === "Escape" && setMenu(false));
  matchMedia("(min-width:52.01rem)").addEventListener("change", () => setMenu(false));

  // Image placeholders: labelled box if the file is not there yet
  const miss = i => i.closest(".ph")?.classList.add("is-missing");
  $$(".ph img").forEach(i => { if (i.complete && !i.naturalWidth) miss(i); i.addEventListener("error", () => miss(i)); });

  // Collection filter
  $$(".chip").forEach(c => c.addEventListener("click", () => {
    $$(".chip").forEach(x => { x.classList.toggle("on", x === c); x.setAttribute("aria-pressed", x === c); });
    $$(".products .card").forEach(k => k.hidden = c.dataset.filter !== "all" && k.dataset.cat !== c.dataset.filter);
  }));

  // FAQ accordion
  $$(".acc button").forEach(b => b.addEventListener("click", () => {
    const o = b.getAttribute("aria-expanded") !== "true";
    b.setAttribute("aria-expanded", o); $("#" + b.getAttribute("aria-controls")).classList.toggle("open", o);
  }));

  // Analytics only after consent (GA4 id is public; set in build.py)
  const loadAnalytics = () => {
    if (!S.gaId || window.__ga) return; window.__ga = 1;
    const s = document.createElement("script"); s.async = true; s.src = "https://www.googletagmanager.com/gtag/js?id=" + S.gaId; document.head.appendChild(s);
    window.dataLayer = window.dataLayer || []; window.gtag = function () { dataLayer.push(arguments); };
    gtag("js", new Date()); gtag("config", S.gaId, { anonymize_ip: true });
  };
  const bar = $(".cookie"), get = () => { try { return localStorage.getItem("consent"); } catch { return null; } };
  const choice = get();
  if (choice === "yes") loadAnalytics(); else if (!choice) bar.hidden = false;
  $$("[data-consent]", bar).forEach(b => b.addEventListener("click", () => {
    try { localStorage.setItem("consent", b.dataset.consent); } catch {}
    bar.hidden = true; if (b.dataset.consent === "yes") loadAnalytics();
  }));

  // Contact form: validation + spam protection (honeypot, minimum fill time, rate limit)
  const form = $(".form"); if (!form) return;
  const opened = Date.now(), status = $("#fstatus");
  const rules = {
    name: v => v.trim().length < 2 ? "Enter your name." : "",
    email: v => /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v) ? "" : "Enter a valid email address, like name@example.com.",
    phone: v => !v || /^[0-9+()\-\s]{7,18}$/.test(v) ? "" : "Use digits, spaces, + or - only (7 to 18 characters).",
    message: v => v.trim().length < 10 ? "Write at least 10 characters so we can help." : ""
  };
  const check = el => { const m = rules[el.name](el.value), f = el.closest(".field");
    f.classList.toggle("bad", !!m); $(".err", f).textContent = m; el.setAttribute("aria-invalid", !!m); return !m; };
  Object.keys(rules).forEach(n => { const el = form.elements[n]; el.addEventListener("blur", () => check(el)); el.addEventListener("input", () => el.closest(".field").classList.contains("bad") && check(el)); });
  const say = (t, c) => { status.textContent = t; status.className = "status " + c; };
  form.addEventListener("submit", async e => {
    e.preventDefault();
    const bad = Object.keys(rules).map(n => form.elements[n]).filter(el => !check(el));
    if (bad.length) { bad[0].focus(); return say("Please fix the highlighted fields.", "fail"); }
    if (form.elements.company.value || Date.now() - opened < 3000) return say("Thank you. We will reply within two working days.", "ok"); // bots get a fake success
    let last = 0; try { last = +sessionStorage.getItem("sent") || 0; } catch {}
    if (Date.now() - last < 30000) return say("Please wait a moment before sending another message.", "fail");
    const data = Object.fromEntries(new FormData(form)); delete data.company;
    try {
      if (S.endpoint) {
        const r = await fetch(S.endpoint, { method: "POST", headers: { "Content-Type": "application/json", Accept: "application/json" }, body: JSON.stringify(data) });
        if (!r.ok) throw 0;
      } else {
        location.href = `mailto:${S.email}?subject=${encodeURIComponent("Website enquiry from " + data.name)}&body=${encodeURIComponent(data.message + "\n\n" + data.name + "\n" + data.email + "\n" + data.phone)}`;
      }
      try { sessionStorage.setItem("sent", Date.now()); } catch {}
      form.reset(); say("Thank you. We will reply within two working days.", "ok");
    } catch { say("Something went wrong. Please try again or email " + S.email + ".", "fail"); }
  });
})();
