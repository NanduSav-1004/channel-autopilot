// Motion-graphics scenes for the data channel. Python loads one scene with load(spec), then calls seek(t) for every frame and
// screenshots the page. Everything on screen is a pure function of t, so frames can be rendered in any order and always match.
(function () {
  "use strict";

  const C = { bg: "#0b0d17", bg2: "#151a2e", ink: "#f5f3ee", muted: "#8a8fa8", faint: "#2a3048",
              volt: "#d4ff3a", coral: "#ff5c7a", cyan: "#39d2ff", amber: "#ffb547" };
  const FIPS = { "01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA", "08": "CO", "09": "CT", "10": "DE", "11": "DC", "12": "FL",
    "13": "GA", "15": "HI", "16": "ID", "17": "IL", "18": "IN", "19": "IA", "20": "KS", "21": "KY", "22": "LA", "23": "ME", "24": "MD",
    "25": "MA", "26": "MI", "27": "MN", "28": "MS", "29": "MO", "30": "MT", "31": "NE", "32": "NV", "33": "NH", "34": "NJ", "35": "NM",
    "36": "NY", "37": "NC", "38": "ND", "39": "OH", "40": "OK", "41": "OR", "42": "PA", "44": "RI", "45": "SC", "46": "SD", "47": "TN",
    "48": "TX", "49": "UT", "50": "VT", "51": "VA", "53": "WA", "54": "WV", "55": "WI", "56": "WY" };

  // ---- timing helpers -------------------------------------------------------------------------------------------------
  const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
  const prog = (t, start, dur) => clamp((t - start) / dur);
  const E = {
    out: (x) => 1 - Math.pow(1 - x, 3),
    inOut: (x) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2),
    expo: (x) => (x >= 1 ? 1 : 1 - Math.pow(2, -10 * x)),
    back: (x) => { const c = 1.70158 * 1.3; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); },
  };
  const lerp = (a, b, x) => a + (b - a) * x;

  function fmt(v, s) {
    const d = s.decimals ?? 0;
    let n = null;
    if (s.compact) for (const [size, w] of [[1e12, "T"], [1e9, "B"], [1e6, "M"]]) if (Math.abs(v) >= size) { n = (v / size).toFixed(Math.max(d, 1)) + w; break; }
    if (n === null) n = Math.abs(v).toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d });
    else n = n.replace("-", "");
    return (v < 0 ? "-" : "") + (s.prefix || "") + n + (s.suffix || "");
  }

  // ---- stage ----------------------------------------------------------------------------------------------------------
  let svg, W, H, scene = null;

  function defs() {
    const d = svg.append("defs");
    const glow = d.append("filter").attr("id", "glow").attr("x", "-50%").attr("y", "-50%").attr("width", "200%").attr("height", "200%");
    glow.append("feGaussianBlur").attr("stdDeviation", 10).attr("result", "b");
    const m = glow.append("feMerge"); m.append("feMergeNode").attr("in", "b"); m.append("feMergeNode").attr("in", "SourceGraphic");
    const soft = d.append("filter").attr("id", "soft").attr("x", "-50%").attr("y", "-50%").attr("width", "200%").attr("height", "200%");
    soft.append("feGaussianBlur").attr("stdDeviation", 60);
    for (const [id, col] of [["blobA", C.cyan], ["blobB", C.coral], ["blobC", C.volt]]) {
      const g = d.append("radialGradient").attr("id", id);
      g.append("stop").attr("offset", "0%").attr("stop-color", col).attr("stop-opacity", 0.55);
      g.append("stop").attr("offset", "100%").attr("stop-color", col).attr("stop-opacity", 0);
    }
    const area = d.append("linearGradient").attr("id", "area").attr("x1", 0).attr("y1", 0).attr("x2", 0).attr("y2", 1);
    area.append("stop").attr("offset", "0%").attr("stop-color", C.volt).attr("stop-opacity", 0.32);
    area.append("stop").attr("offset", "100%").attr("stop-color", C.volt).attr("stop-opacity", 0);
    const bar = d.append("linearGradient").attr("id", "bar").attr("x1", 0).attr("x2", 1);
    bar.append("stop").attr("offset", "0%").attr("stop-color", "#2b6cff");
    bar.append("stop").attr("offset", "100%").attr("stop-color", C.cyan);
    const hot = d.append("linearGradient").attr("id", "hot").attr("x1", 0).attr("x2", 1);
    hot.append("stop").attr("offset", "0%").attr("stop-color", "#9be22a");
    hot.append("stop").attr("offset", "100%").attr("stop-color", C.volt);
    return d;
  }

  function background(root) {
    const g = root.append("g");
    g.append("rect").attr("width", W).attr("height", H).attr("fill", C.bg);
    const blobs = [["blobA", 0.18, 0.25, 0.55], ["blobB", 0.85, 0.8, 0.45], ["blobC", 0.7, 0.15, 0.3]].map(([id, x, y, r]) =>
      ({ el: g.append("circle").attr("r", r * W).attr("fill", `url(#${id})`).attr("opacity", 0.5), x, y }));
    const grid = g.append("g").attr("stroke", C.faint).attr("stroke-width", 1).attr("opacity", 0.35);
    const step = 120;
    for (let x = -step; x <= W + step; x += step) grid.append("line").attr("x1", x).attr("x2", x).attr("y1", -step).attr("y2", H + step);
    for (let y = -step; y <= H + step; y += step) grid.append("line").attr("y1", y).attr("y2", y).attr("x1", -step).attr("x2", W + step);
    g.append("rect").attr("width", W).attr("height", H).attr("fill", "url(#vignette)");
    const vig = svg.select("defs").append("radialGradient").attr("id", "vignette").attr("r", "75%");
    vig.append("stop").attr("offset", "55%").attr("stop-color", "#000").attr("stop-opacity", 0);
    vig.append("stop").attr("offset", "100%").attr("stop-color", "#000").attr("stop-opacity", 0.55);
    return (t) => {
      blobs.forEach((b, i) => b.el.attr("cx", (b.x + 0.06 * Math.sin(t * 0.35 + i * 2)) * W)
        .attr("cy", (b.y + 0.05 * Math.cos(t * 0.3 + i)) * H));
      grid.attr("transform", `translate(${(-t * 12) % step},${(-t * 6) % step})`);
    };
  }

  // Text helpers. Words are separate <text> nodes so each can move on its own.
  function words(g, str, x, y, size, maxW, opts = {}) {
    const out = []; let line = [], lines = [];
    const probe = g.append("text").attr("font-size", size).attr("font-weight", opts.weight || 700);
    const width = (s) => { probe.text(s); return probe.node().getComputedTextLength(); };
    for (const w of str.split(/\s+/)) {
      const tryLine = [...line, w].join(" ");
      if (line.length && width(tryLine) > maxW) { lines.push(line); line = [w]; } else line.push(w);
    }
    if (line.length) lines.push(line);
    const space = width("a b") - width("ab"), lh = size * (opts.lh || 1.08);
    const top = y - ((lines.length - 1) * lh) / 2;
    lines.forEach((ln, li) => {
      const total = width(ln.join(" "));
      let cx = opts.anchor === "start" ? x : x - total / 2;
      for (const w of ln) {
        const ww = width(w);
        const hl = opts.highlight && opts.highlight.some((h) => w.toLowerCase().replace(/[^a-z0-9$%]/g, "").startsWith(h));
        const el = g.append("text").attr("font-size", size).attr("font-weight", opts.weight || 700).text(w)
          .attr("fill", hl ? C.volt : (opts.fill || C.ink));
        out.push({ el, x: cx, y: top + li * lh, w: ww, line: li });
        cx += ww + space;
      }
    });
    probe.remove();
    return { list: out, lines: lines.length, lh, top };
  }

  function revealWords(ws, t, start, stagger = 0.06, dist = 50) {
    ws.list.forEach((w, i) => {
      const p = E.out(prog(t, start + i * stagger, 0.55));
      w.el.attr("x", w.x).attr("y", w.y + (1 - p) * dist).attr("opacity", p);
    });
  }

  function pill(g, text, color, size = 30) {
    const grp = g.append("g");
    const r = grp.append("rect").attr("rx", size * 0.9).attr("fill", color);
    const tx = grp.append("text").attr("font-size", size).attr("font-weight", 700).attr("fill", C.bg).text(text)
      .attr("text-anchor", "middle").attr("dominant-baseline", "central");
    const w = tx.node().getComputedTextLength() + size * 1.4, h = size * 1.8;
    r.attr("x", -w / 2).attr("y", -h / 2).attr("width", w).attr("height", h);
    return { g: grp, w, h };
  }

  function heading(g, text, t, start = 0.1) {
    const x0 = W < 1300 ? 90 : 140;
    const ws = words(g, text, x0, 150, W < 1300 ? 52 : 58, W - 2 * x0, { anchor: "start", weight: 700 });
    const top = 150 - ((ws.lines - 1) * ws.lh) / 2;                  // words() centres lines on y; keep the first line at 150
    ws.list.forEach((w) => { w.y += 150 - top; });
    const bar = g.append("rect").attr("x", x0).attr("y", 150 + (ws.lines - 1) * ws.lh + 36).attr("height", 6).attr("rx", 3).attr("fill", C.volt);
    return (t) => { revealWords(ws, t, start, 0.04, 30); bar.attr("width", 120 * E.out(prog(t, start + 0.3, 0.6))); };
  }

  function source(g, text) {
    const el = g.append("text").attr("class", "body").attr("x", W - 140).attr("y", H - 60).attr("text-anchor", "end")
      .attr("font-size", 22).attr("fill", C.muted).text(text ? "Source: " + text : "");
    return (t) => el.attr("opacity", 0.9 * prog(t, 0.8, 0.6));
  }

  // ---- scenes ---------------------------------------------------------------------------------------------------------
  const SCENES = {};

  SCENES.title = (g, s) => {
    const k = s.kicker ? pill(g, s.kicker.toUpperCase(), C.volt, 26) : null;
    const ws = words(g, s.title, W / 2, H / 2, s.size || 120, W - 360, { highlight: (s.highlight || []).map((h) => h.toLowerCase()) });
    const last = ws.list.filter((w) => w.line === ws.lines - 1);
    const ux = last[0].x, uw = last[last.length - 1].x + last[last.length - 1].w - ux, uy = ws.top + (ws.lines - 1) * ws.lh + 34;
    const under = g.append("rect").attr("x", ux).attr("y", uy).attr("height", 12).attr("rx", 6).attr("fill", C.volt).attr("filter", "url(#glow)");
    const sub = s.sub ? g.append("text").attr("class", "body").attr("x", W / 2).attr("y", uy + 110).attr("text-anchor", "middle")
      .attr("font-size", 40).attr("fill", C.muted).text(s.sub) : null;
    return (t) => {
      if (k) { const p = E.back(prog(t, 0, 0.5)); k.g.attr("transform", `translate(${W / 2},${ws.top - 150}) scale(${p})`); }
      revealWords(ws, t, 0.2, 0.08, 80);
      const n = ws.list.length * 0.08 + 0.5;
      under.attr("width", uw * E.inOut(prog(t, n, 0.6)));
      if (sub) sub.attr("opacity", prog(t, n + 0.3, 0.6)).attr("y", uy + 110 + 20 * (1 - E.out(prog(t, n + 0.3, 0.6))));
    };
  };

  SCENES.counter = (g, s) => {
    const cx = W / 2, cy = H / 2 + 30, R = Math.min(390, W * 0.34);
    const ring = g.append("circle").attr("cx", cx).attr("cy", cy).attr("r", R).attr("fill", "none").attr("stroke", C.faint).attr("stroke-width", 14);
    const arc = g.append("path").attr("transform", `translate(${cx},${cy})`).attr("fill", C.volt).attr("filter", "url(#glow)");
    const arcGen = d3.arc().innerRadius(R - 7).outerRadius(R + 7).cornerRadius(7).startAngle(0);
    const label = g.append("text").attr("x", cx).attr("y", cy - 160).attr("text-anchor", "middle").attr("font-size", 38)
      .attr("font-weight", 500).attr("fill", C.muted).text(s.label.toUpperCase()).attr("letter-spacing", 4);
    const num = g.append("text").attr("class", "num").attr("x", cx).attr("y", cy + 70).attr("text-anchor", "middle").attr("font-size", 210);
    const sub = g.append("text").attr("class", "body").attr("x", cx).attr("y", cy + 150).attr("text-anchor", "middle").attr("font-size", 40)
      .attr("fill", C.ink).text(s.sub || "");
    const badge = s.badge ? pill(g, s.badge, s.badgeColor === "coral" ? C.coral : C.volt, 38) : null;
    const src = source(g, s.source);
    const sparks = d3.range(18).map((i) => g.append("circle").attr("r", 4).attr("fill", i % 2 ? C.volt : C.cyan));
    return (t) => {
      const p = E.expo(prog(t, 0.3, 1.8));
      arc.attr("d", arcGen({ endAngle: 2 * Math.PI * (s.ring ?? 0.75) * E.inOut(prog(t, 0.2, 1.9)) }));
      ring.attr("opacity", prog(t, 0, 0.4));
      label.attr("opacity", prog(t, 0.1, 0.5));
      num.text(fmt(lerp(s.from ?? 0, s.value, p), s)).attr("opacity", prog(t, 0.2, 0.3))
        .attr("transform", `translate(${cx},${cy}) scale(${0.85 + 0.15 * E.back(prog(t, 0.2, 0.7))}) translate(${-cx},${-cy})`);
      sub.attr("opacity", prog(t, 1.6, 0.6));
      if (badge) { const b = E.back(prog(t, 2.1, 0.5)); badge.g.attr("transform", W < 1300 ? `translate(${cx},${cy + R + 90}) scale(${b}) rotate(${-4 * b})` : `translate(${cx + R * 0.72 + badge.w / 2},${cy - R * 0.72}) scale(${b}) rotate(${-8 * b})`); }
      const burst = prog(t, 2.0, 1.0);
      sparks.forEach((sp, i) => {
        const a = (i / sparks.length) * 2 * Math.PI, d = R + 30 + 160 * E.out(burst);
        sp.attr("cx", cx + Math.cos(a) * d).attr("cy", cy + Math.sin(a) * d).attr("opacity", burst > 0 && burst < 1 ? 1 - burst : 0);
      });
      src(t);
    };
  };

  SCENES.line = (g, s) => {
    const head = heading(g, s.title);
    const pts = s.series.map(([d, v]) => [new Date(d), v]);
    const narrow = W < 1300;
    const m = narrow ? { l: 150, r: 70, t: 270, b: 130 } : { l: 200, r: 260, t: 270, b: 150 };
    const x = d3.scaleTime().domain(d3.extent(pts, (p) => p[0])).range([m.l, W - m.r]);
    const y = d3.scaleLinear().domain([0, d3.max(pts, (p) => p[1]) * 1.12]).nice().range([H - m.b, m.t]);
    const axis = g.append("g");
    const yt = y.ticks(5).map((v) => ({ v, line: axis.append("line").attr("x1", m.l).attr("x2", W - m.r).attr("y1", y(v)).attr("y2", y(v))
      .attr("stroke", C.faint).attr("stroke-dasharray", "4 8"),
      label: axis.append("text").attr("class", "body").attr("x", m.l - 24).attr("y", y(v) + 9).attr("text-anchor", "end").attr("font-size", 26)
        .attr("fill", C.muted).text(fmt(v, s)) }));
    const years = x.ticks(d3.timeYear.every(s.yearStep || 10)).map((d) => axis.append("text").attr("class", "body").attr("x", x(d))
      .attr("y", H - m.b + 50).attr("text-anchor", "middle").attr("font-size", 26).attr("fill", C.muted).text(d.getFullYear()));
    const clipId = "clip" + Math.random().toString(36).slice(2);
    const clip = g.append("clipPath").attr("id", clipId).append("rect").attr("y", 0).attr("height", H).attr("x", 0);
    const plot = g.append("g").attr("clip-path", `url(#${clipId})`);
    plot.append("path").attr("d", d3.area().x((p) => x(p[0])).y0(y(0)).y1((p) => y(p[1])).curve(d3.curveMonotoneX)(pts)).attr("fill", "url(#area)");
    plot.append("path").attr("d", d3.line().x((p) => x(p[0])).y((p) => y(p[1])).curve(d3.curveMonotoneX)(pts)).attr("fill", "none")
      .attr("stroke", C.volt).attr("stroke-width", 6).attr("stroke-linejoin", "round").attr("filter", "url(#glow)");
    const dot = g.append("circle").attr("r", 12).attr("fill", C.volt).attr("filter", "url(#glow)");
    const halo = g.append("circle").attr("fill", "none").attr("stroke", C.volt).attr("stroke-width", 3);
    const tag = g.append("g"); const tagBg = tag.append("rect").attr("rx", 12).attr("fill", C.ink);
    const tagTx = tag.append("text").attr("class", "num").attr("font-size", 38).attr("fill", C.bg).attr("dominant-baseline", "central");
    const notes = (s.annotations || []).map((a) => {
      const d = new Date(a.date), near = pts.reduce((b, p) => (Math.abs(p[0] - d) < Math.abs(b[0] - d) ? p : b));
      const ng = g.append("g").attr("opacity", 0);
      ng.append("line").attr("x1", x(near[0])).attr("x2", x(near[0])).attr("y1", y(near[1]) - 20).attr("y2", y(near[1]) - 110)
        .attr("stroke", C.coral).attr("stroke-width", 3);
      ng.append("circle").attr("cx", x(near[0])).attr("cy", y(near[1])).attr("r", 10).attr("fill", C.coral);
      const p = pill(ng, a.label, C.coral, 28); p.g.attr("transform", `translate(${Math.min(x(near[0]), W - m.r - p.w / 2 + 120)},${y(near[1]) - 140})`);
      return { g: ng, at: (near[0] - pts[0][0]) / (pts[pts.length - 1][0] - pts[0][0]) };
    });
    const src = source(g, s.source);
    const drawStart = 0.6, drawDur = s.draw || 4.0;
    return (t) => {
      head(t); src(t);
      yt.forEach((k, i) => { const p = prog(t, 0.2 + i * 0.06, 0.5); k.line.attr("opacity", p); k.label.attr("opacity", p); });
      years.forEach((e, i) => e.attr("opacity", prog(t, 0.3 + i * 0.05, 0.5)));
      const p = E.inOut(prog(t, drawStart, drawDur));
      const xx = lerp(m.l, W - m.r, p);
      clip.attr("width", xx + 8);
      const date = x.invert(xx), i = d3.bisector((q) => q[0]).left(pts, date);
      const a = pts[Math.max(0, i - 1)], b = pts[Math.min(pts.length - 1, i)];
      const f = b[0] - a[0] ? (date - a[0]) / (b[0] - a[0]) : 0, v = lerp(a[1], b[1], f);
      const vis = prog(t, drawStart, 0.2);
      dot.attr("cx", xx).attr("cy", y(v)).attr("opacity", vis);
      const pulse = (t * 1.2) % 1;
      halo.attr("cx", xx).attr("cy", y(v)).attr("r", 12 + 30 * pulse).attr("opacity", vis * (1 - pulse));
      tagTx.text(fmt(v, s)); const tw = tagTx.node().getComputedTextLength() + 36;
      tagBg.attr("x", 0).attr("y", -30).attr("width", tw).attr("height", 60);
      tagTx.attr("x", 18);
      tag.attr("transform", `translate(${Math.min(xx + 28, W - tw - 40)},${y(v) - 60})`).attr("opacity", vis);
      notes.forEach((n) => { const q = E.back(prog(p, n.at, 0.06)); n.g.attr("opacity", Math.min(1, q)); });
    };
  };

  SCENES.bars = (g, s) => {
    // Ranked bars. With negative values the bars grow left or right from a zero line (falls in coral).
    const head = heading(g, s.title);
    const items = s.items.slice(0, 10), top = 260, rowH = (H - top - 130) / items.length;
    const lo = Math.min(0, d3.min(items, (d) => d.value)), hi = Math.max(0, d3.max(items, (d) => d.value));
    const X0 = W < 1300 ? 470 : 620, X1 = W < 1300 ? W - 150 : W - 260;
    const x = d3.scaleLinear().domain([lo, hi]).range([X0, X1]);
    const fit = (txt, size, maxW) => {                      // shrink a long label until it fits its column
      const el = g.append("text").attr("font-size", size).attr("font-weight", 600).text(txt);
      while (el.node().getComputedTextLength() > maxW && size > 20) el.attr("font-size", --size);
      el.remove(); return size;
    };
    const zero = lo < 0 ? g.append("line").attr("x1", x(0)).attr("x2", x(0)).attr("y1", top - 10).attr("y2", top + rowH * items.length)
      .attr("stroke", C.muted).attr("stroke-width", 2) : null;
    const rows = items.map((d, i) => {
      const r = g.append("g").attr("transform", `translate(0,${top + i * rowH})`);
      const hot = s.highlight === i, neg = d.value < 0;
      r.append("text").attr("class", "num").attr("x", 170).attr("y", rowH * 0.62).attr("font-size", 30).attr("fill", hot ? C.volt : C.muted)
        .attr("text-anchor", "end").text(i + 1);
      r.append("text").attr("x", 200).attr("y", rowH * 0.62).attr("font-size", fit(d.label, 34, X0 - 240)).attr("font-weight", 600).text(d.label);
      r.append("rect").attr("x", X0).attr("y", rowH * 0.18).attr("height", rowH * 0.64).attr("rx", rowH * 0.18).attr("fill", C.faint)
        .attr("opacity", 0.35).attr("width", X1 - X0);
      const bar = r.append("rect").attr("y", rowH * 0.18).attr("height", rowH * 0.64).attr("rx", rowH * 0.18)
        .attr("fill", neg ? C.coral : hot ? "url(#hot)" : "url(#bar)").attr("filter", hot ? "url(#glow)" : null);
      const val = r.append("text").attr("class", "num").attr("y", rowH * 0.64).attr("font-size", 32).attr("fill", neg ? C.coral : C.ink);
      return { r, bar, val, d, i, neg };
    });
    const src = source(g, s.source);
    return (t) => {
      head(t); src(t);
      if (zero) zero.attr("opacity", prog(t, 0.3, 0.4));
      rows.forEach(({ r, bar, val, d, i, neg }) => {
        const a = prog(t, 0.4 + i * 0.12, 0.4), p = E.expo(prog(t, 0.5 + i * 0.12, 1.4));
        r.attr("opacity", a).attr("transform", `translate(${(1 - E.out(a)) * -60},${top + i * rowH})`);
        const end = x(d.value * p), z = x(0);
        bar.attr("x", Math.min(z, end)).attr("width", Math.max(1, Math.abs(end - z)));
        val.attr("x", neg ? z + 16 : Math.max(z, end) + 16).text(fmt(d.value * p, s));      // a fall's number sits right of the zero line, clear of the names
      });
    };
  };

  SCENES.map = (g, s) => {
    const head = heading(g, s.title);
    const topo = window.__topo.states;
    const feats = topojson.feature(topo, topo.objects.states).features.filter((f) => FIPS[f.id]);
    const vals = Object.values(s.values);
    const color = d3.scaleSequential().domain(d3.extent(vals)).interpolator(d3.interpolateRgbBasis(["#1d2a6b", "#2b6cff", C.cyan, C.volt]));
    const narrow = W < 1300;
    const k = narrow ? (W - 80) / 975 : 1.05, ox = narrow ? 40 : (W - 975 * k) / 2 - 120, oy = narrow ? 300 : 250;
    const cardX = narrow ? 120 : W - 330, cardY = narrow ? oy + 610 * k + 120 : 330;
    const path = d3.geoPath();
    const mapG = g.append("g").attr("transform", `translate(${ox},${oy}) scale(${k})`);
    const xs = feats.map((f) => path.centroid(f)[0]); const [x0, x1] = d3.extent(xs);
    const shapes = feats.map((f, i) => ({ f, st: FIPS[f.id], at: (xs[i] - x0) / (x1 - x0),
      el: mapG.append("path").attr("d", path(f)).attr("stroke", C.bg).attr("stroke-width", 1.5) }));
    const hi = shapes.find((sh) => sh.st === s.highlight);
    const hiOutline = hi ? mapG.append("path").attr("d", path(hi.f)).attr("fill", "none").attr("stroke", C.ink).attr("stroke-width", 4)
      .attr("filter", "url(#glow)") : null;
    const lg = g.append("g").attr("transform", narrow ? `translate(${W - 400},${oy + 610 * k + 60})` : `translate(${W - 420},${H - 360})`);
    const gid = "lg" + Math.random().toString(36).slice(2);
    const lgd = svg.select("defs").append("linearGradient").attr("id", gid);
    ["#1d2a6b", "#2b6cff", C.cyan, C.volt].forEach((c, i) => lgd.append("stop").attr("offset", `${(i / 3) * 100}%`).attr("stop-color", c));
    lg.append("text").attr("class", "body").attr("font-size", 24).attr("fill", C.muted).text(s.legend || "");
    lg.append("rect").attr("y", 20).attr("width", 300).attr("height", 18).attr("rx", 9).attr("fill", `url(#${gid})`);
    lg.append("text").attr("class", "num").attr("y", 74).attr("font-size", 26).text(fmt(d3.min(vals), s));
    lg.append("text").attr("class", "num").attr("x", 300).attr("y", 74).attr("text-anchor", "end").attr("font-size", 26).text(fmt(d3.max(vals), s));
    let call = null;
    if (hi) {
      const [hx, hy] = path.centroid(hi.f);
      call = g.append("g");
      const px = ox + hx * k, py = oy + hy * k;
      call.append("line").attr("x1", px).attr("y1", py).attr("x2", cardX).attr("y2", cardY).attr("stroke", C.ink).attr("stroke-width", 2);
      call.append("circle").attr("cx", px).attr("cy", py).attr("r", 8).attr("fill", C.ink);
      const card = call.append("g").attr("transform", `translate(${cardX},${cardY})`);
      card.append("rect").attr("x", -10).attr("y", -70).attr("width", 300).attr("height", 150).attr("rx", 18).attr("fill", C.bg2).attr("stroke", C.volt);
      card.append("text").attr("x", 20).attr("y", -20).attr("font-size", 30).attr("font-weight", 600).text(s.highlightName || s.highlight);
      card.append("text").attr("class", "num").attr("x", 20).attr("y", 50).attr("font-size", 56).attr("fill", C.volt).text(fmt(s.values[s.highlight], s));
    }
    const src = source(g, s.source);
    return (t) => {
      head(t); src(t);
      shapes.forEach((sh) => {
        const p = E.out(prog(t, 0.5 + sh.at * 1.6, 0.7));
        const v = s.values[sh.st];
        sh.el.attr("fill", v == null ? C.faint : d3.interpolateRgb(C.faint, color(v))(p));
      });
      lg.attr("opacity", prog(t, 1.8, 0.5));
      if (hiOutline) hiOutline.attr("opacity", prog(t, 2.6, 0.4));
      if (call) { const q = E.back(prog(t, 2.8, 0.5)); call.attr("opacity", Math.min(1, q)); }
    };
  };

  SCENES.compare = (g, s) => {
    const head = heading(g, s.title);
    const max = Math.max(s.left.value, s.right.value), base = H - 170, top = 330, hMax = base - top;
    const cols = [[s.left, W / 2 - 330, C.cyan], [s.right, W / 2 + 330, C.volt]].map(([d, cx, col], i) => {
      const bar = g.append("rect").attr("x", cx - 140).attr("width", 280).attr("rx", 24).attr("fill", col).attr("filter", i ? "url(#glow)" : null);
      const num = g.append("text").attr("class", "num").attr("x", cx).attr("text-anchor", "middle").attr("font-size", 96);
      const lab = g.append("text").attr("x", cx).attr("y", base + 70).attr("text-anchor", "middle").attr("font-size", 40).attr("font-weight", 600)
        .text(d.label);
      return { d, bar, num, lab, i };
    });
    const badge = s.verdict ? pill(g, s.verdict, C.coral, 44) : null;
    const src = source(g, s.source);
    return (t) => {
      head(t); src(t);
      cols.forEach(({ d, bar, num, lab, i }) => {
        const p = E.expo(prog(t, 0.6 + i * 0.9, 1.4)), h = (d.value / max) * hMax * p;
        bar.attr("y", base - h).attr("height", Math.max(0, h));
        num.attr("y", base - h - 30).text(fmt(d.value * p, s)).attr("opacity", prog(t, 0.6 + i * 0.9, 0.3));
        lab.attr("opacity", prog(t, 0.4 + i * 0.9, 0.4));
      });
      if (badge) { const b = E.back(prog(t, 3.0, 0.5)); badge.g.attr("transform", `translate(${W / 2},${top + hMax * 0.42}) scale(${b}) rotate(${-6 * b})`); }
    };
  };

  // ======================================================================================================================
  // More chart types. Each reads its numbers from the spec (computed in Python from the data) and lays itself out for a wide
  // frame (1920 x 1080) or a narrow one (a Short's 1080-wide chart area).
  // ======================================================================================================================
  const PAL = [C.volt, C.cyan, C.coral, C.amber, "#b388ff", "#4dffb0", "#ff8ad8", "#8aa4ff", "#ffd966", "#7fe7ff"];
  const rid = () => Math.random().toString(36).slice(2);

  // ---- several lines on one chart -------------------------------------------------------------------------------------
  SCENES.multiline = (g, s) => {
    const head = heading(g, s.title);
    const narrow = W < 1300;
    const legendH = narrow ? 56 * s.lines.length : 0;
    const m = narrow ? { l: 150, r: 70, t: 290 + legendH, b: 190 } : { l: 200, r: 430, t: 270, b: 150 };
    const lines = s.lines.map((l, i) => ({ ...l, color: PAL[i % PAL.length], pts: l.points.map((p) => [new Date(p[0]), p[1]]) }));
    const all = lines.flatMap((l) => l.pts);
    const x = d3.scaleTime().domain(d3.extent(all, (p) => p[0])).range([m.l, W - m.r]);
    const lo = Math.min(0, d3.min(all, (p) => p[1])), hi = d3.max(all, (p) => p[1]);
    const y = d3.scaleLinear().domain([lo, hi + (hi - lo) * 0.08]).nice().range([H - m.b, m.t]);
    const axis = g.append("g");
    const yt = y.ticks(5).map((v) => ({
      line: axis.append("line").attr("x1", m.l).attr("x2", W - m.r).attr("y1", y(v)).attr("y2", y(v)).attr("stroke", v === 0 ? C.muted : C.faint)
        .attr("stroke-dasharray", v === 0 ? null : "4 8"),
      label: axis.append("text").attr("class", "body").attr("x", m.l - 22).attr("y", y(v) + 9).attr("text-anchor", "end").attr("font-size", 26)
        .attr("fill", C.muted).text(fmt(v, s)),
    }));
    const span = x.domain()[1].getFullYear() - x.domain()[0].getFullYear();
    const years = x.ticks(d3.timeYear.every(span <= 8 ? 1 : span <= 16 ? 2 : span <= 40 ? 5 : 10)).map((d) => axis.append("text").attr("class", "body")
      .attr("x", x(d)).attr("y", H - m.b + 48).attr("text-anchor", "middle").attr("font-size", 26).attr("fill", C.muted).text(d.getFullYear()));
    const cid = "clip" + rid();
    const clip = g.append("clipPath").attr("id", cid).append("rect").attr("y", 0).attr("height", H).attr("x", 0);
    const plot = g.append("g").attr("clip-path", `url(#${cid})`);
    lines.forEach((l, i) => {
      l.path = plot.append("path").attr("d", d3.line().x((p) => x(p[0])).y((p) => y(p[1])).curve(d3.curveMonotoneX)(l.pts)).attr("fill", "none")
        .attr("stroke", l.color).attr("stroke-width", i === 0 ? 8 : 5.5).attr("stroke-linejoin", "round").attr("stroke-linecap", "round")
        .attr("filter", i === 0 ? "url(#glow)" : null).attr("opacity", i === 0 ? 1 : 0.92);
      l.dot = g.append("circle").attr("r", 10).attr("fill", l.color).attr("filter", "url(#glow)");
      l.tag = g.append("g");
      if (!narrow) {
        l.tag.append("text").attr("x", 0).attr("y", -2).attr("font-size", 30).attr("font-weight", 700).attr("fill", l.color).text(l.label);
        l.val = l.tag.append("text").attr("class", "num").attr("x", 0).attr("y", 30).attr("font-size", 28).attr("fill", C.ink);
      }
    });
    if (narrow) lines.forEach((l, i) => {
      const r = g.append("g").attr("transform", `translate(${m.l},${300 + i * 56})`);
      r.append("circle").attr("cx", 10).attr("cy", -9).attr("r", 10).attr("fill", l.color);
      l.val = r.append("text").attr("x", 34).attr("font-size", 30).attr("font-weight", 600).attr("fill", C.ink);
      l.legend = l.label;
    });
    const src = source(g, s.source), bis = d3.bisector((q) => q[0]).left;
    const valueAt = (pts, date) => {
      const i = bis(pts, date), a = pts[Math.max(0, i - 1)], b = pts[Math.min(pts.length - 1, i)];
      return lerp(a[1], b[1], b[0] - a[0] ? clamp((date - a[0]) / (b[0] - a[0])) : 0);
    };
    return (t) => {
      head(t); src(t);
      yt.forEach((k, i) => { const p = prog(t, 0.2 + i * 0.06, 0.5); k.line.attr("opacity", p); k.label.attr("opacity", p); });
      years.forEach((e, i) => e.attr("opacity", prog(t, 0.3 + i * 0.05, 0.5)));
      const p = E.inOut(prog(t, 0.6, s.draw || 4.5)), xx = lerp(m.l, W - m.r, p), date = x.invert(xx), vis = prog(t, 0.6, 0.2);
      clip.attr("width", xx + 8);
      const ys = lines.map((l) => { const lim = l.pts[l.pts.length - 1][0]; const v = valueAt(l.pts, date > lim ? lim : date); l.cur = v; return y(v); });
      const order = d3.range(lines.length).sort((a, b) => ys[a] - ys[b]), ly = [];
      order.forEach((k, n) => { ly[k] = Math.max(ys[k], n ? ly[order[n - 1]] + 66 : -1e9); });
      lines.forEach((l, k) => {
        const lim = l.pts[l.pts.length - 1][0], dx = x(date > lim ? lim : date);
        l.dot.attr("cx", dx).attr("cy", ys[k]).attr("opacity", vis);
        if (!narrow) { l.tag.attr("transform", `translate(${dx + 30},${ly[k] + 6})`).attr("opacity", vis); l.val.text(fmt(l.cur, s)); }
        else l.val.text(`${l.legend}   ${fmt(l.cur, s)}`).attr("opacity", vis);
      });
    };
  };

  // ---- ranking race: bars that reorder as time passes ---------------------------------------------------------------------
  SCENES.race = (g, s) => {
    const head = heading(g, s.title);
    const narrow = W < 1300, items = s.items, n = items.length, F = s.frames.length;
    const top = narrow ? 300 : 260, rowH = Math.min(96, (H - top - 150) / n);
    const X0 = narrow ? 400 : 560, X1 = W - (narrow ? 190 : 250);
    const maxV = d3.max(items, (d) => d3.max(d.values));
    const x = d3.scaleLinear().domain([0, maxV * 1.04]).range([0, X1 - X0]);
    const rank = d3.range(F).map((k) => {
      const ord = d3.range(n).sort((a, b) => items[b].values[k] - items[a].values[k]);
      const r = []; ord.forEach((i, pos) => { r[i] = pos; }); return r;
    });
    const rows = items.map((d, i) => {
      const r = g.append("g");
      const lab = r.append("text").attr("x", X0 - 18).attr("y", rowH * 0.62).attr("text-anchor", "end").attr("font-size", narrow ? 30 : 34).attr("font-weight", 600).text(d.label);
      const bar = r.append("rect").attr("x", X0).attr("y", rowH * 0.14).attr("height", rowH * 0.72).attr("rx", rowH * 0.2)
        .attr("fill", PAL[i % PAL.length]).attr("filter", i === s.highlight ? "url(#glow)" : null);
      const val = r.append("text").attr("class", "num").attr("y", rowH * 0.64).attr("font-size", 32);
      return { r, bar, val, lab, i };
    });
    const tick = g.append("text").attr("class", "num").attr("x", W - (narrow ? 70 : 120)).attr("y", H - (narrow ? 90 : 120)).attr("text-anchor", "end")
      .attr("font-size", narrow ? 150 : 220).attr("fill", C.ink).attr("opacity", 0.14);
    const src = source(g, s.source), play = Math.max(1, s.duration - 2.2);
    return (t) => {
      head(t); src(t);
      const pr = prog(t, 0.9, play), yf = pr * (F - 1), k = Math.min(F - 2, Math.floor(yf)), f = yf - k, sm = f * f * (3 - 2 * f);
      tick.text(s.frames[Math.round(yf)]);
      rows.forEach(({ r, bar, val, i }) => {
        const v = lerp(items[i].values[k], items[i].values[k + 1], f), pos = lerp(rank[k][i], rank[k + 1][i], sm), a = prog(t, 0.3 + i * 0.05, 0.4);
        r.attr("transform", `translate(0,${top + pos * rowH})`).attr("opacity", a);
        bar.attr("width", Math.max(2, x(v)));
        val.attr("x", X0 + x(v) + 14).text(fmt(v, s));
      });
    };
  };

  // ---- dumbbell: then and now for many items --------------------------------------------------------------------------------
  SCENES.slope = (g, s) => {
    const head = heading(g, s.title);
    const narrow = W < 1300, items = s.items, n = items.length, top = narrow ? 330 : 300, rowH = Math.min(150, (H - top - 170) / n);
    const X0 = narrow ? 410 : 560, X1 = W - (narrow ? 170 : 230);
    const lo = d3.min(items, (d) => Math.min(d.a, d.b)), hi = d3.max(items, (d) => Math.max(d.a, d.b));
    const x = d3.scaleLinear().domain([Math.max(0, lo - (hi - lo) * 0.08), hi + (hi - lo) * 0.04]).range([X0, X1]);
    const key = g.append("g").attr("transform", `translate(${X0},${top - 50})`);
    key.append("circle").attr("r", 9).attr("fill", C.cyan); key.append("text").attr("x", 20).attr("y", 9).attr("font-size", 26).attr("fill", C.muted).text(s.aLabel);
    key.append("circle").attr("cx", 230).attr("r", 9).attr("fill", C.coral); key.append("text").attr("x", 250).attr("y", 9).attr("font-size", 26).attr("fill", C.muted).text(s.bLabel);
    const rows = items.map((d, i) => {
      const r = g.append("g"), col = d.b >= d.a ? C.coral : C.cyan;
      r.append("text").attr("x", X0 - 28).attr("y", rowH * 0.62).attr("text-anchor", "end").attr("font-size", narrow ? 30 : 34).attr("font-weight", 600).text(d.label);
      r.append("line").attr("x1", X0).attr("x2", X1).attr("y1", rowH / 2).attr("y2", rowH / 2).attr("stroke", C.faint).attr("stroke-dasharray", "3 9");
      const link = r.append("line").attr("y1", rowH / 2).attr("y2", rowH / 2).attr("stroke", col).attr("stroke-width", 8).attr("stroke-linecap", "round");
      const da = r.append("circle").attr("cy", rowH / 2).attr("r", 15).attr("fill", C.cyan);
      const db = r.append("circle").attr("cy", rowH / 2).attr("r", 15).attr("fill", col).attr("filter", "url(#glow)");
      const ta = r.append("text").attr("class", "num").attr("y", rowH / 2 - 26).attr("text-anchor", "middle").attr("font-size", 26).attr("fill", C.muted);
      const tb = r.append("text").attr("class", "num").attr("y", rowH / 2 + 46).attr("text-anchor", "middle").attr("font-size", 28).attr("fill", col);
      return { r, link, da, db, ta, tb, d, i };
    });
    const src = source(g, s.source);
    return (t) => {
      head(t); src(t);
      rows.forEach(({ r, link, da, db, ta, tb, d, i }) => {
        const a = prog(t, 0.4 + i * 0.16, 0.4), p = E.inOut(prog(t, 0.8 + i * 0.16, 0.9)), xa = x(d.a), xb = lerp(xa, x(d.b), p);
        r.attr("transform", `translate(0,${top + i * rowH})`).attr("opacity", a);
        da.attr("cx", xa); db.attr("cx", xb); link.attr("x1", xa).attr("x2", xb);
        ta.attr("x", xa).text(fmt(d.a, s)); tb.attr("x", xb).text(fmt(lerp(d.a, d.b, p), s)).attr("opacity", prog(t, 0.8 + i * 0.16, 0.3));
      });
    };
  };

  // ---- dashboard of big numbers with trend lines ---------------------------------------------------------------------------
  SCENES.kpi = (g, s) => {
    const head = heading(g, s.title);
    const narrow = W < 1300, n = s.cards.length, gap = 36;
    const cw = narrow ? W - 160 : (W - 280 - (n - 1) * gap) / n, ch = narrow ? (H - 470 - (n - 1) * gap) / n : 560;
    const top = narrow ? 300 : (H - ch) / 2 + 40;
    const cards = s.cards.map((c, i) => {
      const gx = narrow ? 80 : 140 + i * (cw + gap), gy = narrow ? top + i * (ch + gap) : top;
      const r = g.append("g").attr("transform", `translate(${gx},${gy})`);
      const col = PAL[i % PAL.length];
      r.append("rect").attr("width", cw).attr("height", ch).attr("rx", 28).attr("fill", C.bg2).attr("stroke", C.faint).attr("stroke-width", 2);
      r.append("rect").attr("x", 28).attr("y", 28).attr("width", 56).attr("height", 8).attr("rx", 4).attr("fill", col);
      const lab = narrow ? 30 : 32;
      r.append("text").attr("class", "body").attr("x", 28).attr("y", 90).attr("font-size", lab).attr("fill", C.muted).text(c.label);
      const size = Math.min(narrow ? 110 : 120, (cw - 56) / (Math.max(4, c.valueText.length) * 0.6));
      const num = r.append("text").attr("class", "num").attr("x", 28).attr("y", narrow ? 195 : 200).attr("font-size", size).attr("fill", C.ink);
      const pillG = r.append("g").attr("transform", `translate(28,${narrow ? 230 : 250})`);
      const tx = pillG.append("text").attr("class", "num").attr("x", 22).attr("y", 33).attr("font-size", 30).attr("font-weight", 700).attr("fill", C.bg).text(c.change);
      pillG.insert("rect", "text").attr("width", tx.node().getComputedTextLength() + 44).attr("height", 50).attr("rx", 25).attr("fill", c.up ? C.coral : C.cyan);
      pillG.append("text").attr("class", "body").attr("x", tx.node().getComputedTextLength() + 64).attr("y", 34).attr("font-size", 24).attr("fill", C.muted).text(c.since);
      const sy0 = narrow ? 320 : 350, sh = ch - sy0 - 36, sw = cw - 56;
      const xs = d3.scaleLinear().domain([0, c.spark.length - 1]).range([0, sw]);
      const ys = d3.scaleLinear().domain(d3.extent(c.spark)).range([sh, 0]);
      const sp = r.append("g").attr("transform", `translate(28,${sy0})`);
      const cidk = "kc" + rid();
      const clipk = sp.append("clipPath").attr("id", cidk).append("rect").attr("x", -10).attr("y", -20).attr("height", sh + 40);
      const spp = sp.append("g").attr("clip-path", `url(#${cidk})`);
      spp.append("path").attr("d", d3.area().x((_, k) => xs(k)).y0(sh).y1((v) => ys(v)).curve(d3.curveMonotoneX)(c.spark)).attr("fill", col).attr("opacity", 0.15);
      spp.append("path").attr("d", d3.line().x((_, k) => xs(k)).y((v) => ys(v)).curve(d3.curveMonotoneX)(c.spark)).attr("fill", "none").attr("stroke", col)
        .attr("stroke-width", 5).attr("stroke-linecap", "round");
      return { r, num, clipk, sw, c, i, gx, gy };
    });
    const src = source(g, s.source);
    return (t) => {
      head(t); src(t);
      cards.forEach(({ r, num, clipk, sw, c, i, gx, gy }) => {
        const a = E.out(prog(t, 0.3 + i * 0.18, 0.6)), p = E.expo(prog(t, 0.5 + i * 0.18, 1.6));
        r.attr("opacity", a).attr("transform", `translate(${gx},${gy + (1 - a) * 50})`);
        num.text(fmt(lerp(0, c.value, p), c));
        clipk.attr("width", sw * E.inOut(prog(t, 0.9 + i * 0.18, 1.8)) + 20);
      });
    };
  };

  // ---- waffle: 100 squares, "x out of 100" ---------------------------------------------------------------------------------
  SCENES.waffle = (g, s) => {
    const narrow = W < 1300, cell = narrow ? 60 : 70, gap = 8, side = 10 * cell + 9 * gap;
    const gx = narrow ? (W - side) / 2 : 190, gy = narrow ? 250 : (H - side) / 2 + 10;
    const filled = Math.max(0, Math.min(100, s.value)), whole = Math.floor(filled), part = filled - whole;
    const sq = d3.range(100).map((i) => {
      const col = i % 10, row = 9 - Math.floor(i / 10);        // fills left to right, bottom to top
      const cx = gx + col * (cell + gap) + cell / 2, cy = gy + row * (cell + gap) + cell / 2;
      return { i, cx, cy, el: g.append("rect").attr("rx", 12).attr("x", -cell / 2).attr("y", -cell / 2).attr("width", cell).attr("height", cell) };
    });
    const tx = narrow ? W / 2 : gx + side + 120, ty = narrow ? gy + side + 150 : H / 2 - 20;
    const anchor = narrow ? "middle" : "start";
    const label = g.append("text").attr("x", tx).attr("y", narrow ? ty - 130 : ty - 150).attr("text-anchor", anchor).attr("font-size", narrow ? 34 : 40)
      .attr("font-weight", 600).attr("fill", C.muted).attr("letter-spacing", 3).text(s.label.toUpperCase());
    const num = g.append("text").attr("class", "num").attr("x", tx).attr("y", ty + (narrow ? 20 : 40)).attr("text-anchor", anchor).attr("font-size", narrow ? 190 : 250).attr("fill", C.volt).attr("filter", "url(#glow)");
    const sub = g.append("text").attr("class", "body").attr("x", tx).attr("y", ty + (narrow ? 110 : 130)).attr("text-anchor", anchor).attr("font-size", narrow ? 38 : 44).attr("fill", C.ink).text(s.sub || "");
    const sub2 = g.append("text").attr("class", "body").attr("x", tx).attr("y", ty + (narrow ? 170 : 200)).attr("text-anchor", anchor).attr("font-size", narrow ? 34 : 40).attr("fill", C.muted).text(s.caption || "");
    const src = source(g, s.source);
    return (t) => {
      src(t);
      const p = E.inOut(prog(t, 0.4, 2.2)), cnt = filled * p;
      sq.forEach((q) => {
        const on = q.i + 1 <= cnt, edge = q.i < cnt && q.i + 1 > cnt, pop = E.back(prog(t, 0.2 + q.i * 0.012, 0.5));
        const fill = on ? C.volt : edge && q.i === whole ? C.volt : C.faint;
        q.el.attr("transform", `translate(${q.cx},${q.cy}) scale(${clamp(pop, 0, 1.15)})`).attr("fill", fill)
          .attr("opacity", on ? 1 : edge && q.i === whole ? 0.25 + 0.75 * part : 0.5);
      });
      label.attr("opacity", prog(t, 0.2, 0.5));
      num.text(fmt(s.value * p, s));
      sub.attr("opacity", prog(t, 1.6, 0.6)); sub2.attr("opacity", prog(t, 2.0, 0.6));
    };
  };

  // ---- gauge: where a rate stands against its own history -----------------------------------------------------------------------
  SCENES.gauge = (g, s) => {
    const narrow = W < 1300, R = Math.min(W * 0.36, 430), cx = W / 2, cy = narrow ? 640 : H * 0.56;
    const head = heading(g, s.title);
    const arc = d3.arc().innerRadius(R - 46).outerRadius(R).cornerRadius(10);
    const band = (a0, a1, col, op) => g.append("path").attr("transform", `translate(${cx},${cy})`).attr("d", arc({ startAngle: a0, endAngle: a1 })).attr("fill", col).attr("opacity", op);
    const A0 = -Math.PI / 2, A1 = Math.PI / 2, third = Math.PI / 3;
    band(A0, A0 + third - 0.02, C.cyan, 0.28); band(A0 + third, A0 + 2 * third - 0.02, C.volt, 0.28); band(A0 + 2 * third, A1, C.coral, 0.28);
    const frac = clamp((s.value - s.min) / ((s.max - s.min) || 1));
    const fillP = g.append("path").attr("transform", `translate(${cx},${cy})`).attr("fill", frac > 0.66 ? C.coral : frac > 0.33 ? C.volt : C.cyan).attr("filter", "url(#glow)");
    const needle = g.append("g").attr("transform", `translate(${cx},${cy})`);
    needle.append("line").attr("y2", -(R - 70)).attr("stroke", C.ink).attr("stroke-width", 10).attr("stroke-linecap", "round");
    needle.append("circle").attr("r", 26).attr("fill", C.ink);
    const ends = g.append("g");
    ends.append("text").attr("class", "num").attr("x", cx - R + 23).attr("y", cy + 70).attr("text-anchor", "middle").attr("font-size", 36).text(fmt(s.min, s));
    ends.append("text").attr("class", "body").attr("x", cx - R + 23).attr("y", cy + 112).attr("text-anchor", "middle").attr("font-size", 26).attr("fill", C.muted).text(s.minLabel);
    ends.append("text").attr("class", "num").attr("x", cx + R - 23).attr("y", cy + 70).attr("text-anchor", "middle").attr("font-size", 36).text(fmt(s.max, s));
    ends.append("text").attr("class", "body").attr("x", cx + R - 23).attr("y", cy + 112).attr("text-anchor", "middle").attr("font-size", 26).attr("fill", C.muted).text(s.maxLabel);
    const num = g.append("text").attr("class", "num").attr("x", cx).attr("y", cy + (narrow ? 250 : 215)).attr("text-anchor", "middle").attr("font-size", narrow ? 170 : 180).attr("fill", C.ink);
    const label = g.append("text").attr("x", cx).attr("y", cy + (narrow ? 330 : 285)).attr("text-anchor", "middle").attr("font-size", narrow ? 38 : 40).attr("fill", C.muted).text(s.label);
    const sub = g.append("text").attr("class", "body").attr("x", cx).attr("y", cy + (narrow ? 390 : 340)).attr("text-anchor", "middle").attr("font-size", narrow ? 32 : 34).attr("fill", C.ink).text(s.sub || "");
    const src = source(g, s.source);
    return (t) => {
      head(t); src(t);
      const p = E.out(prog(t, 0.5, 2.0)), ang = A0 + (A1 - A0) * frac * p;
      fillP.attr("d", arc({ startAngle: A0, endAngle: Math.max(A0 + 0.04, ang) }));
      needle.attr("transform", `translate(${cx},${cy}) rotate(${(ang * 180) / Math.PI})`).attr("opacity", prog(t, 0.3, 0.4));
      ends.attr("opacity", prog(t, 0.3, 0.6));
      num.text(fmt(lerp(s.min, s.value, p), s)).attr("opacity", prog(t, 0.4, 0.4));
      label.attr("opacity", prog(t, 0.8, 0.5)); sub.attr("opacity", prog(t, 2.0, 0.6));
    };
  };

  // ---- donut: how a total splits ---------------------------------------------------------------------------------------------------
  SCENES.donut = (g, s) => {
    const head = heading(g, s.title);
    const narrow = W < 1300, R = narrow ? 270 : 340, r0 = R * 0.62, cx = narrow ? W / 2 : 170 + R + 40, cy = narrow ? 300 + R + 30 : H / 2 + 60;
    const total = d3.sum(s.items, (d) => d.value), arcs = d3.pie().sort(null).value((d) => d.value).padAngle(0.012)(s.items);
    const gen = d3.arc().innerRadius(r0).outerRadius(R).cornerRadius(8);
    const slices = arcs.map((a, i) => ({ a, el: g.append("path").attr("transform", `translate(${cx},${cy})`).attr("fill", PAL[i % PAL.length]), i }));
    const big = s.items.reduce((b, d, i) => (d.value > s.items[b].value ? i : b), 0);
    const cNum = g.append("text").attr("class", "num").attr("x", cx).attr("y", cy + 20).attr("text-anchor", "middle").attr("font-size", narrow ? 100 : 110).attr("fill", PAL[big % PAL.length]);
    let cs = 30; const cLab = g.append("text").attr("x", cx).attr("y", cy + 70).attr("text-anchor", "middle").attr("font-size", cs).attr("fill", C.muted).text(s.items[big].label);
    while (cLab.node().getComputedTextLength() > r0 * 1.7 && cs > 16) cLab.attr("font-size", --cs);
    const lx = narrow ? 120 : cx + R + 140, ly0 = narrow ? cy + R + 70 : cy - (s.items.length * 70) / 2 + 20;
    const leg = s.items.map((d, i) => {
      const r = g.append("g").attr("transform", `translate(${lx},${ly0 + i * (narrow ? 50 : 70)})`);
      r.append("rect").attr("y", -26).attr("width", 28).attr("height", 28).attr("rx", 8).attr("fill", PAL[i % PAL.length]);
      r.append("text").attr("x", 46).attr("font-size", narrow ? 28 : 34).attr("font-weight", 600).text(d.label);
      const v = r.append("text").attr("class", "num").attr("x", narrow ? W - 240 : 640).attr("text-anchor", "end").attr("font-size", narrow ? 28 : 34).attr("fill", PAL[i % PAL.length]);
      return { r, v, d };
    });
    const src = source(g, s.source);
    return (t) => {
      head(t); src(t);
      const p = E.inOut(prog(t, 0.4, 1.8)), sweep = p * 2 * Math.PI;
      slices.forEach(({ a, el }) => el.attr("d", gen({ startAngle: a.startAngle, endAngle: Math.max(a.startAngle, Math.min(a.endAngle, sweep)), padAngle: 0.012 })));
      cNum.text(fmt((s.items[big].value / total) * 100 * p, { decimals: 0, suffix: "%" })).attr("opacity", prog(t, 0.4, 0.4));
      cLab.attr("opacity", prog(t, 1.0, 0.5));
      leg.forEach(({ r, v, d }, i) => { r.attr("opacity", prog(t, 0.6 + i * 0.15, 0.4)); v.text(fmt((d.value / total) * 100 * p, { decimals: 1, suffix: "%" })); });
    };
  };

  // ---- heatmap: a grid of year by month ----------------------------------------------------------------------------------------------
  SCENES.heatmap = (g, s) => {
    const head = heading(g, s.title);
    const narrow = W < 1300, rows = s.rows, n = rows.length;
    const m = narrow ? { l: 130, r: 60, t: 360, b: 170 } : { l: 230, r: 190, t: 300, b: 190 };
    const cw = (W - m.l - m.r) / 12, chh = Math.min(76, (H - m.t - m.b) / n);
    const vmax = s.vmax, color = d3.scaleDiverging().domain([-vmax, 0, vmax]).interpolator(d3.interpolateRgbBasis([C.cyan, "#161b30", C.coral])).clamp(true);
    const months = "JFMAMJJASOND";
    for (let k = 0; k < 12; k++) g.append("text").attr("class", "body").attr("x", m.l + k * cw + cw / 2).attr("y", m.t - 22).attr("text-anchor", "middle")
      .attr("font-size", 28).attr("fill", C.muted).text(narrow ? months[k] : ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][k]);
    const cells = [];
    rows.forEach((row, i) => {
      g.append("text").attr("class", "num").attr("x", m.l - 22).attr("y", m.t + i * chh + chh * 0.66).attr("text-anchor", "end").attr("font-size", Math.min(30, chh * 0.5)).attr("fill", C.muted).text(row.year);
      row.values.forEach((v, k) => {
        if (v === null) return;
        const c = g.append("g").attr("transform", `translate(${m.l + k * cw + cw / 2},${m.t + i * chh + chh / 2})`);
        c.append("rect").attr("x", -cw / 2 + 3).attr("y", -chh / 2 + 3).attr("width", cw - 6).attr("height", chh - 6).attr("rx", 10).attr("fill", color(v));
        if (!narrow && chh >= 44) c.append("text").attr("class", "num").attr("text-anchor", "middle").attr("y", 9).attr("font-size", 24).attr("fill", Math.abs(v) > vmax * 0.55 ? C.bg : C.ink).text(fmt(v, s));
        cells.push({ c, d: (i + k) * 0.035 });
      });
    });
    const lgid = "hl" + rid(), lgd = svg.select("defs").append("linearGradient").attr("id", lgid);
    [-1, 0, 1].forEach((u, i) => lgd.append("stop").attr("offset", `${i * 50}%`).attr("stop-color", color(u * vmax)));
    const lg = g.append("g").attr("transform", `translate(${m.l},${m.t + n * chh + 36})`);
    lg.append("rect").attr("width", 560).attr("height", 18).attr("rx", 9).attr("fill", `url(#${lgid})`);
    lg.append("text").attr("class", "num").attr("y", 56).attr("font-size", 26).attr("fill", C.cyan).text(fmt(-vmax, s));
    lg.append("text").attr("class", "body").attr("x", 280).attr("y", 56).attr("text-anchor", "middle").attr("font-size", 26).attr("fill", C.muted).text(s.legend || "");
    lg.append("text").attr("class", "num").attr("x", 560).attr("y", 56).attr("text-anchor", "end").attr("font-size", 26).attr("fill", C.coral).text("+" + fmt(vmax, s));
    const src = source(g, s.source);
    return (t) => {
      head(t); src(t);
      cells.forEach(({ c, d }) => { const p = E.out(prog(t, 0.4 + d, 0.5)); c.attr("opacity", p).attr("transform-origin", "center"); });
      lg.attr("opacity", prog(t, 1.4, 0.5));
    };
  };

  // ---- world map ----------------------------------------------------------------------------------------------------------------------------
  SCENES.world_map = (g, s) => {
    const head = heading(g, s.title);
    const narrow = W < 1300, topo = window.__topo.world;
    const feats = topojson.feature(topo, topo.objects.countries).features.filter((f) => f.properties.name !== "Antarctica");
    const vals = Object.values(s.values);
    const lo = d3.quantile(vals.sort(d3.ascending), 0.03), hi = d3.quantile(vals, 0.97);
    const color = d3.scaleSequential().domain([lo, hi]).interpolator(d3.interpolateRgbBasis(["#1d2a6b", "#2b6cff", C.cyan, C.volt])).clamp(true);
    const area = narrow ? { x: 30, y: 320, w: W - 60, h: 700 } : { x: 120, y: 250, w: W - 240, h: H - 400 };
    const proj = d3.geoNaturalEarth1().fitExtent([[area.x, area.y], [area.x + area.w, area.y + area.h]], { type: "FeatureCollection", features: feats });
    const path = d3.geoPath(proj), mapG = g.append("g");
    const mapBottom = path.bounds({ type: "FeatureCollection", features: feats })[1][1];
    const xs = feats.map((f) => path.centroid(f)[0]), [x0, x1] = d3.extent(xs.filter((v) => !Number.isNaN(v)));
    const shapes = feats.map((f, i) => ({ f, name: f.properties.name, at: ((xs[i] || x0) - x0) / (x1 - x0), el: mapG.append("path").attr("d", path(f)).attr("stroke", C.bg).attr("stroke-width", 0.7) }));
    const hi_ = shapes.find((sh) => sh.name === s.highlight);
    const out = hi_ ? mapG.append("path").attr("d", path(hi_.f)).attr("fill", "none").attr("stroke", C.ink).attr("stroke-width", 3).attr("filter", "url(#glow)") : null;
    const lgid = "wl" + rid(), lgd = svg.select("defs").append("linearGradient").attr("id", lgid);
    ["#1d2a6b", "#2b6cff", C.cyan, C.volt].forEach((c, i) => lgd.append("stop").attr("offset", `${(i / 3) * 100}%`).attr("stop-color", c));
    const lg = g.append("g").attr("transform", narrow ? `translate(60,${mapBottom + 40})` : `translate(160,${H - 120})`);
    lg.append("text").attr("class", "body").attr("font-size", 24).attr("fill", C.muted).text(s.legend || "");
    lg.append("rect").attr("y", 18).attr("width", 400).attr("height", 18).attr("rx", 9).attr("fill", `url(#${lgid})`);
    lg.append("text").attr("class", "num").attr("y", 72).attr("font-size", 26).text(fmt(lo, s));
    lg.append("text").attr("class", "num").attr("x", 400).attr("y", 72).attr("text-anchor", "end").attr("font-size", 26).text(fmt(hi, s));
    let card = null;
    if (hi_) {
      card = g.append("g").attr("transform", narrow ? `translate(${W - 460},${mapBottom + 30})` : `translate(${W - 560},${H - 250})`);
      card.append("rect").attr("x", 0).attr("y", 0).attr("width", 400).attr("height", 150).attr("rx", 18).attr("fill", C.bg2).attr("stroke", C.volt);
      card.append("text").attr("x", 24).attr("y", 52).attr("font-size", 32).attr("font-weight", 600).text(s.highlightName || s.highlight);
      card.append("text").attr("class", "num").attr("x", 24).attr("y", 120).attr("font-size", 62).attr("fill", C.volt).text(fmt(s.values[s.highlight], s));
    }
    const src = source(g, s.source);
    return (t) => {
      head(t); src(t);
      shapes.forEach((sh) => {
        const p = E.out(prog(t, 0.4 + sh.at * 1.8, 0.7)), v = s.values[sh.name];
        sh.el.attr("fill", v == null ? "#20263d" : d3.interpolateRgb("#20263d", color(v))(p));
      });
      lg.attr("opacity", prog(t, 1.8, 0.5));
      if (out) out.attr("opacity", prog(t, 2.6, 0.4));
      if (card) card.attr("opacity", Math.min(1, E.back(prog(t, 2.8, 0.5))));
    };
  };

  // ---- stacked area: how a total's parts change over time -----------------------------------------------------------------
  SCENES.stacked = (g, s) => {
    const head = heading(g, s.title);
    const narrow = W < 1300, share = s.mode === "share", n = s.layers.length;
    const legendH = narrow ? 52 * n : 0;
    const m = narrow ? { l: 150, r: 60, t: 290 + legendH, b: 190 } : { l: 200, r: 470, t: 270, b: 150 };
    const dates = s.layers[0].points.map((p) => new Date(p[0]));
    const rows = dates.map((d, i) => { const o = { date: d }; s.layers.forEach((l, k) => { o["k" + k] = l.points[i][1]; }); return o; });
    const keys = s.layers.map((_, k) => "k" + k);
    const series = d3.stack().keys(keys).offset(share ? d3.stackOffsetExpand : d3.stackOffsetNone).order(d3.stackOrderNone)(rows);
    const x = d3.scaleTime().domain(d3.extent(dates)).range([m.l, W - m.r]);
    const yMax = share ? 1 : d3.max(series[series.length - 1], (d) => d[1]);
    const y = d3.scaleLinear().domain([0, yMax]).nice().range([H - m.b, m.t]);
    const yfmt = share ? (v) => `${Math.round(v * 100)}%` : (v) => fmt(v, s);
    const axis = g.append("g");
    y.ticks(5).forEach((v) => {
      axis.append("line").attr("x1", m.l).attr("x2", W - m.r).attr("y1", y(v)).attr("y2", y(v)).attr("stroke", C.faint).attr("stroke-dasharray", "4 8");
      axis.append("text").attr("class", "body").attr("x", m.l - 22).attr("y", y(v) + 9).attr("text-anchor", "end").attr("font-size", 26).attr("fill", C.muted).text(yfmt(v));
    });
    const span = dates[dates.length - 1].getFullYear() - dates[0].getFullYear();
    x.ticks(d3.timeYear.every(span <= 8 ? 1 : span <= 16 ? 2 : span <= 40 ? 5 : 10)).forEach((d) => axis.append("text").attr("class", "body")
      .attr("x", x(d)).attr("y", H - m.b + 48).attr("text-anchor", "middle").attr("font-size", 26).attr("fill", C.muted).text(d.getFullYear()));
    const cid = "clip" + rid();
    const clip = g.append("clipPath").attr("id", cid).append("rect").attr("y", 0).attr("height", H).attr("x", 0);
    const plot = g.append("g").attr("clip-path", `url(#${cid})`);
    const area = d3.area().x((d) => x(d.data.date)).y0((d) => y(d[0])).y1((d) => y(d[1])).curve(d3.curveMonotoneX);
    series.forEach((sr, k) => plot.append("path").attr("d", area(sr)).attr("fill", PAL[k % PAL.length]).attr("opacity", 0.88).attr("stroke", C.bg).attr("stroke-width", 2));
    const last = rows.length - 1;
    const labels = series.map((sr, k) => {
      const mid = (sr[last][0] + sr[last][1]) / 2, tot = share ? 1 : yMax;
      const val = share ? sr[last][1] - sr[last][0] : s.layers[k].points[last][1];
      if (narrow) {
        const r = g.append("g").attr("transform", `translate(${m.l},${290 + k * 52})`);
        r.append("rect").attr("y", -24).attr("width", 26).attr("height", 26).attr("rx", 8).attr("fill", PAL[k % PAL.length]);
        r.append("text").attr("x", 40).attr("font-size", 28).attr("font-weight", 600).text(`${s.layers[k].label}  ${share ? Math.round(val * 100) + "%" : fmt(val, s)}`);
        return r;
      }
      const t = g.append("g");
      t.append("text").attr("y", -2).attr("font-size", 28).attr("font-weight", 700).attr("fill", PAL[k % PAL.length]).text(s.layers[k].label);
      t.append("text").attr("class", "num").attr("y", 28).attr("font-size", 26).text(share ? Math.round(val * 100) + "%" : fmt(val, s));
      t.datum({ want: y(mid * (tot / yMax)) });
      return t;
    });
    if (!narrow) {                                           // top to bottom, at least 62 px apart
      const ord = labels.map((l, i) => i).sort((a, b) => labels[a].datum().want - labels[b].datum().want);
      let prev = -1e9;
      ord.forEach((i) => { const yy = Math.max(labels[i].datum().want, prev + 62); labels[i].attr("transform", `translate(${W - m.r + 22},${yy})`); prev = yy; });
    }
    const src = source(g, s.source);
    return (t) => {
      head(t); src(t);
      const p = E.inOut(prog(t, 0.5, s.draw || 3.5));
      clip.attr("width", lerp(m.l, W - m.r, p) + 6);
      labels.forEach((l) => l.attr("opacity", prog(t, 0.5 + (s.draw || 3.5) * 0.8, 0.5)));
    };
  };

  // ---- scatter: two measures against each other, with paths for the highlighted ones ---------------------------------------------
  SCENES.scatter = (g, s) => {
    const head = heading(g, s.title);
    const narrow = W < 1300;
    const m = narrow ? { l: 250, r: 60, t: 300, b: 250 } : { l: 230, r: 130, t: 270, b: 200 };
    const allp = s.points.concat((s.trails || []).flatMap((tr) => tr.pts.map((q) => ({ x: q[0], y: q[1] }))));
    const xs = allp.map((p) => p.x), ys = allp.map((p) => p.y);
    const xlog = !!s.xlog && d3.min(xs) > 0;
    const x = (xlog ? d3.scaleLog() : d3.scaleLinear()).domain([d3.min(xs) * (xlog ? 0.9 : 1), d3.max(xs) * (xlog ? 1.1 : 1.03)]).range([m.l, W - m.r]);
    const y = d3.scaleLinear().domain([d3.min(ys) - (d3.max(ys) - d3.min(ys)) * 0.04, d3.max(ys) + (d3.max(ys) - d3.min(ys)) * 0.04]).range([H - m.b, m.t]);
    const axis = g.append("g");
    y.ticks(5).forEach((v) => {
      axis.append("line").attr("x1", m.l).attr("x2", W - m.r).attr("y1", y(v)).attr("y2", y(v)).attr("stroke", C.faint).attr("stroke-dasharray", "4 8");
      axis.append("text").attr("class", "body").attr("x", m.l - 20).attr("y", y(v) + 9).attr("text-anchor", "end").attr("font-size", 26).attr("fill", C.muted).text(fmt(v, s.yfmt));
    });
    (xlog ? x.ticks(5).filter((v) => (narrow ? [1, 5] : [1, 2, 5]).includes(v / Math.pow(10, Math.floor(Math.log10(v))))) : x.ticks(narrow ? 4 : 6)).forEach((v) => {
      axis.append("line").attr("x1", x(v)).attr("x2", x(v)).attr("y1", m.t).attr("y2", H - m.b).attr("stroke", C.faint).attr("stroke-dasharray", "4 8").attr("opacity", 0.6);
      axis.append("text").attr("class", "body").attr("x", x(v)).attr("y", H - m.b + 44).attr("text-anchor", "middle").attr("font-size", 26).attr("fill", C.muted).text(fmt(v, s.xfmt));
    });
    axis.append("text").attr("x", (m.l + W - m.r) / 2).attr("y", H - m.b + (narrow ? 110 : 100)).attr("text-anchor", "middle").attr("font-size", narrow ? 30 : 34).attr("font-weight", 600).attr("fill", C.cyan).text(s.xLabel + " →");
    axis.append("text").attr("transform", `translate(${narrow ? 60 : 70},${(m.t + H - m.b) / 2}) rotate(-90)`).attr("text-anchor", "middle").attr("font-size", narrow ? 30 : 34)
      .attr("font-weight", 600).attr("fill", C.volt).text(s.yLabel + " →");
    const dots = s.points.map((p, i) => ({ p, i, el: g.append("circle").attr("cx", x(p.x)).attr("cy", y(p.y)).attr("r", p.hi ? 16 : 8).attr("fill", p.hi ? C.volt : C.cyan)
      .attr("opacity", 0).attr("filter", p.hi ? "url(#glow)" : null), at: (x(p.x) - m.l) / (W - m.r - m.l) }));
    const trend = s.trend ? g.append("line").attr("stroke", C.coral).attr("stroke-width", 5).attr("stroke-dasharray", "14 10").attr("stroke-linecap", "round")
      .attr("x1", x(s.trend.x0)).attr("y1", y(s.trend.y0)).attr("opacity", 0.9) : null;
    const trails = (s.trails || []).map((tr, i) => {
      const pts = tr.pts.map((q) => [x(q[0]), y(q[1])]);
      const path = g.append("path").attr("d", d3.line().curve(d3.curveCatmullRom)(pts)).attr("fill", "none").attr("stroke", C.volt).attr("stroke-width", 6).attr("stroke-linecap", "round")
        .attr("opacity", 0.9);
      const len = path.node().getTotalLength();
      path.attr("stroke-dasharray", `${len} ${len}`);
      g.append("circle").attr("cx", pts[0][0]).attr("cy", pts[0][1]).attr("r", 9).attr("fill", C.bg).attr("stroke", C.volt).attr("stroke-width", 4);
      return { path, len, i };
    });
    const hi = dots.filter((d) => d.p.hi), used = [];
    const labels = hi.map((d) => {
      let ly = y(d.p.y) - 24; while (used.some((u) => Math.abs(u - ly) < 34)) ly -= 36;
      used.push(ly);
      const right = x(d.p.x) < W - m.r - 300;
      return { d, el: g.append("text").attr("x", x(d.p.x) + (right ? 26 : -26)).attr("y", ly).attr("text-anchor", right ? "start" : "end").attr("font-size", 30).attr("font-weight", 700)
        .attr("fill", C.ink).attr("paint-order", "stroke").attr("stroke", C.bg).attr("stroke-width", 7).text(d.p.label) };
    });
    const note = s.note ? g.append("text").attr("class", "body").attr("x", m.l + 20).attr("y", m.t + 40).attr("font-size", narrow ? 28 : 32).attr("fill", C.coral).text(s.note) : null;
    const src = source(g, s.source);
    return (t) => {
      head(t); src(t);
      dots.forEach(({ p, el, at }) => el.attr("opacity", p.hi ? E.out(prog(t, 2.2 + at * 0.4, 0.4)) : 0.55 * E.out(prog(t, 0.4 + at * 1.6, 0.5))));
      if (trend) { const q = E.inOut(prog(t, 1.9, 0.9)); trend.attr("x2", lerp(x(s.trend.x0), x(s.trend.x1), q)).attr("y2", lerp(y(s.trend.y0), y(s.trend.y1), q)); }
      trails.forEach(({ path, len, i }) => path.attr("stroke-dashoffset", len * (1 - E.inOut(prog(t, 2.6 + i * 0.25, 1.6)))));
      labels.forEach(({ el }) => el.attr("opacity", prog(t, 2.5, 0.6)));
      if (note) note.attr("opacity", prog(t, 3.0, 0.6));
    };
  };

  // ---- public API -----------------------------------------------------------------------------------------------------
  window.load = async (spec, topo) => {
    if (topo) window.__topo = topo;
    await Promise.all(["500 40px Inter", "700 40px Inter", "500 40px 'Space Grotesk'", "700 40px 'Space Grotesk'"].map((f) => document.fonts.load(f)));
    const [CW, CH] = spec.canvas || [spec.width || 1920, spec.height || 1080];   // the whole picture
    svg = d3.select("#stage").attr("width", CW).attr("height", CH).attr("viewBox", `0 0 ${CW} ${CH}`);
    svg.selectAll("*").remove();
    W = CW; H = CH;
    defs();
    const bg = background(svg);                                                  // the background fills the whole picture
    W = spec.width || CW; H = spec.height || CH;                                 // the scene lays itself out in its own area
    const cam = svg.append("g").attr("transform", `translate(0,${spec.offset || 0})`).append("g"), body = cam.append("g");
    const upd = SCENES[spec.type](body, spec);
    const dur = spec.duration;
    scene = (t) => {
      bg(t);
      const out = E.inOut(prog(t, dur - 0.45, 0.45));                   // every scene leaves the same way: up and fade
      const z = 1 + 0.025 * (t / dur);                                     // a slow push-in keeps still moments alive
      cam.attr("transform", `translate(${W / 2},${H / 2 - out * 60}) scale(${z}) translate(${-W / 2},${-H / 2})`).attr("opacity", 1 - out);
      upd(t);
    };
    await document.fonts.ready;
    scene(0);
    return true;
  };
  window.seek = (t) => { scene(t); return true; };
})();
