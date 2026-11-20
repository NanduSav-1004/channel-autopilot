// Science Chaya scene kit: animated explainers for Kerala (cut-aways, maps, machines, counters), laid out for wide (16:9) and tall (9:16) pictures.
// A video is one "chaya" scene: spec.scenes = [{t0, t1, kind, p}] (times in seconds, from the narration) and spec.cards = [{t0, t1, ml, en, col}].
(() => {
  const M = window.MOTION, d3 = window.d3, { SCENES, E, prog, clamp, lerp, rid } = M;
  const K = {};
  const P = { cream: "#f7ecd9", brown: "#7b4a2b", dark: "#4a2a17", amber: "#e8a33d", leaf: "#2f7d4f", leaf2: "#1f7344", sea: "#1f8aa8", seaDeep: "#146a85", sky1: "#bfe3f2", sky2: "#eaf6fb",
    rock: "#8a6a45", rock2: "#5a4029", sand: "#c9a35e", red: "#c8442f", steel: "#8d99a6", steel2: "#5e6b78", gold: "#f6b945", ink: "#2a1a10" };
  const MAL = '"Noto Sans Malayalam", "Space Grotesk", sans-serif';
  const rnd = (n) => { const v = Math.sin(n * 127.1 + 311.7) * 43758.5453; return v - Math.floor(v); };
  const line = d3.line(), smooth = d3.line().curve(d3.curveCatmullRom), basis = d3.line().curve(d3.curveBasis);
  const frac = (lt, d) => clamp(lt / Math.max(0.001, d));
  const at = (a, key, dflt = 9) => (a && a[key] != null ? a[key] : dflt);           // when (as a fraction of the scene) something starts
  const fit = (node, size, maxW, min = 14) => { let s = size; node.attr("font-size", s); while (node.node().getComputedTextLength() > maxW && s > min) node.attr("font-size", --s); return s; };

  function pill(g, text, en, x, y, col, w = 360, size = 46) {
    const grp = g.append("g").attr("transform", `translate(${x},${y})`);
    const h = en ? size * 1.9 : size * 1.5;
    grp.append("rect").attr("x", -w / 2).attr("y", -h / 2).attr("width", w).attr("height", h).attr("rx", h / 2.6).attr("fill", col).attr("opacity", 0.96);
    const t = grp.append("text").attr("y", en ? -size * 0.02 : size * 0.35).attr("text-anchor", "middle").attr("fill", "#fff").attr("font-weight", 800).attr("font-family", MAL).text(text);
    fit(t, size, w - 40, 16);
    if (en) { const e = grp.append("text").attr("y", size * 0.72).attr("text-anchor", "middle").attr("fill", "#fff").attr("fill-opacity", 0.85).attr("font-weight", 600).attr("letter-spacing", 2).text(en); fit(e, size * 0.5, w - 40, 11); }
    return grp;
  }

  // ---- icons: each draws into a group, centred on 0,0, about 100 units across ----
  const ICON = {
    dam: (g) => { g.append("path").attr("d", "M -50 -40 L 20 -40 L 36 44 L -50 44 Z").attr("fill", P.steel); g.append("path").attr("d", "M -50 -40 L -50 44 L -62 44 L -62 -40 Z").attr("fill", P.seaDeep);
      g.append("path").attr("d", "M -50 -22 Q -20 -30 20 -22 L 24 -10 Q -20 -18 -50 -10 Z").attr("fill", "#fff").attr("opacity", 0.25); },
    turbine: (g) => { g.append("circle").attr("r", 40).attr("fill", P.steel2); for (let i = 0; i < 8; i++) g.append("path").attr("d", "M 0 -40 Q 14 -54 22 -40 L 6 -22 Z").attr("fill", P.gold).attr("transform", `rotate(${i * 45})`); g.append("circle").attr("r", 10).attr("fill", P.dark); },
    generator: (g) => { g.append("rect").attr("x", -48).attr("y", -34).attr("width", 96).attr("height", 68).attr("rx", 14).attr("fill", P.steel2); g.append("circle").attr("r", 22).attr("fill", P.cream); g.append("path").attr("d", "M -14 6 L 0 -16 L 14 6 Z").attr("fill", P.amber); },
    transformer: (g) => { g.append("rect").attr("x", -40).attr("y", -42).attr("width", 80).attr("height", 84).attr("rx", 6).attr("fill", P.steel); for (const x of [-18, 18]) for (let y = -30; y < 30; y += 11) g.append("ellipse").attr("cx", x).attr("cy", y).attr("rx", 16).attr("ry", 4).attr("fill", P.amber); },
    pylon: (g) => { g.append("path").attr("d", "M 0 -52 L -26 50 M 0 -52 L 26 50 M -16 -4 L 16 -4 M -22 22 L 22 22 M -10 -30 L 12 22 M 10 -30 L -12 22").attr("stroke", P.dark).attr("stroke-width", 7).attr("fill", "none").attr("stroke-linecap", "round");
      g.append("path").attr("d", "M -42 -36 L 42 -36 M -34 -16 L 34 -16").attr("stroke", P.dark).attr("stroke-width", 7).attr("stroke-linecap", "round"); },
    pole: (g) => { g.append("rect").attr("x", -5).attr("y", -52).attr("width", 10).attr("height", 104).attr("fill", P.brown); g.append("rect").attr("x", -30).attr("y", -40).attr("width", 60).attr("height", 8).attr("fill", P.brown);
      g.append("rect").attr("x", -16).attr("y", -20).attr("width", 32).attr("height", 24).attr("rx", 5).attr("fill", P.steel2); },
    house: (g) => { g.append("path").attr("d", "M -48 -4 L 0 -48 L 48 -4 Z").attr("fill", P.red); g.append("rect").attr("x", -38).attr("y", -4).attr("width", 76).attr("height", 52).attr("fill", P.cream); g.append("rect").attr("x", -9).attr("y", 14).attr("width", 18).attr("height", 34).attr("fill", P.brown); g.append("rect").attr("x", 14).attr("y", 6).attr("width", 16).attr("height", 16).attr("fill", P.gold); },
    meter: (g) => { g.append("rect").attr("x", -34).attr("y", -44).attr("width", 68).attr("height", 88).attr("rx", 10).attr("fill", P.cream).attr("stroke", P.dark).attr("stroke-width", 6);
      g.append("rect").attr("x", -24).attr("y", -30).attr("width", 48).attr("height", 22).attr("rx", 4).attr("fill", P.dark); g.append("circle").attr("cy", 20).attr("r", 14).attr("fill", "none").attr("stroke", P.dark).attr("stroke-width", 5); g.append("path").attr("d", "M 0 20 L 8 12").attr("stroke", P.red).attr("stroke-width", 4); },
    bulb: (g) => { g.append("circle").attr("cy", -10).attr("r", 30).attr("fill", P.gold); g.append("rect").attr("x", -14).attr("y", 16).attr("width", 28).attr("height", 22).attr("rx", 5).attr("fill", P.steel2); },
    cloud: (g) => { for (const [x, y, r] of [[-22, 6, 24], [4, -10, 30], [30, 6, 22]]) g.append("circle").attr("cx", x).attr("cy", y).attr("r", r).attr("fill", "#fff"); g.append("rect").attr("x", -44).attr("y", 6).attr("width", 88).attr("height", 22).attr("fill", "#fff"); },
    drop: (g) => { g.append("path").attr("d", "M 0 -46 Q 34 4 28 22 Q 22 44 0 44 Q -22 44 -28 22 Q -34 4 0 -46 Z").attr("fill", P.sea); },
    sun: (g) => { g.append("circle").attr("r", 26).attr("fill", P.gold); for (let i = 0; i < 10; i++) g.append("rect").attr("x", -4).attr("y", -52).attr("width", 8).attr("height", 18).attr("rx", 4).attr("fill", P.gold).attr("transform", `rotate(${i * 36})`); },
    mountain: (g) => { g.append("path").attr("d", "M -54 40 L -8 -40 L 18 4 L 32 -18 L 56 40 Z").attr("fill", P.leaf); g.append("path").attr("d", "M -8 -40 L 4 -18 L -8 -10 L -20 -18 Z").attr("fill", "#fff").attr("opacity", 0.9); },
    bolt: (g) => { g.append("path").attr("d", "M 8 -50 L -26 6 L -2 6 L -10 50 L 28 -8 L 4 -8 Z").attr("fill", P.gold).attr("stroke", P.dark).attr("stroke-width", 4).attr("stroke-linejoin", "round"); },
    cup: (g) => { g.append("path").attr("d", "M -34 -30 L 34 -30 L 26 38 Q 25 46 16 46 L -16 46 Q -25 46 -26 38 Z").attr("fill", P.amber).attr("stroke", P.dark).attr("stroke-width", 5); },
    fan: (g) => { g.append("circle").attr("r", 8).attr("fill", P.dark); for (let i = 0; i < 3; i++) g.append("ellipse").attr("cx", 0).attr("cy", -26).attr("rx", 11).attr("ry", 24).attr("fill", P.steel2).attr("transform", `rotate(${i * 120})`); },
    ac: (g) => { g.append("rect").attr("x", -48).attr("y", -22).attr("width", 96).attr("height", 44).attr("rx", 10).attr("fill", P.cream).attr("stroke", P.dark).attr("stroke-width", 5); for (let i = -2; i <= 2; i++) g.append("line").attr("x1", i * 16 - 6).attr("x2", i * 16 + 6).attr("y1", 8).attr("y2", 8).attr("stroke", P.steel2).attr("stroke-width", 4); },
    led: (g) => { g.append("path").attr("d", "M -24 -8 A 26 26 0 1 1 24 -8 L 14 20 L -14 20 Z").attr("fill", "#fff3b0").attr("stroke", P.dark).attr("stroke-width", 4); g.append("rect").attr("x", -12).attr("y", 22).attr("width", 24).attr("height", 18).attr("rx", 4).attr("fill", P.steel2); },
    bird: (g) => { g.append("ellipse").attr("rx", 34).attr("ry", 22).attr("fill", "#2b2b34"); g.append("circle").attr("cx", 30).attr("cy", -16).attr("r", 16).attr("fill", "#2b2b34"); g.append("path").attr("d", "M 44 -16 L 62 -10 L 44 -8 Z").attr("fill", P.gold); g.append("circle").attr("cx", 34).attr("cy", -20).attr("r", 3.5).attr("fill", "#fff"); g.append("path").attr("d", "M -34 -4 L -62 12 L -30 12 Z").attr("fill", "#2b2b34"); g.append("path").attr("d", "M -6 20 L -6 40 M 10 20 L 10 40").attr("stroke", P.gold).attr("stroke-width", 5).attr("stroke-linecap", "round"); },
  };
  const icon = (g, name, x, y, size = 100, col) => { const grp = g.append("g").attr("transform", `translate(${x},${y}) scale(${size / 100})`); ICON[name](grp); return grp; };
  M.chayaIcon = icon;

  // ---- the stage: where the picture goes (below the cards) and how big things are ----
  function terrainY(TER, x) { for (let i = 1; i < TER.length; i++) if (x <= TER[i][0]) { const [x0, y0] = TER[i - 1], [x1, y1] = TER[i]; return lerp(y0, y1, (x - x0) / (x1 - x0)); } return TER[TER.length - 1][1]; }
  Object.assign(M, { P, MAL, rnd, line, smooth, basis, frac, at, fit, pill, terrainY, K });

  // ================= terrain: the cut-away of Kerala (sea, coast, the Ghats, the dry side) with wind, cloud, rain, rivers, soil =================
  // p.at = fractions of the scene when each part starts: heat, wind, cool, cloud, rain, shadow, river, ground, lapse. p.zoom = {cx, cy, s, at, dur}. p.tags = [{u, v, ml, en, at, col}]
  K.terrain = (g, p, c) => {
    const { X, Y, S } = c, a = p.at || {}, id = c.id + rid();
    const defs = M.svg.select("defs");
    const sky = defs.append("linearGradient").attr("id", id + "sky").attr("x1", 0).attr("y1", 0).attr("x2", 0).attr("y2", 1);
    sky.append("stop").attr("offset", "0%").attr("stop-color", P.sky1); sky.append("stop").attr("offset", "100%").attr("stop-color", P.sky2);
    const rock = defs.append("linearGradient").attr("id", id + "rock").attr("x1", 0).attr("y1", 0).attr("x2", 0).attr("y2", 1);
    rock.append("stop").attr("offset", "0%").attr("stop-color", P.rock); rock.append("stop").attr("offset", "100%").attr("stop-color", P.rock2);
    const hill = defs.append("linearGradient").attr("id", id + "hill").attr("x1", 0).attr("y1", 0).attr("x2", 1).attr("y2", 0);
    hill.append("stop").attr("offset", "0%").attr("stop-color", "#3f9a5f"); hill.append("stop").attr("offset", "58%").attr("stop-color", P.leaf); hill.append("stop").attr("offset", "100%").attr("stop-color", P.sand);
    const inner = g.append("g");
    const gray = d3.interpolateRgb("#ffffff", "#9aa6b2");
    const TER = [[0.31, 0.80], [0.50, 0.79], [0.64, 0.55], [0.73, 0.36], [0.78, 0.21], [0.855, 0.34], [1.0, 0.64]].map(([u, v]) => [X(u), Y(v)]);
    const ty = (x) => terrainY(TER, x), sea0 = Y(0.80), BOT = Y(0.985), top = c.stage.y, W0 = c.stage.x, W1 = c.stage.x + c.stage.w;
    inner.append("rect").attr("x", W0 - 40).attr("y", top).attr("width", c.stage.w + 80).attr("height", sea0 - top + 4).attr("fill", `url(#${id}sky)`);
    const storm = inner.append("rect").attr("x", W0 - 40).attr("y", top).attr("width", c.stage.w + 80).attr("height", sea0 - top).attr("fill", "#5f7487").attr("opacity", 0);
    // sun and drifting clouds
    const sun = inner.append("g").attr("transform", `translate(${X(0.90)},${Y(0.10)}) scale(${S})`);
    const rays = sun.append("g"); for (let i = 0; i < 14; i++) rays.append("rect").attr("x", -9).attr("y", -150).attr("width", 18).attr("height", 52).attr("rx", 9).attr("fill", P.gold).attr("transform", `rotate(${i * 360 / 14})`);
    const disc = sun.append("circle").attr("r", 82).attr("fill", "#f9c74f"); sun.append("circle").attr("r", 58).attr("fill", "#fbd978");
    const drift = [0, 1, 2].map((k) => { const cg = inner.append("g"); [[0, 0, 34], [34, -14, 42], [76, 0, 34]].forEach(([x, y, r]) => cg.append("circle").attr("cx", x).attr("cy", y).attr("r", r * S).attr("fill", "#fff").attr("opacity", 0.85)); return cg; });
    // sea
    const seaG = inner.append("g");
    seaG.append("rect").attr("x", W0 - 40).attr("y", sea0).attr("width", X(0.31) - W0 + 50).attr("height", BOT - sea0).attr("fill", P.seaDeep);
    const waves = [0, 1, 2].map((k) => seaG.append("path").attr("fill", k === 0 ? P.sea : k === 1 ? "#3aa3c0" : "#6bbdd3").attr("opacity", k === 0 ? 1 : 0.7));
    // land: rock, windward green to dry sand, soil layers
    inner.append("path").attr("d", line([[X(0.31), BOT], ...TER, [W1 + 40, TER[TER.length - 1][1]], [W1 + 40, BOT]]) + "Z").attr("fill", `url(#${id}rock)`);
    inner.append("path").attr("d", line([...TER, [W1 + 40, TER[TER.length - 1][1] + 70 * S], ...TER.slice().reverse().map(([x, y]) => [x, y + 70 * S])]) + "Z").attr("fill", `url(#${id}hill)`);
    for (const [dy, col] of [[150, "#7a5a38"], [260, "#6b4d31"]]) inner.append("path").attr("d", line(TER.map(([x, y]) => [x, y + dy * S]).concat([[W1 + 40, BOT], [X(0.31), BOT]])) + "Z").attr("fill", col).attr("opacity", 0.55);
    for (let i = 0; i < 24; i++) {
      const x = X(0.32) + i * (X(0.86) - X(0.32)) / 24 + rnd(i) * 8 * S, y = ty(x), dry = x > X(0.88), h = ((dry ? 40 : 70) + rnd(i + 9) * 34) * S;
      const tr = inner.append("g").attr("transform", `translate(${x},${y + 4})`);
      tr.append("rect").attr("x", -3 * S).attr("y", -h * 0.35).attr("width", 6 * S).attr("height", h * 0.4).attr("fill", "#5b3a1f");
      tr.append("circle").attr("cy", -h * (dry ? 0.5 : 0.62)).attr("r", h * (dry ? 0.32 : 0.45)).attr("fill", dry ? "#a8934d" : (i % 2 ? "#2c8a52" : "#1f7344"));
    }
    for (let i = 0; i < 9; i++) { const x = X(0.90) + i * (X(1.0) - X(0.90)) / 9, y = ty(x); inner.append("path").attr("d", `M ${x - 14 * S} ${y + 14 * S} l ${10 * S} ${-8 * S} l ${8 * S} ${6 * S} l ${10 * S} ${-10 * S}`).attr("fill", "none").attr("stroke", "#8a6a3a").attr("stroke-width", 4 * S).attr("opacity", 0.8); }  // cracks on the dry side
    // river down the windward slope into the sea
    const RIV = [[0.70, 0.40], [0.665, 0.50], [0.63, 0.60], [0.56, 0.72], [0.46, 0.775], [0.36, 0.795]].map(([u, v]) => [X(u), Y(v)]);
    const river = inner.append("path").attr("d", smooth(RIV)).attr("fill", "none").attr("stroke", "#3aa3c0").attr("stroke-width", 9 * S).attr("stroke-linecap", "round").attr("opacity", 0);
    const riverFlow = inner.append("path").attr("d", smooth(RIV)).attr("fill", "none").attr("stroke", "#fff").attr("stroke-width", 4 * S).attr("stroke-dasharray", `${14 * S} ${30 * S}`).attr("opacity", 0);
    // heat shimmer
    const heat = [0, 1, 2].map(() => inner.append("path").attr("fill", "none").attr("stroke", "#e8793d").attr("stroke-width", 7 * S).attr("stroke-linecap", "round").attr("opacity", 0));
    // the wind and its moisture
    const WIND = [[-0.04, 0.74], [0.15, 0.72], [0.40, 0.68], [0.56, 0.58], [0.67, 0.42], [0.74, 0.24], [0.82, 0.12], [0.93, 0.14], [1.05, 0.26]].map(([u, v]) => [X(u), Y(v)]);
    const wp = inner.append("path").attr("d", smooth(WIND)).attr("fill", "none"), WL = wp.node().getTotalLength();
    const wpts = Array.from({ length: 400 }, (_, i) => { const q = wp.node().getPointAtLength((i / 399) * WL); return [q.x, q.y]; }); wp.remove();
    const streaks = [-46, -16, 14, 44].map((dy) => inner.append("path").attr("fill", "none").attr("stroke", "#fff").attr("stroke-width", 7 * S).attr("stroke-linecap", "round").attr("stroke-dasharray", `${46 * S} ${90 * S}`).attr("d", smooth(WIND.slice(0, 7).map(([x, y]) => [x, y + dy * S]))));
    const NP = 90, parts = Array.from({ length: NP }, (_, i) => ({ off: i / NP, jy: (rnd(i + 3) - 0.5) * 110 * S, r: (8 + rnd(i + 5) * 9) * S, sp: 0.8 + rnd(i + 1) * 0.5 }));
    const dots = parts.map(() => inner.append("circle").attr("opacity", 0));
    const arrow = inner.append("g").attr("opacity", 0);
    arrow.append("path").attr("d", "M -90 0 L 90 0 M 50 -36 L 100 0 L 50 36").attr("fill", "none").attr("stroke", P.seaDeep).attr("stroke-width", 14).attr("stroke-linecap", "round").attr("stroke-linejoin", "round");
    // the dry air coming down the far side, warming as it sinks
    const SINK = [[0.83, 0.13], [0.90, 0.22], [0.96, 0.34], [1.02, 0.46]].map(([u, v]) => [X(u), Y(v)]);
    const sinkG = inner.append("path").attr("d", smooth(SINK)).attr("fill", "none").attr("stroke", "#e8793d").attr("stroke-width", 12 * S).attr("stroke-linecap", "round").attr("stroke-dasharray", `${28 * S} ${24 * S}`).attr("opacity", 0);
    // cloud and rain
    const CL = [[0, 0, 62], [58, -28, 74], [126, -6, 64], [188, 12, 52], [-58, 16, 50], [34, 38, 58], [100, 42, 56]];
    const cloud = inner.append("g"); const blobs = CL.map(([x, y, r]) => cloud.append("circle").attr("cx", x).attr("cy", y).attr("r", r).attr("fill", "#fff"));
    const NR = 170, drops = Array.from({ length: NR }, (_, i) => ({ x: X(0.58) + rnd(i + 20) * (X(0.79) - X(0.58)), ph: rnd(i + 40), sp: 1.1 + rnd(i + 60) * 0.7, len: (26 + rnd(i + 80) * 22) * S }));
    const rain = drops.map(() => inner.append("line").attr("stroke", "#2d7fb8").attr("stroke-width", 5 * S).attr("stroke-linecap", "round").attr("opacity", 0));
    const ground = [0, 1, 2, 3].map((k) => inner.append("path").attr("d", "M 0 0 L 0 34 M -9 22 L 0 36 L 9 22").attr("fill", "none").attr("stroke", "#5fb4e6").attr("stroke-width", 6 * S).attr("stroke-linecap", "round").attr("opacity", 0));
    // thermometers up the slope (the air cools as it climbs)
    const lapse = [[0.52, 0.64, "30°C"], [0.60, 0.50, "24°C"], [0.67, 0.35, "18°C"]].map(([u, v, txt]) => { const t = pill(inner, txt, null, X(u) - 70 * S, Y(v), "#c45a2a", 130 * S, 34 * S); t.attr("opacity", 0); return t; });
    const tags = (p.tags || []).map((tg) => { const t = pill(inner, tg.ml, tg.en, X(tg.u), Y(tg.v), tg.col || P.brown, (tg.w || 340) * S, 34 * S); t.attr("opacity", 0); return { t, at: tg.at || 0 }; });
    const waveP = (k, t) => { const pts = []; for (let x = W0 - 20; x <= X(0.32) + 5; x += 18) pts.push([x, sea0 + 5 + k * 18 * S + Math.sin(x / 38 + t * (1.6 + k * 0.5) + k) * (11 - k * 2) * S]); return basis(pts) + `L${X(0.32) + 5},${BOT}L${W0 - 20},${BOT}Z`; };
    return (lt, d) => {
      const f = lt / d, z = p.zoom, zk = z ? E.inOut(prog(f, z.at || 0, z.dur || 0.4)) : 0;
      if (z) { const tx = X(z.cx), tyy = Y(z.cy), s = 1 + (z.s - 1) * zk; inner.attr("transform", `translate(${tx},${tyy}) scale(${s}) translate(${-tx},${-tyy})`); }
      const heatOn = prog(f, at(a, "heat"), 0.06), windOn = prog(f, at(a, "wind"), 0.06), coolOn = prog(f, at(a, "cool"), 0.06), cloudG = E.out(prog(f, at(a, "cloud"), 0.12)), rainOn = prog(f, at(a, "rain"), 0.08), shadowOn = prog(f, at(a, "shadow"), 0.08);
      const dark = rainOn * (1 - 0.6 * shadowOn);
      storm.attr("opacity", 0.38 * dark); sun.attr("opacity", 1 - 0.55 * dark); rays.attr("transform", `rotate(${lt * 14})`); disc.attr("r", 82 + 6 * Math.sin(lt * 2) + 12 * heatOn + 8 * shadowOn);
      waves.forEach((w, k) => w.attr("d", waveP(k, lt)));
      drift.forEach((cg, k) => cg.attr("transform", `translate(${(((lt * (14 + k * 6) + k * 420) % (c.stage.w + 340)) - 170) + W0},${Y(0.10 + 0.13 * k)})`).attr("opacity", 1 - 0.7 * dark));
      heat.forEach((q, k) => { const pts = []; for (let y = 0; y <= 150; y += 15) pts.push([X(0.38 + k * 0.045) + Math.sin(y / 14 + lt * 4 + k) * 14 * S, Y(0.76) - y * S - ((lt * 60 + k * 50) % 70) * S]); q.attr("d", basis(pts)).attr("opacity", 0.55 * heatOn * (1 - windOn * 0.6)); });
      arrow.attr("opacity", 0.85 * windOn * (1 - coolOn)).attr("transform", `translate(${X(0.10) + 40 * Math.sin(lt * 3)},${Y(0.65)}) scale(${1.4 * S})`);
      streaks.forEach((q, k) => q.attr("stroke-dashoffset", -lt * 90 - k * 30).attr("opacity", 0.55 * windOn * (1 - coolOn * 0.7)));
      parts.forEach((q, i) => { const raw = (lt - d * at(a, "wind", 9)) * 0.075 * q.sp + q.off, u = ((raw % 1) + 1) % 1, pt = wpts[Math.floor(u * 399)], cool = prog(u, 0.5, 0.25);
        dots[i].attr("cx", pt[0]).attr("cy", pt[1] + q.jy * (1 - 0.6 * u)).attr("r", q.r * (1 + 0.5 * coolOn * cool)).attr("opacity", windOn * (u > 0.02 ? 1 : 0) * (0.9 - 0.5 * shadowOn * cool)).attr("fill", d3.interpolateRgb("#4fb3e0", "#ffffff")(cool)); });
      lapse.forEach((t, i) => t.attr("opacity", prog(f, at(a, "lapse") + i * 0.04, 0.05)));
      cloud.attr("transform", `translate(${X(0.60) + 6 * Math.sin(lt * 1.3)},${Y(0.16) - 8 * Math.sin(lt * 1.7)}) scale(${(0.15 + 1.3 * cloudG) * S})`).attr("opacity", clamp(cloudG * 3) * (1 - 0.65 * shadowOn));
      blobs.forEach((b) => b.attr("fill", gray(0.85 * rainOn)));
      const rI = rainOn * (1 - 0.15 * shadowOn);
      drops.forEach((q, i) => { const tp = Y(0.24), bt = ty(q.x) - 4, u = (lt * q.sp * 0.9 + q.ph) % 1, y = lerp(tp, bt, u); rain[i].attr("x1", q.x - 6 * S).attr("y1", y).attr("x2", q.x - 14 * S).attr("y2", y + q.len).attr("opacity", i / NR < rI ? 0.85 * (u < 0.96 ? 1 : 0.2) : 0); });
      const gOn = prog(f, at(a, "ground"), 0.08);
      ground.forEach((q, k) => { const x = X(0.58 + k * 0.045), y = ty(x) + (60 + 40 * k) * S + ((lt * 40 + k * 20) % 40) * S; q.attr("transform", `translate(${x},${y}) scale(${S})`).attr("opacity", 0.9 * gOn * (1 - ((lt * 40 + k * 20) % 40) / 40 * 0.6)); });
      const rv = prog(f, at(a, "river"), 0.08);
      river.attr("opacity", 0.9 * rv); riverFlow.attr("opacity", 0.8 * rv).attr("stroke-dashoffset", -lt * 60);
      sinkG.attr("opacity", 0.9 * shadowOn).attr("stroke-dashoffset", -lt * 50).attr("stroke", d3.interpolateRgb("#4fb3e0", "#e8793d")(0.5 + 0.5 * Math.sin(lt)));
      tags.forEach((tg) => tg.t.attr("opacity", prog(f, tg.at, 0.05)));
    };
  };

  // ================= map: Kerala and its neighbours (Natural Earth, public domain), with pins, arrows and shading =================
  // p: pins [{lon, lat, ml, en, at, col, side}], arrows (true), shade: "rain"|"dry"|null, ridge (true), at: {arrows, shade, ridge}
  const PLACES = { tvm: [76.94, 8.52], kochi: [76.27, 9.93], munnar: [77.06, 10.09], marayoor: [77.16, 10.27], idukki: [76.97, 9.84], moolamattom: [76.88, 9.80], kozhikode: [75.78, 11.26], palakkad: [76.65, 10.78], anamudi: [77.06, 10.17] };
  K.map = (g, p, c) => {
    const { X, Y, S } = c, a = p.at || {}, topo = window.__topo.kerala;
    const wide = c.wide, box = wide ? { x: X(0.30), y: Y(0.01), w: X(0.70) - X(0.30), h: Y(0.99) - Y(0.01) } : { x: X(0.10), y: Y(0.02), w: X(0.90) - X(0.10), h: Y(0.98) - Y(0.02) };
    const lon0 = 74.2, lon1 = 78.4, lat0 = 7.9, lat1 = 13.1, kx = Math.cos(10.5 * Math.PI / 180);
    const sc = Math.min(box.w / ((lon1 - lon0) * kx), box.h / (lat1 - lat0));
    const ox = box.x + (box.w - (lon1 - lon0) * kx * sc) / 2, oy = box.y + (box.h - (lat1 - lat0) * sc) / 2;
    const proj = ([lo, la]) => [ox + (lo - lon0) * kx * sc, oy + (lat1 - la) * sc];
    const ring = (r) => line(r.map(proj)) + "Z";
    const gid = c.id + rid();
    g.append("rect").attr("x", box.x - 80 * S).attr("y", box.y).attr("width", box.w + 160 * S).attr("height", box.h).attr("rx", 40 * S).attr("fill", "#cfe9f3").attr("opacity", 0.55);
    for (const nm of ["Karnataka", "Tamil Nadu"]) topo[nm].rings.forEach((r) => g.append("path").attr("d", ring(r)).attr("fill", nm === "Tamil Nadu" ? "#e9dcb8" : "#dfe8cf").attr("stroke", "#fff").attr("stroke-width", 3 * S));
    const tn = g.append("g"), dryShade = [];
    topo["Tamil Nadu"].rings.forEach((r) => dryShade.push(tn.append("path").attr("d", ring(r)).attr("fill", "#d9a441").attr("opacity", 0)));
    const defs = M.svg.select("defs"), cp = defs.append("clipPath").attr("id", gid + "cp"); topo.Kerala.rings.forEach((r) => cp.append("path").attr("d", ring(r)));
    topo.Kerala.rings.forEach((r) => g.append("path").attr("d", ring(r)).attr("fill", "#8fcf9f").attr("stroke", P.leaf2).attr("stroke-width", 5 * S));
    const kg = g.append("g").attr("clip-path", `url(#${gid}cp)`);
    const bx0 = ox + (74.8 - lon0) * kx * sc, bx1 = ox + (77.5 - lon0) * kx * sc;
    const rainRect = kg.append("rect").attr("x", bx0).attr("y", oy).attr("width", (bx1 - bx0)).attr("height", (lat1 - lat0) * sc).attr("fill", "#3b8fcf").attr("opacity", 0);
    // the ridge of the Ghats: the east edge of Kerala
    const east = []; for (let la = 8.3; la <= 12.75; la += 0.12) { let best = null; for (const [lo, l2] of topo.Kerala.rings[0]) if (Math.abs(l2 - la) < 0.07 && (best === null || lo > best)) best = lo; if (best) east.push(proj([best, la])); }
    const ridge = g.append("path").attr("d", smooth(east)).attr("fill", "none").attr("stroke", P.dark).attr("stroke-width", 10 * S).attr("stroke-linecap", "round").attr("stroke-dasharray", `${18 * S} ${12 * S}`).attr("opacity", 0);
    // monsoon arrows from the south-west
    const arrows = [0, 1, 2].map((k) => { const x = box.x + 0.02 * box.w + k * 0.10 * box.w, y = oy + (lat1 - 8.6 - k * 1.6) * sc; const ag = g.append("g").attr("opacity", 0); ag.append("path").attr("d", "M -70 40 L 40 -26 M 6 -40 L 48 -30 L 34 10").attr("fill", "none").attr("stroke", P.seaDeep).attr("stroke-width", 12).attr("stroke-linecap", "round").attr("stroke-linejoin", "round"); return { ag, x, y }; });
    const pins = (p.pins || []).map((pn) => { const [x, y] = proj(pn.lon != null ? [pn.lon, pn.lat] : PLACES[pn.id]); const pg = g.append("g").attr("opacity", 0);
      pg.append("circle").attr("cx", x).attr("cy", y).attr("r", 11 * S).attr("fill", pn.col || P.red).attr("stroke", "#fff").attr("stroke-width", 4 * S);
      const side = pn.side || (wide ? 1 : 1), lw = (pn.w || 250) * S, lx = x + side * (22 * S + lw / 2);
      pill(pg, pn.ml, pn.en, lx, y - 4 * S, pn.col || P.brown, lw, 30 * S);
      return { pg, at: pn.at || 0 }; });
    return (lt, d) => {
      const f = lt / d, aOn = prog(f, at(a, "arrows"), 0.06), sOn = prog(f, at(a, "shade"), 0.1), rOn = prog(f, at(a, "ridge"), 0.06);
      arrows.forEach((q, k) => q.ag.attr("opacity", aOn * (0.55 + 0.45 * Math.sin(lt * 3 - k))).attr("transform", `translate(${q.x + 24 * Math.sin(lt * 2 - k)},${q.y - 16 * Math.sin(lt * 2 - k)}) scale(${S * 1.3})`));
      rainRect.attr("opacity", p.shade === "rain" ? 0.45 * sOn : 0);
      dryShade.forEach((q) => q.attr("opacity", p.shade === "dry" ? 0.75 * sOn : 0));
      ridge.attr("opacity", rOn).attr("stroke-dashoffset", -lt * 20);
      pins.forEach((q) => q.pg.attr("opacity", prog(f, q.at, 0.05)));
    };
  };

  // ================= stat: one big counting number =================
  // p: value, decimals, prefix, suffix, ml, en (label), icon, col, note
  K.stat = (g, p, c) => {
    const { X, Y } = c, S = c.S * (c.wide ? 1.35 : 1), wide = c.wide, cx = X(0.5), cy = Y(wide ? 0.45 : 0.42), col = p.col || P.brown;
    const ring = g.append("circle").attr("cx", cx).attr("cy", cy).attr("r", 330 * S).attr("fill", "none").attr("stroke", col).attr("stroke-width", 16 * S).attr("opacity", 0.18);
    const arc = g.append("path").attr("transform", `translate(${cx},${cy})`).attr("fill", col);
    const gen = d3.arc().innerRadius(322 * S).outerRadius(338 * S).cornerRadius(8 * S).startAngle(0);
    if (p.icon) icon(g, p.icon, cx, cy - 215 * S, 110 * S);
    const num = g.append("text").attr("class", "num").attr("x", cx).attr("y", cy + 60 * S).attr("text-anchor", "middle").attr("fill", P.ink).attr("font-weight", 700);
    const ml = g.append("text").attr("x", cx).attr("y", cy + 150 * S).attr("text-anchor", "middle").attr("fill", P.brown).attr("font-family", MAL).attr("font-weight", 800).text(p.ml || "");
    fit(ml, 58 * S, 560 * S); const en = g.append("text").attr("x", cx).attr("y", cy + 200 * S).attr("text-anchor", "middle").attr("fill", P.brown).attr("fill-opacity", 0.75).attr("font-weight", 600).attr("letter-spacing", 3).text(p.en || ""); fit(en, 30 * S, 560 * S, 12);
    const f0 = (v) => (p.prefix || "") + v.toLocaleString("en-US", { minimumFractionDigits: p.decimals || 0, maximumFractionDigits: p.decimals || 0 }) + (p.suffix || "");
    fit(num.text(f0(p.value)), 200 * S, 560 * S, 40);
    const size = parseFloat(num.attr("font-size"));
    return (lt, d) => {
      const k = E.out(prog(lt, 0.15, Math.min(1.8, d * 0.5)));
      arc.attr("d", gen.endAngle(k * Math.PI * 2 * (p.fill == null ? 1 : p.fill))());
      num.text(f0(p.value * k)).attr("font-size", size).attr("opacity", clamp(lt / 0.2));
      ring.attr("opacity", 0.18 + 0.05 * Math.sin(lt * 3));
    };
  };

  // ================= bars: animated comparison =================
  // p: items [{ml, en, v, col}], unit, max, decimals
  K.bars = (g, p, c) => {
    const { X, Y, S } = c, items = p.items, n = items.length, wide = c.wide, x0 = X(wide ? 0.12 : 0.08), x1 = X(wide ? 0.88 : 0.92), top = Y(0.08), rowH = (Y(0.92) - top) / n, mx = p.max || Math.max(...items.map((i) => i.v)) * 1.1;
    const lw = (wide ? 360 : 230) * S;
    const rows = items.map((it, i) => {
      const y = top + i * rowH, r = g.append("g").attr("opacity", 0);
      const lab = r.append("text").attr("x", x0).attr("y", y + rowH * 0.5).attr("fill", P.brown).attr("font-family", MAL).attr("font-weight", 800).text(it.ml); fit(lab, 46 * S, lw - 20, 14);
      if (it.en) { const e = r.append("text").attr("x", x0).attr("y", y + rowH * 0.5 + 30 * S).attr("fill", P.brown).attr("fill-opacity", 0.7).attr("font-weight", 600).attr("letter-spacing", 2).text(it.en); fit(e, 24 * S, lw - 20, 10); }
      r.append("rect").attr("x", x0 + lw).attr("y", y + rowH * 0.18).attr("width", x1 - x0 - lw).attr("height", rowH * 0.64).attr("rx", rowH * 0.2).attr("fill", P.brown).attr("opacity", 0.1);
      const bar = r.append("rect").attr("x", x0 + lw).attr("y", y + rowH * 0.18).attr("height", rowH * 0.64).attr("rx", rowH * 0.2).attr("fill", it.col || P.sea);
      const val = r.append("text").attr("class", "num").attr("y", y + rowH * 0.62).attr("fill", P.ink).attr("font-weight", 700).attr("font-size", 44 * S);
      return { r, bar, val, it };
    });
    return (lt, d) => rows.forEach((q, i) => {
      const k = E.out(prog(lt, 0.2 + i * 0.35, 1.1)), w = (x1 - x0 - lw) * (q.it.v / mx);
      q.r.attr("opacity", clamp(k * 3)); q.bar.attr("width", w * k);
      q.val.attr("x", x0 + lw + Math.min(w * k + 14 * S, x1 - x0 - lw - 150 * S)).text((q.it.v * k).toLocaleString("en-US", { maximumFractionDigits: p.decimals || 0 }) + (p.unit ? " " + p.unit : ""));
    });
  };

  // ================= flow: a chain of machines, lit one after another, with charge moving along it =================
  // p: nodes [{icon, ml, en}], carry: "water"|"charge"
  K.flow = (g, p, c) => {
    const { X, Y } = c, S = c.S * (c.wide ? 1.35 : 1), nodes = p.nodes, n = nodes.length, wide = c.wide;
    const pos = nodes.map((_, i) => wide ? [X(0.08 + (0.84 * i) / (n - 1)), Y(0.42)] : [X(0.5 + (i % 2 ? 0.22 : -0.22)), Y(0.07 + (0.86 * i) / (n - 1))]);
    const path = g.append("path").attr("d", smooth(pos)).attr("fill", "none").attr("stroke", p.carry === "water" ? P.sea : P.amber).attr("stroke-width", 12 * S).attr("stroke-linecap", "round").attr("opacity", 0.35);
    const node = path.node(), L = node.getTotalLength();
    const dots = Array.from({ length: 22 }, () => g.append("circle").attr("r", 10 * S).attr("fill", p.carry === "water" ? "#7fd0ee" : P.gold));
    const items = nodes.map((nd, i) => { const gg = g.append("g").attr("opacity", 0.25);
      gg.append("circle").attr("cx", pos[i][0]).attr("cy", pos[i][1]).attr("r", 74 * S).attr("fill", "#fffaf0").attr("stroke", P.brown).attr("stroke-width", 6 * S);
      icon(gg, nd.icon, pos[i][0], pos[i][1], 100 * S);
      const t = gg.append("text").attr("x", pos[i][0]).attr("y", pos[i][1] + (wide ? 135 : 125) * S).attr("text-anchor", "middle").attr("fill", P.brown).attr("font-family", MAL).attr("font-weight", 800).text(nd.ml); fit(t, 38 * S, (wide ? 280 : 360) * S, 14);
      if (nd.en) { const e = gg.append("text").attr("x", pos[i][0]).attr("y", pos[i][1] + (wide ? 135 : 125) * S + 30 * S).attr("text-anchor", "middle").attr("fill", P.brown).attr("fill-opacity", 0.7).attr("font-weight", 600).attr("letter-spacing", 2).text(nd.en); fit(e, 22 * S, (wide ? 280 : 360) * S, 9); }
      return gg; });
    return (lt, d) => {
      const lit = lt / d * (n + 0.6);
      items.forEach((gg, i) => gg.attr("opacity", 0.25 + 0.75 * E.out(clamp(lit - i))));
      dots.forEach((dt, i) => { const u = (((lt * 0.12 + i / dots.length) % 1) + 1) % 1, pt = node.getPointAtLength(u * L); dt.attr("cx", pt.x).attr("cy", pt.y).attr("opacity", u * (n + 0.6) / 1 < lit ? 1 : 0); });
    };
  };

  // ================= generator: a magnet turning inside a coil makes a current (Faraday) =================
  K.generator = (g, p, c) => {
    const { X, Y } = c, S = c.S * (c.wide ? 1.35 : 1), cx = X(0.5), cy = Y(c.wide ? 0.48 : 0.40), R = 190 * S;
    g.append("rect").attr("x", cx - R * 1.9).attr("y", cy - R * 1.25).attr("width", R * 3.8).attr("height", R * 2.5).attr("rx", 40 * S).attr("fill", P.steel2).attr("opacity", 0.18);
    const coilL = g.append("g"), coilR = g.append("g");
    for (const [gg, sx] of [[coilL, -1], [coilR, 1]]) for (let i = 0; i < 7; i++) gg.append("ellipse").attr("cx", cx + sx * (R * 1.45)).attr("cy", cy - R * 0.9 + i * R * 0.3).attr("rx", R * 0.28).attr("ry", R * 0.1).attr("fill", "none").attr("stroke", P.amber).attr("stroke-width", 12 * S);
    const rotor = g.append("g").attr("transform", `translate(${cx},${cy})`);
    rotor.append("path").attr("d", `M ${-R * 0.34} ${-R} L ${R * 0.34} ${-R} L ${R * 0.34} 0 L ${-R * 0.34} 0 Z`).attr("fill", P.red);
    rotor.append("path").attr("d", `M ${-R * 0.34} 0 L ${R * 0.34} 0 L ${R * 0.34} ${R} L ${-R * 0.34} ${R} Z`).attr("fill", P.seaDeep);
    rotor.append("text").attr("y", -R * 0.45).attr("text-anchor", "middle").attr("fill", "#fff").attr("font-size", 70 * S).attr("font-weight", 800).text("N");
    rotor.append("text").attr("y", R * 0.62).attr("text-anchor", "middle").attr("fill", "#fff").attr("font-size", 70 * S).attr("font-weight", 800).text("S");
    const fieldLines = [0, 1, 2].map((k) => g.append("ellipse").attr("cx", cx).attr("cy", cy).attr("rx", R * (1.0 + k * 0.32)).attr("ry", R * (0.62 + k * 0.2)).attr("fill", "none").attr("stroke", P.sea).attr("stroke-width", 4 * S).attr("stroke-dasharray", `${10 * S} ${14 * S}`).attr("opacity", 0.55));
    // wire out to a bulb
    const bx = X(c.wide ? 0.86 : 0.5), by = c.wide ? cy : Y(0.80);
    const wire = g.append("path").attr("d", c.wide ? `M ${cx + R * 1.73} ${cy - R * 0.9} L ${bx - 70 * S} ${cy - R * 0.9} L ${bx - 70 * S} ${by - 40 * S}` : `M ${cx + R * 1.73} ${cy - R * 0.9} L ${cx + R * 2.0} ${cy - R * 0.9} L ${cx + R * 2.0} ${by - 40 * S} L ${bx + 70 * S} ${by - 40 * S}`).attr("fill", "none").attr("stroke", P.dark).attr("stroke-width", 7 * S);
    const glow = g.append("circle").attr("cx", bx).attr("cy", by - 10 * S).attr("r", 90 * S).attr("fill", P.gold).attr("opacity", 0);
    icon(g, "bulb", bx, by, 120 * S);
    const dots = Array.from({ length: 10 }, () => g.append("circle").attr("r", 9 * S).attr("fill", P.gold));
    const wn = wire.node(), L = wn.getTotalLength();
    return (lt, d) => {
      const spin = lt * (p.speed || 2.4), ang = spin * 360 / (2 * Math.PI) * 0.9;
      rotor.attr("transform", `translate(${cx},${cy}) rotate(${ang})`);
      const emf = Math.sin(spin * 2), on = prog(lt, 0.6, 0.8);
      fieldLines.forEach((q, k) => q.attr("stroke-dashoffset", -lt * (30 + k * 10) * Math.sign(emf || 1)).attr("transform", `rotate(${ang * 0.5} ${cx} ${cy})`));
      glow.attr("opacity", 0.55 * on * (0.5 + 0.5 * Math.abs(emf)));
      dots.forEach((q, i) => { const u = (((i / dots.length + emf * lt * 0.4) % 1) + 1) % 1, pt = wn.getPointAtLength(u * L); q.attr("cx", pt.x).attr("cy", pt.y).attr("opacity", on); });
    };
  };

  // ================= transformer: few turns -> many turns, high voltage and low current =================
  K.transformer = (g, p, c) => {
    const { X, Y } = c, S = c.S * (c.wide ? 1.35 : 1), cx = X(0.5), cy = Y(c.wide ? 0.46 : 0.40), w = 520 * S, h = 380 * S;
    g.append("rect").attr("x", cx - w / 2).attr("y", cy - h / 2).attr("width", w).attr("height", h).attr("rx", 30 * S).attr("fill", P.steel).attr("opacity", 0.9);
    g.append("rect").attr("x", cx - w / 2 + 90 * S).attr("y", cy - h / 2 + 80 * S).attr("width", w - 180 * S).attr("height", h - 160 * S).attr("rx", 14 * S).attr("fill", P.cream);
    const coil = (x, n, col) => { for (let i = 0; i < n; i++) g.append("ellipse").attr("cx", x).attr("cy", cy - h / 2 + 100 * S + i * ((h - 200 * S) / Math.max(1, n - 1))).attr("rx", 64 * S).attr("ry", 9 * S).attr("fill", "none").attr("stroke", col).attr("stroke-width", 9 * S); };
    coil(cx - w / 2 + 45 * S, p.nIn || 4, P.sea); coil(cx + w / 2 - 45 * S, p.nOut || 16, P.red);
    const mk = (x, y, txt, col) => { const t = g.append("text").attr("x", x).attr("y", y).attr("text-anchor", "middle").attr("fill", col).attr("font-weight", 800).attr("font-family", MAL).text(txt); fit(t, 52 * S, 300 * S, 16); return t; };
    mk(cx - w / 2 - 100 * S, cy - h / 2 - 20 * S, p.inLabel || "കുറഞ്ഞ വോൾട്ടേജ്", P.seaDeep); mk(cx + w / 2 + 100 * S, cy - h / 2 - 20 * S, p.outLabel || "ഉയർന്ന വോൾട്ടേജ്", P.red);
    const flux = Array.from({ length: 12 }, () => g.append("circle").attr("r", 8 * S).attr("fill", P.amber));
    const inA = g.append("path").attr("d", `M ${cx - w / 2 - 200 * S} ${cy} L ${cx - w / 2 - 40 * S} ${cy}`).attr("stroke", P.seaDeep).attr("stroke-width", 22 * S).attr("stroke-linecap", "round");
    const outA = g.append("path").attr("d", `M ${cx + w / 2 + 40 * S} ${cy} L ${cx + w / 2 + 200 * S} ${cy}`).attr("stroke", P.red).attr("stroke-width", 6 * S).attr("stroke-linecap", "round");
    const bigI = mk(cx - w / 2 - 190 * S, cy + 70 * S, p.inI || "വലിയ കറന്റ്", P.seaDeep), smallI = mk(cx + w / 2 + 190 * S, cy + 70 * S, p.outI || "ചെറിയ കറന്റ്", P.red);
    void bigI; void smallI;
    return (lt, d) => { flux.forEach((q, i) => { const u = (lt * 0.35 + i / 12) % 1, ang = u * Math.PI * 2, rx = (w - 180 * S) / 2, ry = (h - 160 * S) / 2; q.attr("cx", cx + rx * Math.cos(ang)).attr("cy", cy + ry * Math.sin(ang)).attr("opacity", 0.9); });
      inA.attr("opacity", 0.6 + 0.4 * Math.sin(lt * 8)); outA.attr("opacity", 0.6 + 0.4 * Math.sin(lt * 8)); };
  };

  // ================= dam: reservoir, the tunnel through the rock, and the turbine in the underground power house =================
  K.dam = (g, p, c) => {
    const { X, Y, S } = c, wide = c.wide, id = c.id + rid();
    const rock = g.append("rect").attr("x", X(0)).attr("y", Y(0.30)).attr("width", c.stage.w).attr("height", Y(0.99) - Y(0.30)).attr("fill", P.rock).attr("opacity", 0.9);
    g.append("path").attr("d", line([[X(0), Y(0.30)], [X(0.30), Y(0.28)], [X(0.46), Y(0.34)], [X(1), Y(0.30)], [X(1), Y(0.36)], [X(0), Y(0.36)]]) + "Z").attr("fill", P.leaf);
    const lvl = (f) => Y(0.30 - 0.12 * f);
    const res = g.append("path").attr("fill", P.sea).attr("opacity", 0.95);
    g.append("path").attr("d", line([[X(0.30), Y(0.14)], [X(0.38), Y(0.14)], [X(0.43), Y(0.60)], [X(0.28), Y(0.60)]]) + "Z").attr("fill", P.steel).attr("stroke", P.steel2).attr("stroke-width", 5 * S);
    const tag = (u, v, ml, en, col) => pill(g, ml, en, X(u), Y(v), col || P.brown, 330 * S, 32 * S);
    tag(0.34, 0.05, p.hMl || "169 മീറ്റർ ഉയരം", p.hEn || "DAM HEIGHT", P.brown);
    const tun = [[0.34, 0.50], [0.42, 0.64], [0.60, 0.70], [0.76, 0.76]].map(([u, v]) => [X(u), Y(v)]);
    g.append("path").attr("d", smooth(tun)).attr("fill", "none").attr("stroke", P.dark).attr("stroke-width", 34 * S).attr("stroke-linecap", "round").attr("opacity", 0.55);
    const flow = g.append("path").attr("d", smooth(tun)).attr("fill", "none").attr("stroke", "#7fd0ee").attr("stroke-width", 18 * S).attr("stroke-linecap", "round").attr("stroke-dasharray", `${30 * S} ${26 * S}`);
    g.append("rect").attr("x", X(0.70)).attr("y", Y(0.70)).attr("width", X(0.26) - X(0)).attr("height", Y(0.27) - Y(0)).attr("rx", 40 * S).attr("fill", "#3a2a1c");
    const tw = g.append("g").attr("transform", `translate(${X(0.78)},${Y(0.83)}) scale(${1.35 * S})`); ICON.turbine(tw);
    const gen = g.append("g").attr("transform", `translate(${X(0.90)},${Y(0.83)}) scale(${1.1 * S})`); ICON.generator(gen);
    const jets = Array.from({ length: 14 }, () => g.append("circle").attr("r", 8 * S).attr("fill", "#9fe0f5"));
    tag(0.83, 0.64, p.pMl || "ഭൂഗർഭ പവർഹൗസ്", p.pEn || "UNDERGROUND POWER HOUSE", P.dark);
    return (lt, d) => { const f = lt / d, w = lvl(1 - 0.05 * f); res.attr("d", line([[X(0), w], [X(0.30), w], [X(0.30), Y(0.60)], [X(0), Y(0.60)]]) + "Z");
      flow.attr("stroke-dashoffset", -lt * 120); tw.attr("transform", `translate(${X(0.78)},${Y(0.83)}) scale(${1.35 * S}) rotate(${lt * 260})`);
      jets.forEach((q, i) => { const u = (lt * 0.8 + i / 14) % 1; q.attr("cx", X(0.72) + u * (X(0.78) - X(0.72)) + 12 * S * Math.sin(i)).attr("cy", Y(0.76) + u * (Y(0.83) - Y(0.76))).attr("opacity", 1 - u * 0.6); }); };
  };

  // ================= meter: units, and how long common things take to use one =================
  K.meter = (g, p, c) => {
    const { X, Y, S } = c, wide = c.wide, items = p.items || [], n = items.length;
    const mx = X(wide ? 0.20 : 0.5), my = wide ? Y(0.5) : Y(0.16);
    icon(g, "meter", mx, my, (wide ? 330 : 230) * S);
    const digits = g.append("text").attr("class", "num").attr("x", mx).attr("y", my - (wide ? 80 : 56) * S + 1 * S).attr("text-anchor", "middle").attr("fill", "#7dffb0").attr("font-size", (wide ? 17 : 12) * S * 1.3).attr("font-weight", 700);
    const rows = items.map((it, i) => { const x = wide ? X(0.50) : X(0.08), y = wide ? Y(0.14 + i * 0.28) : Y(0.34 + i * 0.22), w = wide ? X(0.46) : X(0.84), r = g.append("g").attr("opacity", 0);
      r.append("rect").attr("x", x).attr("y", y - 70 * S).attr("width", w).attr("height", 140 * S).attr("rx", 36 * S).attr("fill", "#fffaf0").attr("stroke", P.brown).attr("stroke-width", 5 * S);
      icon(r, it.icon, x + 90 * S, y, 90 * S);
      const t = r.append("text").attr("x", x + 180 * S).attr("y", y - 6 * S).attr("fill", P.brown).attr("font-family", MAL).attr("font-weight", 800).text(it.ml); fit(t, 44 * S, w - (wide ? 600 : 640) * S, 14);
      const e = r.append("text").attr("x", x + 180 * S).attr("y", y + 34 * S).attr("fill", P.brown).attr("fill-opacity", 0.7).attr("font-weight", 600).text(it.watts + " W"); e.attr("font-size", 28 * S);
      const hrs = r.append("text").attr("class", "num").attr("x", x + w - 30 * S).attr("y", y + 16 * S).attr("text-anchor", "end").attr("fill", it.col || P.red).attr("font-weight", 700).attr("font-size", (wide ? 60 : 38) * S);
      return { r, hrs, it }; });
    return (lt, d) => { const k = (lt * 3) % 100; digits.text(String(Math.floor(lt * 12 % 10000)).padStart(4, "0"));
      rows.forEach((q, i) => { const o = prog(lt, 0.4 + i * 0.9, 0.4); q.r.attr("opacity", o); const val = 1000 / q.it.watts; q.hrs.text(((E.out(prog(lt, 0.6 + i * 0.9, 1.0)) * val)).toFixed(val < 10 ? 1 : 0) + " " + (p.unitMl || "മണിക്കൂർ")); }); };
  };

  // ================= bird: why a bird on a high-voltage wire is safe =================
  K.bird = (g, p, c) => {
    const { X, Y } = c, S = c.S * (c.wide ? 1.35 : 1), wy = Y(0.46), x0 = X(0.04), x1 = X(0.96);
    g.append("rect").attr("x", X(0.0)).attr("y", Y(0.86)).attr("width", c.stage.w).attr("height", Y(1) - Y(0.86)).attr("fill", P.leaf).attr("opacity", 0.5);
    const pole = (x) => { g.append("rect").attr("x", x - 14 * S).attr("y", wy - 30 * S).attr("width", 28 * S).attr("height", Y(0.9) - wy + 30 * S).attr("fill", P.brown); g.append("rect").attr("x", x - 90 * S).attr("y", wy - 30 * S).attr("width", 180 * S).attr("height", 18 * S).attr("fill", P.brown); };
    pole(X(0.08)); pole(X(0.92));
    const wire = g.append("path").attr("fill", "none").attr("stroke", P.dark).attr("stroke-width", 12 * S);
    const hum = g.append("path").attr("fill", "none").attr("stroke", P.gold).attr("stroke-width", 6 * S).attr("stroke-dasharray", `${14 * S} ${22 * S}`);
    const bird = g.append("g");
    ICON.bird(bird);
    const v1 = pill(g, "11,000 V", null, 0, 0, P.red, 190 * S, 34 * S), v2 = pill(g, "11,000 V", null, 0, 0, P.red, 190 * S, 34 * S);
    const diff = pill(g, "വ്യത്യാസം ≈ 0", "NO DIFFERENCE, NO CURRENT", P.leaf, X(0.5), Y(0.78), 560 * S, 38 * S);
    const gnd = pill(g, "0 V", null, X(0.5), Y(0.93), P.dark, 130 * S, 34 * S);
    const spark = g.append("path").attr("d", "M 0 0 L 16 -34 L -6 -34 L 12 -70").attr("fill", "none").attr("stroke", P.gold).attr("stroke-width", 9 * S).attr("stroke-linecap", "round").attr("opacity", 0);
    return (lt, d) => { const f = lt / d, sag = 24 * S; const pts = []; for (let i = 0; i <= 20; i++) { const u = i / 20; pts.push([lerp(x0, x1, u), wy + sag * Math.sin(u * Math.PI)]); }
      wire.attr("d", basis(pts)); hum.attr("d", basis(pts)).attr("stroke-dashoffset", -lt * 90);
      const bx = X(0.5), by = wy + sag - 36 * S + 3 * Math.sin(lt * 5) * 0; const touch = prog(f, 0.62, 0.1);
      bird.attr("transform", `translate(${bx + (touch ? 260 * S * touch : 0)},${by - 8 * S * touch * 0}) scale(${1.5 * S})`);
      v1.attr("transform", `translate(${bx - 70 * S},${wy - 110 * S})`).attr("opacity", prog(f, 0.15, 0.08)); v2.attr("transform", `translate(${bx + 70 * S},${wy - 110 * S})`).attr("opacity", prog(f, 0.25, 0.08));
      diff.attr("opacity", prog(f, 0.40, 0.08) * (1 - touch)); gnd.attr("opacity", prog(f, 0.58, 0.08));
      spark.attr("opacity", touch > 0.7 ? 0.5 + 0.5 * Math.sin(lt * 40) : 0).attr("transform", `translate(${bx + 260 * S * touch},${by - 24 * S}) scale(${S * 1.5})`); };
  };

  // ================= tea: the steam from a hot glass makes drops on a cold plate, the way vapour makes cloud =================
  K.tea = (g, p, c) => {
    const { X, Y } = c, S = c.S * (c.wide ? 1.35 : 1), cx = X(0.5), gy = Y(c.wide ? 0.70 : 0.72);
    icon(g, "cup", cx, gy, 340 * S);
    const plate = g.append("ellipse").attr("cx", cx).attr("cy", Y(0.20)).attr("rx", 300 * S).attr("ry", 34 * S).attr("fill", "#dde7ee").attr("stroke", P.steel2).attr("stroke-width", 6 * S);
    const steam = Array.from({ length: 26 }, (_, i) => ({ el: g.append("circle").attr("r", (7 + rnd(i) * 7) * S).attr("fill", "#fff").attr("stroke", "#c9d5dd").attr("stroke-width", 2), ph: rnd(i + 5), sp: 0.7 + rnd(i + 9) * 0.5, dx: (rnd(i + 2) - 0.5) * 120 * S }));
    const drops = Array.from({ length: 16 }, (_, i) => ({ el: g.append("path").attr("d", "M 0 -10 Q 8 4 0 10 Q -8 4 0 -10 Z").attr("fill", P.sea), u: (rnd(i + 12) - 0.5) * 520 * S, ph: rnd(i + 1) }));
    return (lt, d) => { const hot = clamp(lt / 1.0);
      steam.forEach((q) => { const u = (lt * 0.28 * q.sp + q.ph) % 1; q.el.attr("cx", cx + q.dx * u + Math.sin(u * 9 + q.ph * 6) * 22 * S).attr("cy", gy - 60 * S - u * (gy - Y(0.24) - 60 * S)).attr("opacity", hot * (1 - 0.5 * u)); });
      drops.forEach((q, i) => { const k = E.out(prog(lt, 1.2 + i * 0.3, 1.2)), fall = prog(lt, 4 + q.ph * 3, 1.6); q.el.attr("transform", `translate(${cx + q.u},${Y(0.20) + 28 * S + fall * 240 * S}) scale(${(0.4 + k * 1.1) * S * 1.6})`).attr("opacity", k * (1 - fall)); }); };
  };

  // ================= text: a big question or statement over a calm moving background =================
  K.text = (g, p, c) => {
    const { X, Y } = c, S = c.S * (c.wide ? 1.35 : 1), cx = X(0.5), cy = Y(0.46), col = p.col || P.brown;
    const rings = [0, 1, 2].map((k) => g.append("circle").attr("cx", cx).attr("cy", cy).attr("fill", "none").attr("stroke", col).attr("stroke-width", 6 * S));
    if (p.icon) icon(g, p.icon, cx, cy - 230 * S, 150 * S);
    const t = g.append("text").attr("x", cx).attr("y", cy + 40 * S).attr("text-anchor", "middle").attr("fill", P.ink).attr("font-family", MAL).attr("font-weight", 800).text(p.ml); fit(t, 150 * S, c.stage.w * 0.86, 40);
    if (p.en) { const e = g.append("text").attr("x", cx).attr("y", cy + 120 * S).attr("text-anchor", "middle").attr("fill", P.brown).attr("fill-opacity", 0.75).attr("font-weight", 700).attr("letter-spacing", 5).text(p.en); fit(e, 40 * S, c.stage.w * 0.86, 14); }
    return (lt, d) => { rings.forEach((q, k) => { const u = (lt * 0.25 + k / 3) % 1; q.attr("r", (120 + u * 520) * S).attr("opacity", 0.35 * (1 - u)); }); t.attr("opacity", E.out(clamp(lt / 0.4))); };
  };

  // ================= outro: the question for the comments, and the brand =================
  K.outro = (g, p, c) => {
    const { X, Y } = c, S = c.S * (c.wide ? 1.35 : 1), cx = X(0.5);
    const q = g.append("g").attr("opacity", 0);
    q.append("rect").attr("x", cx - c.stage.w * 0.42).attr("y", Y(0.12)).attr("width", c.stage.w * 0.84).attr("height", Y(0.48) - Y(0.12)).attr("rx", 50 * S).attr("fill", "#fffaf0").attr("stroke", P.brown).attr("stroke-width", 7 * S);
    const t = q.append("text").attr("x", cx).attr("y", Y(0.12) + (Y(0.48) - Y(0.12)) * 0.56).attr("text-anchor", "middle").attr("fill", P.brown).attr("font-family", MAL).attr("font-weight", 800).text(p.ml); fit(t, 96 * S, c.stage.w * 0.78, 28);
    if (p.en) { const e = q.append("text").attr("x", cx).attr("y", Y(0.12) + (Y(0.48) - Y(0.12)) * 0.82).attr("text-anchor", "middle").attr("fill", P.brown).attr("fill-opacity", 0.75).attr("font-weight", 600).text(p.en); fit(e, 36 * S, c.stage.w * 0.78, 12); }
    const cup = g.append("g").attr("opacity", 0).attr("transform", `translate(${cx - 380 * S},${Y(0.76)})`); ICON.cup(cup);
    const steam = [0, 1, 2].map((k) => cup.append("path").attr("fill", "none").attr("stroke", P.brown).attr("stroke-width", 6).attr("stroke-linecap", "round").datum(k));
    const b1 = g.append("text").attr("x", cx + 70 * S).attr("y", Y(0.76) + 10 * S).attr("text-anchor", "middle").attr("font-family", MAL).attr("font-weight", 800).attr("fill", P.brown).attr("font-size", 110 * S).text("സയൻസ് ചായ").attr("opacity", 0);
    const b2 = g.append("text").attr("x", cx + 70 * S).attr("y", Y(0.76) + 80 * S).attr("text-anchor", "middle").attr("font-weight", 700).attr("letter-spacing", 10).attr("fill", P.brown).attr("font-size", 42 * S).text("SCIENCE CHAYA").attr("opacity", 0);
    const sub = g.append("text").attr("x", cx).attr("y", Y(0.93)).attr("text-anchor", "middle").attr("font-family", MAL).attr("font-weight", 700).attr("fill", P.dark).attr("opacity", 0).text(p.sub || "ഇതുപോലുള്ള വീഡിയോകൾക്ക് സബ്സ്ക്രൈബ് ചെയ്യൂ"); fit(sub, 50 * S, c.stage.w * 0.9, 18);
    return (lt, d) => { const k = E.back(prog(lt, 0.2, 0.6)), k2 = E.out(prog(lt, 1.0, 0.7)); q.attr("opacity", clamp(k * 2)).attr("transform", `translate(0,${(1 - k) * 30 * S})`);
      cup.attr("opacity", k2).attr("transform", `translate(${cx - 380 * S},${Y(0.76) - 8 * (1 - k2)}) scale(${S * 1.5})`); b1.attr("opacity", k2); b2.attr("opacity", k2); sub.attr("opacity", E.out(prog(lt, 1.6, 0.6)));
      steam.forEach((s2) => { const kk = s2.datum(), pts = []; for (let y = 0; y <= 70; y += 10) pts.push([(kk - 1) * 22 + Math.sin(y / 9 + lt * 3 + kk) * 7, -60 - y - ((lt * 22 + kk * 20) % 20)]); s2.attr("d", basis(pts)).attr("opacity", 0.55 * k2); }); };
  };

  // ================= more icons for the nostalgia and village stories =================
  Object.assign(ICON, {
    bottle: (g) => { g.append("path").attr("d", "M -14 -52 L 14 -52 L 14 -34 Q 30 -22 30 -2 L 30 44 Q 30 52 22 52 L -22 52 Q -30 52 -30 44 L -30 -2 Q -30 -22 -14 -34 Z").attr("fill", "#7fc6b0").attr("fill-opacity", 0.75).attr("stroke", P.dark).attr("stroke-width", 4);
      g.append("rect").attr("x", -26).attr("y", 8).attr("width", 52).attr("height", 40).attr("rx", 6).attr("fill", "#f6b945").attr("opacity", 0.55); },
    marble: (g) => { g.append("circle").attr("r", 12).attr("fill", "#3a6fb0").attr("stroke", "#fff").attr("stroke-width", 2); g.append("circle").attr("cx", -4).attr("cy", -4).attr("r", 3).attr("fill", "#fff").attr("opacity", 0.8); },
    firefly: (g) => { g.append("ellipse").attr("rx", 14).attr("ry", 8).attr("fill", P.dark); g.append("ellipse").attr("cx", 12).attr("rx", 9).attr("ry", 7).attr("fill", "#fff36b"); g.append("path").attr("d", "M -2 -6 Q -14 -26 -26 -16 Q -16 -6 -2 -4 Z").attr("fill", "#fff").attr("opacity", 0.7); g.append("circle").attr("cx", -16).attr("r", 5).attr("fill", P.dark); },
    lamp: (g) => { g.append("path").attr("d", "M -30 52 L 30 52 L 26 14 Q 24 4 0 4 Q -24 4 -26 14 Z").attr("fill", P.steel2); g.append("path").attr("d", "M -20 -6 Q -22 -44 0 -48 Q 22 -44 20 -6 Z").attr("fill", "#fffbe0").attr("fill-opacity", 0.5).attr("stroke", P.dark).attr("stroke-width", 3);
      g.append("path").attr("d", "M 0 -6 Q -12 -22 0 -40 Q 12 -22 0 -6 Z").attr("fill", P.gold); g.append("rect").attr("x", -3).attr("y", -8).attr("width", 6).attr("height", 14).attr("fill", P.dark); },
    cassette: (g) => { g.append("rect").attr("x", -50).attr("y", -32).attr("width", 100).attr("height", 64).attr("rx", 8).attr("fill", P.dark); g.append("rect").attr("x", -40).attr("y", -24).attr("width", 80).attr("height", 30).attr("rx", 5).attr("fill", P.cream);
      for (const x of [-18, 18]) { g.append("circle").attr("cx", x).attr("cy", -9).attr("r", 10).attr("fill", P.dark); g.append("circle").attr("cx", x).attr("cy", -9).attr("r", 4).attr("fill", P.cream); } g.append("path").attr("d", "M -30 32 L -22 14 L 22 14 L 30 32 Z").attr("fill", P.steel2); },
    chenda: (g) => { g.append("rect").attr("x", -22).attr("y", -42).attr("width", 44).attr("height", 84).attr("rx", 6).attr("fill", P.rock2); g.append("ellipse").attr("cy", -42).attr("rx", 26).attr("ry", 9).attr("fill", P.cream).attr("stroke", P.dark).attr("stroke-width", 4);
      g.append("ellipse").attr("cy", 42).attr("rx", 26).attr("ry", 9).attr("fill", P.cream).attr("stroke", P.dark).attr("stroke-width", 4); for (let i = -2; i <= 2; i++) g.append("path").attr("d", `M ${i * 10 - 4} -40 L ${i * 10 + 4} 40`).attr("stroke", P.amber).attr("stroke-width", 2); },
    rocket: (g) => { g.append("path").attr("d", "M 0 -60 Q 22 -34 20 20 L -20 20 Q -22 -34 0 -60 Z").attr("fill", "#f2f2f2").attr("stroke", P.dark).attr("stroke-width", 3); g.append("circle").attr("cy", -22).attr("r", 9).attr("fill", P.sea);
      g.append("path").attr("d", "M -20 4 L -38 34 L -20 22 Z").attr("fill", P.red); g.append("path").attr("d", "M 20 4 L 38 34 L 20 22 Z").attr("fill", P.red); g.append("path").attr("d", "M -10 22 Q 0 52 10 22 Z").attr("fill", P.gold); },
    church: (g) => { g.append("rect").attr("x", -42).attr("y", -6).attr("width", 84).attr("height", 52).attr("fill", "#f3e2c4").attr("stroke", P.dark).attr("stroke-width", 3); g.append("path").attr("d", "M -42 -6 L 0 -40 L 42 -6 Z").attr("fill", P.red);
      g.append("rect").attr("x", -9).attr("y", 20).attr("width", 18).attr("height", 26).attr("rx", 9).attr("fill", P.dark); g.append("path").attr("d", "M 0 -64 L 0 -42 M -8 -56 L 8 -56").attr("stroke", P.dark).attr("stroke-width", 4); },
    bicycle: (g) => { for (const x of [-32, 32]) g.append("circle").attr("cx", x).attr("cy", 18).attr("r", 22).attr("fill", "none").attr("stroke", P.dark).attr("stroke-width", 5); g.append("path").attr("d", "M -32 18 L -6 -14 L 22 -14 L 32 18 M -6 -14 L 8 18 L -32 18 M 22 -14 L 18 -26").attr("fill", "none").attr("stroke", P.red).attr("stroke-width", 5).attr("stroke-linejoin", "round"); },
    banana: (g) => { g.append("path").attr("d", "M -44 -10 Q -10 56 46 -34 Q 50 -42 42 -40 Q 6 34 -36 -22 Q -46 -24 -44 -10 Z").attr("fill", "#f4d03f").attr("stroke", P.dark).attr("stroke-width", 3); g.append("rect").attr("x", 38).attr("y", -48).attr("width", 10).attr("height", 12).attr("fill", P.leaf2); },
    jackfruit: (g) => { g.append("ellipse").attr("rx", 42).attr("ry", 56).attr("fill", "#9bb64a").attr("stroke", P.dark).attr("stroke-width", 3); for (let i = 0; i < 18; i++) g.append("circle").attr("cx", Math.cos(i * 2.4) * 26).attr("cy", Math.sin(i * 2.4) * 36 * (i % 3 ? 0.9 : 0.5)).attr("r", 3.4).attr("fill", "#6c8a2a"); },
    mango: (g) => { g.append("path").attr("d", "M 0 -40 Q 44 -34 46 12 Q 44 50 4 52 Q -40 50 -44 6 Q -42 -36 0 -40 Z").attr("fill", "#f7b32b").attr("stroke", P.dark).attr("stroke-width", 3); g.append("path").attr("d", "M 2 -40 Q 10 -54 24 -52 Q 18 -42 2 -40 Z").attr("fill", P.leaf); },
    salt: (g) => { g.append("rect").attr("x", -22).attr("y", -22).attr("width", 44).attr("height", 60).attr("rx", 8).attr("fill", "#fff").attr("stroke", P.dark).attr("stroke-width", 3); g.append("rect").attr("x", -26).attr("y", -36).attr("width", 52).attr("height", 18).attr("rx", 6).attr("fill", P.steel); for (const [x, y] of [[-8, -28], [0, -28], [8, -28]]) g.append("circle").attr("cx", x).attr("cy", y).attr("r", 2).attr("fill", P.dark); },
    person: (g) => { g.append("circle").attr("cy", -34).attr("r", 12).attr("fill", "#d9a272"); g.append("path").attr("d", "M -16 -18 L 16 -18 L 20 24 L -20 24 Z").attr("fill", P.sea); g.append("path").attr("d", "M -12 24 L -14 56 M 12 24 L 14 56").attr("stroke", P.dark).attr("stroke-width", 7).attr("stroke-linecap", "round"); },
    tree: (g) => { g.append("rect").attr("x", -7).attr("y", 4).attr("width", 14).attr("height", 48).attr("fill", P.rock2); g.append("circle").attr("cy", -14).attr("r", 34).attr("fill", P.leaf); g.append("circle").attr("cx", -22).attr("cy", 2).attr("r", 24).attr("fill", P.leaf2); g.append("circle").attr("cx", 22).attr("cy", 2).attr("r", 24).attr("fill", P.leaf2); },
    coconut: (g) => { g.append("rect").attr("x", -5).attr("y", -20).attr("width", 10).attr("height", 76).attr("fill", P.rock2).attr("transform", "rotate(6)"); for (let i = 0; i < 6; i++) g.append("path").attr("d", "M 0 -24 Q 30 -50 52 -26 Q 28 -34 0 -24").attr("fill", P.leaf).attr("transform", `rotate(${i * 60 - 20} 0 -24)`); },
    moon: (g) => { g.append("path").attr("d", "M 14 -44 A 44 44 0 1 0 14 44 A 34 34 0 1 1 14 -44 Z").attr("fill", "#fff6c9"); },
    cloudDark: (g) => { for (const [x, y, r] of [[-26, 6, 26], [4, -12, 34], [34, 6, 24]]) g.append("circle").attr("cx", x).attr("cy", y).attr("r", r).attr("fill", "#59606b"); g.append("rect").attr("x", -52).attr("y", 6).attr("width", 104).attr("height", 24).attr("fill", "#59606b"); },
    thermo: (g) => { g.append("rect").attr("x", -8).attr("y", -48).attr("width", 16).attr("height", 70).attr("rx", 8).attr("fill", "#fff").attr("stroke", P.dark).attr("stroke-width", 3); g.append("circle").attr("cy", 32).attr("r", 16).attr("fill", P.red).attr("stroke", P.dark).attr("stroke-width", 3); g.append("rect").attr("x", -4).attr("y", -10).attr("width", 8).attr("height", 40).attr("fill", P.red); },
    magnet: (g) => { g.append("path").attr("d", "M -36 -40 L -36 10 Q -36 44 0 44 Q 36 44 36 10 L 36 -40 L 18 -40 L 18 10 Q 18 26 0 26 Q -18 26 -18 10 L -18 -40 Z").attr("fill", P.red); g.append("rect").attr("x", -36).attr("y", -40).attr("width", 18).attr("height", 16).attr("fill", "#fff"); g.append("rect").attr("x", 18).attr("y", -40).attr("width", 18).attr("height", 16).attr("fill", "#fff"); },
    boat: (g) => { g.append("path").attr("d", "M -64 6 Q 0 34 64 -8 Q 60 18 30 22 L -50 22 Q -62 18 -64 6 Z").attr("fill", P.red).attr("stroke", P.dark).attr("stroke-width", 3); for (let i = -3; i <= 3; i++) g.append("path").attr("d", `M ${i * 14} 2 L ${i * 14 - 8} -22`).attr("stroke", P.dark).attr("stroke-width", 5).attr("stroke-linecap", "round"); },
  });

  // ================= compose: a scene described as data (layers in drawing order, each with its own start/end as a fraction of the scene) =================
  // layer types: icon rect circle ellipse path text flow particles bolt flash rings spiral. Coordinates are 0..1 of the stage; "s" is an icon size multiplier.
  K.compose = (g, p, c) => {
    const { X, Y } = c, S = c.S * (c.wide ? 1.2 : 1), W = c.stage.w, H = c.stage.h, id = c.id + rid();
    const defs = M.svg.select("defs"), BG = { sky: [P.sky1, P.sky2], night: ["#0b1631", "#2a4472"], dusk: ["#f0a679", "#fde7c8"], dark: ["#17110c", "#3a2a1d"], storm: ["#3c4350", "#7a8493"], soil: ["#9a6f45", "#6a4a2c"] };
    if (BG[p.bg]) { const gr = defs.append("linearGradient").attr("id", id + "g").attr("x1", 0).attr("x2", 0).attr("y1", 0).attr("y2", 1); gr.append("stop").attr("offset", 0).attr("stop-color", BG[p.bg][0]); gr.append("stop").attr("offset", 1).attr("stop-color", BG[p.bg][1]);
      g.append("rect").attr("x", X(0)).attr("y", Y(0)).attr("width", W).attr("height", H).attr("fill", `url(#${id}g)`); }
    const flashRect = g.append("rect").attr("x", X(0)).attr("y", Y(0)).attr("width", W).attr("height", H).attr("fill", "#fff").attr("opacity", 0);
    const ups = [];
    const pt = (o, k = "x") => [X(o[k] ?? 0.5), Y(o[k === "x" ? "y" : k + "y"] ?? 0.5)];
    const vis = (o, f) => prog(f, o.at ?? 0, 0.04) * (o.end != null ? 1 - prog(f, o.end, 0.04) : 1);
    const label = (grp, o) => { if (!o.label) return null; const l = o.label, lw = (l.w || 330) * S; return pill(grp, l.ml, l.en, (l.dx || 0) * S * 100, (l.dy ?? 1.3) * S * 100 + 0, l.col || P.brown, lw, 34 * S); };
    for (const o of p.layers || []) {
      const grp = g.append("g").attr("opacity", ["flow", "particles", "rings", "spiral"].includes(o.t) ? 1 : 0);
      const sty = (n) => n.attr("fill", o.fill || "none").attr("stroke", o.stroke || "none").attr("stroke-width", (o.sw || 4) * S).attr("fill-opacity", o.op ?? 1);
      if (o.t === "icon") {
        const ig = icon(grp, o.icon, 0, 0, (o.s || 1.5) * 100 * S);
        if (o.glow) ig.insert("circle", ":first-child").attr("r", 52).attr("fill", o.glow).attr("opacity", 0.22);
        label(grp, o);
        const from = pt(o), to = o.to ? [X(o.to[0]), Y(o.to[1])] : from, ph = rnd((o.x || 0) * 99 + (o.y || 0) * 31);
        ups.push((lt, f) => { const mk = E.inOut(prog(f, o.mv ?? o.at ?? 0, o.dur ?? 0.2)), x = lerp(from[0], to[0], mk), y = lerp(from[1], to[1], mk);
          let dy = 0, sc = 1, rot = o.rot || 0, op = vis(o, f);
          if (o.anim === "float") dy = Math.sin(lt * 2 + ph * 6) * 10 * S; if (o.anim === "pulse") sc = 1 + 0.12 * Math.sin(lt * 4 + ph * 6); if (o.anim === "spin") rot += lt * (o.speed || 120);
          if (o.anim === "shake") dy = Math.sin(lt * 40) * 4 * S; if (o.anim === "blink") op *= 0.25 + 0.75 * Math.max(0, Math.sin(lt * 3 + ph * 8));
          if (o.rise) dy -= lt * o.rise * S * 100;
          grp.attr("opacity", op).attr("transform", `translate(${x},${y + dy}) rotate(${rot}) scale(${sc})`); });
      } else if (o.t === "rect") { sty(grp.append("rect").attr("x", X(o.x)).attr("y", Y(o.y)).attr("width", o.w * W).attr("height", o.h * H).attr("rx", (o.rx || 0) * S)); ups.push((lt, f) => grp.attr("opacity", vis(o, f)));
      } else if (o.t === "circle") { sty(grp.append("circle").attr("cx", X(o.x)).attr("cy", Y(o.y)).attr("r", o.r * Math.min(W, H))); ups.push((lt, f) => grp.attr("opacity", vis(o, f) * (o.pulse ? 0.7 + 0.3 * Math.sin(lt * 4) : 1)));
      } else if (o.t === "ellipse") { sty(grp.append("ellipse").attr("cx", X(o.x)).attr("cy", Y(o.y)).attr("rx", o.rx * W).attr("ry", o.ry * H)); ups.push((lt, f) => grp.attr("opacity", vis(o, f)));
      } else if (o.t === "path") { const pts = o.pts.map(([x, y]) => [X(x), Y(y)]); sty(grp.append("path").attr("d", (o.smooth ? smooth : line)(pts) + (o.close ? "Z" : ""))); ups.push((lt, f) => grp.attr("opacity", vis(o, f)));
      } else if (o.t === "text") { const t = grp.append("text").attr("x", X(o.x ?? 0.5)).attr("y", Y(o.y ?? 0.5)).attr("text-anchor", "middle").attr("fill", o.col || P.ink).attr("font-family", MAL).attr("font-weight", 800).text(o.ml); fit(t, (o.size || 90) * S, (o.w || 0.9) * W, 20); ups.push((lt, f) => grp.attr("opacity", vis(o, f)));
      } else if (o.t === "flow") {        // particles streaming from one point to another
        const n = o.n || 12, a = pt(o), b = [X(o.to[0]), Y(o.to[1])], dots = Array.from({ length: n }, () => grp.append("circle").attr("r", (o.r || 8) * S).attr("fill", o.col || P.sea));
        ups.push((lt, f) => { const v = vis(o, f); dots.forEach((q, i) => { const u = (((lt * (o.speed || 0.4) + i / n) % 1) + 1) % 1; q.attr("cx", lerp(a[0], b[0], u) + Math.sin(u * 12 + i) * (o.wob || 10) * S).attr("cy", lerp(a[1], b[1], u) + Math.cos(u * 9 + i * 2) * (o.wob || 10) * S).attr("opacity", v * Math.sin(Math.PI * u)); }); });
      } else if (o.t === "particles") {   // a field of drifting dots: fireflies blink, bubbles rise, rain falls
        const n = o.n || 20, ar = o.area || [0, 0, 1, 1], dots = Array.from({ length: n }, (_, i) => ({ el: grp.append("circle").attr("r", (o.r || 7) * S).attr("fill", o.col || "#fff36b"), s: rnd(i + 3), t: rnd(i + 9), u: rnd(i + 17) }));
        ups.push((lt, f) => { const v = vis(o, f); dots.forEach((q, i) => { let x, y, op = v; const T = lt * (o.speed || 0.3);
          if (o.kind === "rain") { const u = (T * 2 + q.s) % 1; x = lerp(ar[0], ar[2], q.t) + u * 0.02; y = lerp(ar[1], ar[3], u); op *= 0.8; }
          else if (o.kind === "bubbles") { const u = (T + q.s) % 1; x = lerp(ar[0], ar[2], q.t) + Math.sin(u * 14 + i) * 0.015; y = lerp(ar[3], ar[1], u); op *= Math.sin(Math.PI * u); }
          else { x = lerp(ar[0], ar[2], q.t) + Math.sin(T * 2 + q.s * 9) * 0.05; y = lerp(ar[1], ar[3], q.s) + Math.cos(T * 1.7 + q.t * 9) * 0.04; op *= 0.1 + 0.9 * Math.max(0, Math.sin(lt * 2.4 + q.u * 12)); }
          q.el.attr("cx", X(x)).attr("cy", Y(y)).attr("opacity", op); }); });
      } else if (o.t === "bolt") {        // a jagged lightning stroke with a white flash
        const a = pt(o), b = [X(o.to[0]), Y(o.to[1])], pts = [a], N = 16; for (let i = 1; i < N; i++) { const u = i / N; pts.push([lerp(a[0], b[0], u) + (rnd(i + (o.seed || 1) * 7) - 0.5) * 140 * S * (1 - u * 0.4), lerp(a[1], b[1], u)]); } pts.push(b);
        const path = grp.append("path").attr("d", line(pts)).attr("fill", "none").attr("stroke", o.col || "#fff7c2").attr("stroke-width", (o.w || 12) * S).attr("stroke-linejoin", "round");
        const glow = grp.insert("path", ":first-child").attr("d", line(pts)).attr("fill", "none").attr("stroke", "#9fc7ff").attr("stroke-width", (o.w || 12) * S * 3).attr("opacity", 0.5);
        ups.push((lt, f, d) => { const k = (f - (o.at ?? 0)) * d, dd = o.dur || 0.09, on = k >= 0 && k < dd ? 1 : (k >= dd * 2 && k < dd * 3 ? 0.7 : 0); grp.attr("opacity", on); flashRect.attr("opacity", on * 0.55); void path; void glow; });
      } else if (o.t === "flash") { ups.push((lt, f, d) => { const k = (f - (o.at ?? 0)) * d; if (k >= 0 && k < 0.45) flashRect.attr("opacity", 0.8 * (1 - k / 0.45)); }); grp.remove();
      } else if (o.t === "rings") {       // sound or pressure waves
        const cx = X(o.x), cy = Y(o.y), rs = [0, 1, 2, 3].map(() => grp.append("circle").attr("cx", cx).attr("cy", cy).attr("fill", "none").attr("stroke", o.col || P.red).attr("stroke-width", 6 * S));
        ups.push((lt, f) => { const v = vis(o, f); rs.forEach((q, k) => { const u = (lt * (o.speed || 0.5) + k / 4) % 1; q.attr("r", (30 + u * (o.r || 0.45) * Math.min(W, H)) ).attr("opacity", v * (1 - u) * 0.8); }); });
      } else if (o.t === "spiral") {      // a turning cyclone: arms of cloud around a low-pressure centre
        const cx = X(o.x), cy = Y(o.y), R = (o.r || 0.3) * Math.min(W, H), arms = [0, 1, 2].map(() => grp.append("path").attr("fill", "none").attr("stroke", o.col || "#ffffff").attr("stroke-width", 22 * S).attr("stroke-linecap", "round").attr("opacity", 0.8));
        const eye = grp.append("circle").attr("cx", cx).attr("cy", cy).attr("r", R * 0.09).attr("fill", o.eye || P.dark).attr("opacity", 0.7);
        ups.push((lt, f) => { const v = vis(o, f); arms.forEach((q, k) => { const pts = []; for (let i = 0; i <= 40; i++) { const u = i / 40, th = u * 4.2 + k * 2.094 - lt * (o.speed || 0.8); pts.push([cx + Math.cos(th) * R * (0.1 + 0.9 * u), cy + Math.sin(th) * R * (0.1 + 0.9 * u) * 0.9]); } q.attr("d", basis(pts)).attr("opacity", v * 0.85); }); eye.attr("opacity", v * 0.7); });
      }
    }
    return (lt, d) => { const f = lt / d; flashRect.attr("opacity", 0); ups.forEach((u) => u(lt, f, d)); };
  };

  // ================= the runner: scenes crossfade, bilingual cards on top, a thin progress line, a small brand mark =================
  SCENES.chaya = (g, s) => {
    const W = M.W, H = M.H, wide = W > H, id = "cz" + rid();
    const stage = wide ? { x: 0, y: 215, w: W, h: H - 215 - 20 } : { x: 0, y: 330, w: W, h: 1420 };
    const c = { W, H, wide, stage, X: (u) => stage.x + u * stage.w, Y: (v) => stage.y + v * stage.h, S: Math.min(stage.w, stage.h) / 1000, id };
    const defs = M.svg.select("defs");
    const sh = defs.append("filter").attr("id", id + "sh").attr("x", "-20%").attr("y", "-20%").attr("width", "140%").attr("height", "150%");
    sh.append("feDropShadow").attr("dx", 0).attr("dy", 8).attr("stdDeviation", 9).attr("flood-color", P.ink).attr("flood-opacity", 0.35);
    g.append("rect").attr("width", W).attr("height", H).attr("fill", P.cream);
    const dotsBg = g.append("g").attr("opacity", 0.07);
    for (let x = 30; x < W; x += 70) for (let y = 30; y < H; y += 70) dotsBg.append("circle").attr("cx", x).attr("cy", y).attr("r", 4).attr("fill", P.brown);
    const scenes = s.scenes.map((sc) => { const grp = g.append("g").attr("opacity", 0).attr("display", "none"); const upd = K[sc.kind](grp, sc.p || {}, c); return { grp, upd, t0: sc.t0, t1: sc.t1, kind: sc.kind }; });
    // cards
    const cardW = wide ? Math.min(1200, W * 0.64) : 900, cardH = wide ? 150 : 190, cardY = wide ? 118 : 215;
    const cards = (s.cards || []).map((cd) => { const grp = g.append("g").attr("opacity", 0), col = cd.col || P.brown;
      grp.append("rect").attr("x", -cardW / 2).attr("y", -cardH / 2).attr("width", cardW).attr("height", cardH).attr("rx", 40).attr("fill", col).attr("filter", `url(#${id}sh)`);
      grp.append("rect").attr("x", -cardW / 2 + 8).attr("y", -cardH / 2 + 8).attr("width", cardW - 16).attr("height", cardH - 16).attr("rx", 34).attr("fill", "none").attr("stroke", "#fff").attr("stroke-opacity", 0.28).attr("stroke-width", 3);
      const tml = grp.append("text").attr("y", -cardH * 0.02).attr("text-anchor", "middle").attr("fill", "#fff").attr("font-weight", 800).attr("font-family", MAL).text(cd.ml); fit(tml, wide ? 76 : 84, cardW - 70, 30);
      if (cd.en) { const ten = grp.append("text").attr("y", cardH * (wide ? 0.38 : 0.37)).attr("text-anchor", "middle").attr("fill", "#fff").attr("fill-opacity", 0.86).attr("font-weight", 600).attr("letter-spacing", 4).text(cd.en); fit(ten, wide ? 26 : 30, cardW - 70, 12); }
      return { grp, t0: cd.t0, t1: cd.t1 }; });
    // brand mark and progress
    const bar = g.append("rect").attr("x", 0).attr("y", H - 8).attr("height", 8).attr("fill", P.amber);
    const mark = g.append("text").attr("x", wide ? 36 : 40).attr("y", wide ? 52 : 84).attr("fill", P.brown).attr("fill-opacity", 0.7).attr("font-family", MAL).attr("font-weight", 800).attr("font-size", wide ? 34 : 38).text("സയൻസ് ചായ");
    const T = s.duration;
    return (t) => {
      scenes.forEach((sc, i) => {
        const last = i === scenes.length - 1, vis = t >= sc.t0 - 0.02 && (last || t <= sc.t1 + 0.35);
        sc.grp.attr("display", vis ? null : "none");
        if (!vis) return;
        const lt = t - sc.t0, d = sc.t1 - sc.t0, o = prog(t, sc.t0, 0.3) * (last ? 1 : 1 - prog(t, sc.t1, 0.3));
        sc.grp.attr("opacity", o).attr("transform", `translate(0,${(1 - E.out(prog(t, sc.t0, 0.4))) * 26})`);
        sc.upd(Math.max(0, lt), Math.max(0.5, d));
      });
      cards.forEach((cd) => { const a = clamp(prog(t, cd.t0, 0.28) * (1 - prog(t, cd.t1 - 0.12, 0.12))), pop = E.back(prog(t, cd.t0, 0.36));
        cd.grp.attr("opacity", a).attr("transform", `translate(${W / 2},${cardY + 16 * (1 - pop)}) scale(${0.92 + 0.08 * pop})`); });
      bar.attr("width", W * clamp(t / T));
      mark.attr("opacity", 1);
    };
  };
})();
