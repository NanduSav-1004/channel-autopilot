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
    const n = Math.abs(v) >= 1e6 && s.compact ? (v / 1e6).toFixed(1) + "M"
      : v.toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d });
    return (s.prefix || "") + n + (s.suffix || "");
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
    const ws = words(g, text, 140, 150, 58, W - 280, { anchor: "start", weight: 700 });
    const bar = g.append("rect").attr("x", 140).attr("y", 186).attr("height", 6).attr("rx", 3).attr("fill", C.volt);
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
    const cx = W / 2, cy = H / 2 + 30, R = 390;
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
      if (badge) { const b = E.back(prog(t, 2.1, 0.5)); badge.g.attr("transform", `translate(${cx + R * 0.72 + badge.w / 2},${cy - R * 0.72}) scale(${b}) rotate(${-8 * b})`); }
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
    const m = { l: 200, r: 260, t: 270, b: 150 };
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
    const head = heading(g, s.title);
    const items = s.items.slice(0, 10), top = 260, rowH = (H - top - 130) / items.length;
    const x = d3.scaleLinear().domain([0, d3.max(items, (d) => d.value)]).range([0, W - 760]);
    const rows = items.map((d, i) => {
      const r = g.append("g").attr("transform", `translate(0,${top + i * rowH})`);
      const hot = s.highlight === i;
      r.append("text").attr("class", "num").attr("x", 170).attr("y", rowH * 0.62).attr("font-size", 30).attr("fill", hot ? C.volt : C.muted)
        .attr("text-anchor", "end").text(i + 1);
      r.append("text").attr("x", 200).attr("y", rowH * 0.62).attr("font-size", 34).attr("font-weight", 600).text(d.label);
      r.append("rect").attr("x", 530).attr("y", rowH * 0.18).attr("height", rowH * 0.64).attr("rx", rowH * 0.18).attr("fill", C.faint).attr("opacity", 0.45)
        .attr("width", x(x.domain()[1]));
      const bar = r.append("rect").attr("x", 530).attr("y", rowH * 0.18).attr("height", rowH * 0.64).attr("rx", rowH * 0.18)
        .attr("fill", hot ? "url(#hot)" : "url(#bar)").attr("filter", hot ? "url(#glow)" : null);
      const val = r.append("text").attr("class", "num").attr("y", rowH * 0.64).attr("font-size", 32);
      return { r, bar, val, d, i };
    });
    const src = source(g, s.source);
    return (t) => {
      head(t); src(t);
      rows.forEach(({ r, bar, val, d, i }) => {
        const a = prog(t, 0.4 + i * 0.12, 0.4), p = E.expo(prog(t, 0.5 + i * 0.12, 1.4));
        r.attr("opacity", a).attr("transform", `translate(${(1 - E.out(a)) * -60},${top + i * rowH})`);
        bar.attr("width", Math.max(1, x(d.value) * p));
        val.attr("x", 530 + x(d.value) * p + 20).text(fmt(d.value * p, s));
      });
    };
  };

  SCENES.map = (g, s) => {
    const head = heading(g, s.title);
    const topo = window.__topo.states;
    const feats = topojson.feature(topo, topo.objects.states).features.filter((f) => FIPS[f.id]);
    const vals = Object.values(s.values);
    const color = d3.scaleSequential().domain(d3.extent(vals)).interpolator(d3.interpolateRgbBasis(["#1d2a6b", "#2b6cff", C.cyan, C.volt]));
    const k = 1.05, ox = (W - 975 * k) / 2 - 120, oy = 250;
    const path = d3.geoPath();
    const mapG = g.append("g").attr("transform", `translate(${ox},${oy}) scale(${k})`);
    const xs = feats.map((f) => path.centroid(f)[0]); const [x0, x1] = d3.extent(xs);
    const shapes = feats.map((f, i) => ({ f, st: FIPS[f.id], at: (xs[i] - x0) / (x1 - x0),
      el: mapG.append("path").attr("d", path(f)).attr("stroke", C.bg).attr("stroke-width", 1.5) }));
    const hi = shapes.find((sh) => sh.st === s.highlight);
    const hiOutline = hi ? mapG.append("path").attr("d", path(hi.f)).attr("fill", "none").attr("stroke", C.ink).attr("stroke-width", 4)
      .attr("filter", "url(#glow)") : null;
    const lg = g.append("g").attr("transform", `translate(${W - 420},${H - 360})`);
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
      call.append("line").attr("x1", px).attr("y1", py).attr("x2", W - 330).attr("y2", 330).attr("stroke", C.ink).attr("stroke-width", 2);
      call.append("circle").attr("cx", px).attr("cy", py).attr("r", 8).attr("fill", C.ink);
      const card = call.append("g").attr("transform", `translate(${W - 330},330)`);
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

  // ---- public API -----------------------------------------------------------------------------------------------------
  window.load = async (spec, topo) => {
    if (topo) window.__topo = topo;
    await Promise.all(["500 40px Inter", "700 40px Inter", "500 40px 'Space Grotesk'", "700 40px 'Space Grotesk'"].map((f) => document.fonts.load(f)));
    W = spec.width || 1920; H = spec.height || 1080;
    svg = d3.select("#stage").attr("width", W).attr("height", H).attr("viewBox", `0 0 ${W} ${H}`);
    svg.selectAll("*").remove();
    defs();
    const bg = background(svg);
    const cam = svg.append("g"), body = cam.append("g");
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
