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
    jackfruit: (g) => { g.append("ellipse").attr("rx", 42).attr("ry", 56).attr("fill", "#b8c24b").attr("stroke", P.dark).attr("stroke-width", 3); for (let i = 0; i < 18; i++) g.append("circle").attr("cx", Math.cos(i * 2.4) * 26).attr("cy", Math.sin(i * 2.4) * 36 * (i % 3 ? 0.9 : 0.5)).attr("r", 3.4).attr("fill", "#6c8a2a"); },
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
    leaf: (g) => { g.append("path").attr("d", "M 0 50 Q -52 8 0 -52 Q 52 8 0 50 Z").attr("fill", P.leaf); g.append("path").attr("d", "M 0 44 L 0 -36").attr("stroke", P.leaf2).attr("stroke-width", 4); },
    bowl: (g) => { g.append("path").attr("d", "M -50 -4 L 50 -4 Q 46 44 0 46 Q -46 44 -50 -4 Z").attr("fill", "#f3ede0").attr("stroke", P.dark).attr("stroke-width", 4); g.append("ellipse").attr("cy", -4).attr("rx", 50).attr("ry", 10).attr("fill", "#fffaf0").attr("stroke", P.dark).attr("stroke-width", 4); },
    cooker: (g) => { g.append("rect").attr("x", -44).attr("y", -10).attr("width", 88).attr("height", 52).attr("rx", 10).attr("fill", P.steel); g.append("rect").attr("x", -50).attr("y", -22).attr("width", 100).attr("height", 18).attr("rx", 8).attr("fill", P.steel2); g.append("rect").attr("x", -6).attr("y", -42).attr("width", 12).attr("height", 22).attr("fill", P.dark); g.append("rect").attr("x", -54).attr("y", 8).attr("width", 12).attr("height", 10).attr("fill", P.dark); g.append("rect").attr("x", 42).attr("y", 8).attr("width", 12).attr("height", 10).attr("fill", P.dark); },
    onion: (g) => { g.append("path").attr("d", "M 0 -46 Q 10 -34 8 -26 Q 52 -6 40 28 Q 24 52 0 52 Q -24 52 -40 28 Q -52 -6 -8 -26 Q -10 -34 0 -46 Z").attr("fill", "#b24a8f").attr("stroke", P.dark).attr("stroke-width", 3); for (const x of [-18, 0, 18]) g.append("path").attr("d", `M ${x * 0.3} -24 Q ${x * 1.6} 10 ${x} 46`).attr("fill", "none").attr("stroke", "#e9b6d6").attr("stroke-width", 3); },
    elephant: (g) => { g.append("ellipse").attr("cx", 6).attr("cy", 6).attr("rx", 44).attr("ry", 32).attr("fill", "#7b8794"); g.append("circle").attr("cx", -36).attr("cy", -8).attr("r", 24).attr("fill", "#7b8794"); g.append("path").attr("d", "M -48 0 Q -62 26 -50 44 Q -42 48 -42 38 Q -46 22 -38 8 Z").attr("fill", "#6a7582"); g.append("ellipse").attr("cx", -22).attr("cy", -8).attr("rx", 16).attr("ry", 22).attr("fill", "#6a7582"); g.append("circle").attr("cx", -42).attr("cy", -14).attr("r", 3).attr("fill", P.dark); g.append("path").attr("d", "M -50 10 Q -64 14 -66 4").attr("stroke", "#f6efe0").attr("stroke-width", 5).attr("fill", "none").attr("stroke-linecap", "round"); for (const x of [-18, -2, 18, 34]) g.append("rect").attr("x", x - 6).attr("y", 22).attr("width", 12).attr("height", 30).attr("rx", 4).attr("fill", "#6a7582"); },
  });

  // ---- characters: small flat people with faces, moods, a blink and a prop in the hand ----
  const CAST = { man: { skin: "#c68b5e", hair: "#1d130c", top: "#f3efe6", extra: "mundu" }, woman: { skin: "#c68b5e", hair: "#1d130c", top: "#2f7d4f", extra: "bun" },
    kid: { skin: "#d19a6c", hair: "#1d130c", top: "#f0b43a", extra: "kid" }, shopkeeper: { skin: "#b97b50", hair: "#1d130c", top: "#c8442f", extra: "mustache" }, student: { skin: "#c68b5e", hair: "#1d130c", top: "#1f8aa8", extra: "bag" } };
  function drawChar(g, who, mood, holdIcon) {
    const C = CAST[who] || CAST.man, kid = who === "kid", hs = kid ? 1.15 : 1;
    const body = g.append("g");
    body.append("path").attr("d", kid ? "M -34 30 Q -36 100 -28 112 L 28 112 Q 36 100 34 30 Q 0 14 -34 30 Z" : "M -42 28 Q -48 110 -38 128 L 38 128 Q 48 110 42 28 Q 0 8 -42 28 Z").attr("fill", C.top).attr("stroke", P.dark).attr("stroke-width", 3);
    if (C.extra === "mundu") body.append("path").attr("d", "M -38 128 L 38 128 L 44 170 L -44 170 Z").attr("fill", "#fffaf0").attr("stroke", P.dark).attr("stroke-width", 3);
    else if (!kid) body.append("path").attr("d", "M -38 128 L 38 128 L 34 172 L -34 172 Z").attr("fill", who === "woman" ? "#1f7344" : "#2b3a55").attr("stroke", P.dark).attr("stroke-width", 3);
    else body.append("path").attr("d", "M -28 112 L 28 112 L 26 150 L -26 150 Z").attr("fill", "#2b3a55").attr("stroke", P.dark).attr("stroke-width", 3);
    body.append("rect").attr("x", -9).attr("y", 14).attr("width", 18).attr("height", 18).attr("fill", C.skin);
    // arms: a raised, pointing arm on the right and a hanging one on the left (or holding the prop)
    const armL = g.append("path").attr("d", "M -40 36 Q -64 70 -56 108").attr("fill", "none").attr("stroke", C.top).attr("stroke-width", 16).attr("stroke-linecap", "round");
    const hand = mood === "point" ? "M 40 36 Q 74 14 92 -22" : holdIcon ? "M 40 36 Q 72 62 70 84" : "M 40 36 Q 64 70 56 108";
    const armR = g.append("path").attr("d", hand).attr("fill", "none").attr("stroke", C.top).attr("stroke-width", 16).attr("stroke-linecap", "round");
    const endpt = mood === "point" ? [92, -22] : holdIcon ? [70, 84] : [56, 108];
    g.append("circle").attr("cx", endpt[0]).attr("cy", endpt[1]).attr("r", 9).attr("fill", C.skin);
    if (holdIcon && ICON[holdIcon]) { const hg = g.append("g").attr("transform", `translate(${endpt[0] + 12},${endpt[1] - 22}) scale(0.5)`); ICON[holdIcon](hg); }
    void armL; void armR;
    const head = g.append("g").attr("transform", `translate(0,${-22}) scale(${hs})`);
    head.append("circle").attr("r", 36).attr("fill", C.skin).attr("stroke", P.dark).attr("stroke-width", 3);
    head.append("path").attr("d", C.extra === "bun" ? "M -36 -6 Q -40 -46 0 -44 Q 40 -46 36 -6 Q 24 -28 0 -26 Q -24 -28 -36 -6 Z" : "M -36 -8 Q -38 -48 0 -46 Q 38 -48 36 -8 Q 20 -30 0 -28 Q -20 -30 -36 -8 Z").attr("fill", C.hair);
    if (C.extra === "bun") head.append("circle").attr("cx", 0).attr("cy", -50).attr("r", 13).attr("fill", C.hair);
    const eyes = [-13, 13].map((x) => head.append("ellipse").attr("cx", x).attr("cy", -4).attr("rx", 5).attr("ry", mood === "wow" ? 8 : 5.5).attr("fill", P.dark));
    head.append("path").attr("d", mood === "wow" ? "M -20 -18 Q -13 -26 -6 -18 M 6 -18 Q 13 -26 20 -18" : mood === "think" ? "M -20 -14 L -6 -18 M 6 -20 L 20 -14" : "M -20 -16 Q -13 -20 -6 -16 M 6 -16 Q 13 -20 20 -16").attr("fill", "none").attr("stroke", C.hair === "#1d130c" ? "#1d130c" : P.dark).attr("stroke-width", 3.5).attr("stroke-linecap", "round");
    if (mood === "wow") head.append("ellipse").attr("cy", 18).attr("rx", 8).attr("ry", 11).attr("fill", "#7a2418").attr("stroke", P.dark).attr("stroke-width", 2.5);
    else if (mood === "smile" || mood === "point") head.append("path").attr("d", "M -14 14 Q 0 30 14 14").attr("fill", "#fff").attr("stroke", P.dark).attr("stroke-width", 3);
    else if (mood === "think") head.append("path").attr("d", "M -10 20 L 10 16").attr("stroke", P.dark).attr("stroke-width", 3.5).attr("stroke-linecap", "round");
    else head.append("path").attr("d", "M -10 18 Q 0 22 10 18").attr("fill", "none").attr("stroke", P.dark).attr("stroke-width", 3.5).attr("stroke-linecap", "round");
    if (C.extra === "mustache") head.append("path").attr("d", "M -16 10 Q 0 4 16 10 Q 0 16 -16 10 Z").attr("fill", C.hair);
    if (C.extra === "bag") g.append("rect").attr("x", -58).attr("y", 38).attr("width", 20).attr("height", 46).attr("rx", 6).attr("fill", "#8d4a2b").attr("opacity", 0.9);
    return { eyes, head, armR };
  }

  // ================= painted sets: rich backgrounds with depth (soft blur far away), used by compose scenes through p.bg =================
  function drawSet(g, name, c, id) {
    const { X, Y } = c, W = c.stage.w, H = c.stage.h, defs = M.svg.select("defs"), u = c.S;
    const lg = (nm, stops, x2 = 0, y2 = 1) => { const gr = defs.append("linearGradient").attr("id", id + nm).attr("x1", 0).attr("y1", 0).attr("x2", x2).attr("y2", y2); stops.forEach(([o, col]) => gr.append("stop").attr("offset", o).attr("stop-color", col)); return `url(#${id + nm})`; };
    const rg = (nm, stops) => { const gr = defs.append("radialGradient").attr("id", id + nm); stops.forEach(([o, col, op]) => gr.append("stop").attr("offset", o).attr("stop-color", col).attr("stop-opacity", op ?? 1)); return `url(#${id + nm})`; };
    const blur = (nm, sd) => { defs.append("filter").attr("id", id + nm).attr("x", "-10%").attr("y", "-10%").attr("width", "120%").attr("height", "120%").append("feGaussianBlur").attr("stdDeviation", sd); return `url(#${id + nm})`; };
    const R = (x, y, w, h, fill) => g.append("rect").attr("x", X(x)).attr("y", Y(y)).attr("width", w * W).attr("height", h * H).attr("fill", fill);
    const palms = (y0, n, seed, col, f) => { const pg = g.append("g").attr("filter", blur("pb" + seed, 2.2 * u)); for (let i = 0; i < n; i++) { const x = X(rnd(seed + i) * 1.1 - 0.05), h = (0.18 + rnd(seed + i * 3) * 0.14) * H, k = 0.8 + rnd(i + seed) * 0.5, yy = Y(y0);
        pg.append("path").attr("d", `M ${x} ${yy} Q ${x + 10 * u} ${yy - h / 2} ${x - 6 * u} ${yy - h}`).attr("fill", "none").attr("stroke", f || "#6b5034").attr("stroke-width", 8 * u * k);
        for (let j = 0; j < 8; j++) pg.append("path").attr("d", `M ${x - 6 * u} ${yy - h} q ${46 * u * k * Math.cos(j * 0.8)} ${(-30 + 20 * Math.sin(j * 0.8)) * u * k} ${90 * u * k * Math.cos(j * 0.8)} ${(28 + 30 * Math.abs(Math.sin(j * 0.8))) * u * k}`).attr("fill", "none").attr("stroke", col).attr("stroke-width", 10 * u * k).attr("stroke-linecap", "round"); } };
    const hills = (y, col, sd, seed) => { const pts = []; for (let i = 0; i <= 12; i++) pts.push([X(i / 12 * 1.2 - 0.1), Y(y - 0.06 * rnd(seed + i))]); g.append("path").attr("d", `M ${X(-0.1)} ${Y(1.1)} L ` + pts.map((q) => q.join(" ")).join(" L ") + ` L ${X(1.1)} ${Y(1.1)} Z`).attr("fill", col).attr("filter", blur("h" + seed, sd * u)); };
    const clouds = (n, seed, col, op) => { for (let i = 0; i < n; i++) { const cg = g.append("g").attr("filter", blur("c" + seed + i, 2 * u)).attr("opacity", op), x = X(rnd(seed + i) * 1.0), y = Y(0.06 + rnd(seed + i * 5) * 0.25), k = (0.7 + rnd(i + 2) * 0.8) * u;
        for (const [dx, dy, r] of [[-40, 8, 34], [0, -10, 46], [44, 6, 32], [10, 16, 36]]) cg.append("circle").attr("cx", x + dx * k).attr("cy", y + dy * k).attr("r", r * k).attr("fill", col); } };
    if (name === "sky") {
      R(-0.2, -0.2, 1.4, 1.4, lg("s", [[0, "#7cc4ec"], [0.62, "#cfeaf8"], [1, "#eef8fd"]]));
      g.append("circle").attr("cx", X(0.82)).attr("cy", Y(0.14)).attr("r", 0.32 * Math.min(W, H)).attr("fill", rg("sun", [[0, "#fff6c8", 0.95], [0.35, "#fff1b0", 0.5], [1, "#fff1b0", 0]]));
      clouds(4, 3, "#fff", 0.92); hills(0.66, "#9cc79a", 3, 11); palms(0.72, 7, 21, "#3f7d3a"); hills(0.78, "#78b460", 1.2, 13);
    } else if (name === "night") {
      R(-0.2, -0.2, 1.4, 1.4, lg("s", [[0, "#07112a"], [0.7, "#1d3463"], [1, "#2c4a7c"]]));
      for (let i = 0; i < 70; i++) g.append("circle").attr("cx", X(rnd(i + 3) * 1.1 - 0.05)).attr("cy", Y(rnd(i + 9) * 0.6)).attr("r", (0.8 + rnd(i) * 1.8) * u).attr("fill", "#fff").attr("opacity", 0.4 + rnd(i + 1) * 0.6);
      g.append("circle").attr("cx", X(0.8)).attr("cy", Y(0.14)).attr("r", 0.22 * Math.min(W, H)).attr("fill", rg("moon", [[0, "#fff9d6", 0.45], [1, "#fff9d6", 0]]));
      hills(0.68, "#13284a", 2.5, 15); palms(0.74, 6, 31, "#0d1f33", "#0d1f33"); hills(0.8, "#0f2a1f", 1.2, 17);
    } else if (name === "storm") {
      R(-0.2, -0.2, 1.4, 1.4, lg("s", [[0, "#2c323d"], [0.6, "#5b6573"], [1, "#7d8896"]]));
      clouds(6, 41, "#4a515d", 0.95); hills(0.68, "#4b6150", 3, 19); palms(0.74, 6, 51, "#2f4a36", "#3b3027"); hills(0.8, "#3f5a3c", 1.2, 23);
    } else if (name === "dusk") {
      R(-0.2, -0.2, 1.4, 1.4, lg("s", [[0, "#f4c48e"], [1, "#fbe6c9"]]));
      R(-0.2, 0.74, 1.4, 0.5, lg("tab", [[0, "#9a6a3e"], [1, "#6f4a2a"]]));                     // a wooden table top
      R(-0.2, 0.74, 1.4, 0.012, "#c49260");
      const win = g.append("g").attr("filter", blur("win", 1.5 * u)).attr("opacity", 0.85);       // a soft window with light
      win.append("rect").attr("x", X(0.06)).attr("y", Y(0.08)).attr("width", 0.24 * W).attr("height", 0.36 * H).attr("rx", 10 * u).attr("fill", "#fff4d6");
      win.append("rect").attr("x", X(0.176)).attr("y", Y(0.08)).attr("width", 6 * u).attr("height", 0.36 * H).attr("fill", "#d9a86c"); win.append("rect").attr("x", X(0.06)).attr("y", Y(0.25)).attr("width", 0.24 * W).attr("height", 6 * u).attr("fill", "#d9a86c");
      g.append("circle").attr("cx", X(0.18)).attr("cy", Y(0.26)).attr("r", 0.45 * Math.min(W, H)).attr("fill", rg("wl", [[0, "#fff3cf", 0.55], [1, "#fff3cf", 0]]));
      const shelf = g.append("g").attr("filter", blur("sh", 1.8 * u)).attr("opacity", 0.7);
      shelf.append("rect").attr("x", X(0.62)).attr("y", Y(0.3)).attr("width", 0.34 * W).attr("height", 10 * u).attr("fill", "#8a5a33");
      for (let i = 0; i < 5; i++) shelf.append("rect").attr("x", X(0.64 + i * 0.065)).attr("y", Y(0.3) - (30 + rnd(i) * 30) * u).attr("width", 26 * u).attr("height", (30 + rnd(i) * 30) * u).attr("rx", 6 * u).attr("fill", ["#c45a2a", "#2f7d4f", "#e8a33d", "#1f8aa8", "#7b4a2b"][i]);
    } else if (name === "dark") {
      R(-0.2, -0.2, 1.4, 1.4, lg("s", [[0, "#1c140e"], [1, "#3d2b1d"]]));
      g.append("circle").attr("cx", X(0.5)).attr("cy", Y(0.45)).attr("r", 0.6 * Math.min(W, H)).attr("fill", rg("sp", [[0, "#ffd88a", 0.25], [1, "#ffd88a", 0]]));
    } else if (name === "soil") {
      R(-0.2, -0.2, 1.4, 1.4, lg("s", [[0, "#a77a4c"], [1, "#5e4027"]]));
      for (let i = 0; i < 60; i++) g.append("circle").attr("cx", X(rnd(i + 70))).attr("cy", Y(rnd(i + 80))).attr("r", (2 + rnd(i) * 6) * u).attr("fill", "#4a3220").attr("opacity", 0.35);
    } else return false;
    return true;
  }

  // ================= compose: a scene described as data (layers in drawing order, each with its own start/end as a fraction of the scene) =================
  // layer types: icon rect circle ellipse path text flow particles bolt flash rings spiral. Coordinates are 0..1 of the stage; "s" is an icon size multiplier.
  K.compose = (g, p, c) => {
    const { X, Y } = c, S = c.S * (c.wide ? 1.2 : 1), W = c.stage.w, H = c.stage.h, id = c.id + rid();
    const defs = M.svg.select("defs"), BG = { sky: [P.sky1, P.sky2], night: ["#0b1631", "#2a4472"], dusk: ["#f0a679", "#fde7c8"], dark: ["#17110c", "#3a2a1d"], storm: ["#3c4350", "#7a8493"], soil: ["#9a6f45", "#6a4a2c"] };
    const bgG = g.append("g"), world = g.append("g");
    if (!(p.flat || !drawSet(bgG, p.bg, c, id)) ) { /* painted set drawn */ } else if (BG[p.bg]) { const gr = defs.append("linearGradient").attr("id", id + "g").attr("x1", 0).attr("x2", 0).attr("y1", 0).attr("y2", 1); gr.append("stop").attr("offset", 0).attr("stop-color", BG[p.bg][0]); gr.append("stop").attr("offset", 1).attr("stop-color", BG[p.bg][1]);
      bgG.append("rect").attr("x", X(-0.2)).attr("y", Y(-0.2)).attr("width", W * 1.4).attr("height", H * 1.4).attr("fill", `url(#${id}g)`); }
    const ds = defs.append("filter").attr("id", id + "ds").attr("x", "-30%").attr("y", "-30%").attr("width", "160%").attr("height", "170%");
    ds.append("feDropShadow").attr("dx", 0).attr("dy", 7 * S).attr("stdDeviation", 6 * S).attr("flood-color", "#2a1a10").attr("flood-opacity", 0.28);
    const flashRect = g.append("rect").attr("x", X(0)).attr("y", Y(0)).attr("width", W).attr("height", H).attr("fill", "#fff").attr("opacity", 0);
    const ups = [];
    const pt = (o, k = "x") => [X(o[k] ?? 0.5), Y(o[k === "x" ? "y" : k + "y"] ?? 0.5)];
    const vis = (o, f) => prog(f, o.at ?? 0, 0.04) * (o.end != null ? 1 - prog(f, o.end, 0.04) : 1);
    const label = (grp, o) => { if (!o.label) return null; const l = o.label, lw = (l.w || 330) * S; return pill(grp, l.ml, l.en, (l.dx || 0) * S * 100, (l.dy ?? 1.3) * S * 100 + 0, l.col || P.brown, lw, 34 * S); };
    for (const o of p.layers || []) {
      const grp = world.append("g").attr("opacity", ["flow", "particles", "rings", "spiral"].includes(o.t) ? 1 : 0);
      const sty = (n) => n.attr("fill", o.fill || "none").attr("stroke", o.stroke || "none").attr("stroke-width", (o.sw || 4) * S).attr("fill-opacity", o.op ?? 1);
      if (o.t === "icon") {
        const ig = icon(grp, o.icon, 0, 0, (o.s || 1.5) * 100 * S); ig.attr("filter", `url(#${id}ds)`);
        if (o.glow) { const gid = id + "gl" + rid(), gr = defs.append("radialGradient").attr("id", gid); gr.append("stop").attr("offset", 0).attr("stop-color", o.glow).attr("stop-opacity", 0.75); gr.append("stop").attr("offset", 1).attr("stop-color", o.glow).attr("stop-opacity", 0);
          ig.insert("circle", ":first-child").attr("r", 60).attr("fill", `url(#${gid})`); }
        label(grp, o);
        const from = pt(o), to = o.to ? [X(o.to[0]), Y(o.to[1])] : from, ph = rnd((o.x || 0) * 99 + (o.y || 0) * 31);
        ups.push((lt, f, d) => { const mk = E.inOut(prog(f, o.mv ?? o.at ?? 0, o.dur ?? 0.2)), x = lerp(from[0], to[0], mk), y = lerp(from[1], to[1], mk);
          let dy = 0, sc = 0.45 + 0.55 * E.back(clamp((lt - (o.at ?? 0) * d) / 0.38)), rot = o.rot || 0, op = vis(o, f);
          if (o.anim === "float") dy = Math.sin(lt * 2 + ph * 6) * 10 * S; if (o.anim === "pulse") sc *= 1 + 0.12 * Math.sin(lt * 4 + ph * 6); if (o.anim === "spin") rot += lt * (o.speed || 120);
          if (o.anim === "shake") dy = Math.sin(lt * 40) * 4 * S; if (o.anim === "blink") op *= 0.25 + 0.75 * Math.max(0, Math.sin(lt * 3 + ph * 8));
          if (o.rise) dy -= lt * o.rise * S * 100;
          grp.attr("opacity", op).attr("transform", `translate(${x},${y + dy}) rotate(${rot}) scale(${sc})`); });
      } else if (o.t === "char") {        // a person: who = man | woman | kid | shopkeeper | student; mood = neutral | smile | wow | think | point; hold = an icon in the hand
        const cg = grp.append("g").attr("filter", `url(#${id}ds)`), parts = drawChar(cg, o.who || "man", o.mood || "neutral", o.hold), ph = rnd((o.x || 0) * 77 + 3), from = pt(o), to = o.to ? [X(o.to[0]), Y(o.to[1])] : from;
        if (o.label) { const l = o.label; pill(grp, l.ml, l.en, (l.dx || 0) * S * 100, 205 * (o.s || 1.6) * S, l.col || P.brown, (l.w || 330) * S, 34 * S); }
        ups.push((lt, f, d) => { const mk = E.inOut(prog(f, o.mv ?? o.at ?? 0, o.dur ?? 0.2)), x = lerp(from[0], to[0], mk), y = lerp(from[1], to[1], mk), k = E.back(clamp((lt - (o.at ?? 0) * d) / 0.4));
          const blink = ((lt * 0.7 + ph * 5) % 3) < 0.12 ? 0.1 : 1, tilt = Math.sin(lt * 1.6 + ph * 6) * 2.5, bob = Math.sin(lt * 2.2 + ph * 6) * 4 * S, flip = o.flip ? -1 : 1;
          parts.eyes.forEach((e) => e.attr("transform", `scale(1,${blink})`)); parts.head.attr("transform", `translate(0,-22) rotate(${tilt}) scale(${o.who === "kid" ? 1.15 : 1})`);
          grp.attr("opacity", vis(o, f)).attr("transform", `translate(${x},${y + bob})`);
          cg.attr("transform", `scale(${(o.s || 1.6) * S * (0.5 + 0.5 * k) * flip},${(o.s || 1.6) * S * (0.5 + 0.5 * k)})`); });
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
    // a directed camera: wide at the start, then it eases to each new thing as it appears, and back to wide near the end (p.cams overrides; p.still = no camera)
    const focus = (p.layers || []).filter((o) => (o.t === "icon" || o.t === "char") && (o.at ?? 0) > 0.03 && !o.bg).map((o) => ({ at: o.at, x: lerp(0.5, o.to ? o.to[0] : o.x, 0.6), y: lerp(0.5, o.to ? o.to[1] : o.y, 0.6), z: o.t === "char" ? 1.2 : 1.3 }));
    const cams = p.cams || [{ at: 0, x: 0.5, y: 0.5, z: 1.0 }, ...focus, ...(focus.length ? [{ at: Math.max(0.86, (focus[focus.length - 1].at || 0) + 0.12), x: 0.5, y: 0.5, z: 1.05 }] : [{ at: 0.02, x: 0.5, y: 0.5, z: 1.1, dur: 9 }])];
    cams.sort((a2, b2) => a2.at - b2.at);
    const camAt = (f, d) => { let i = 0; while (i + 1 < cams.length && cams[i + 1].at <= f) i++; const cur = cams[i], prev = cams[Math.max(0, i - 1)];
      if (i === 0 || cur.cut) return cur; const k = E.inOut(clamp(((f - cur.at) * d) / (cur.dur || 0.85))); return { x: lerp(prev.x, cur.x, k), y: lerp(prev.y, cur.y, k), z: lerp(prev.z ?? 1, cur.z ?? 1, k) }; };
    const cx0 = X(0.5), cy0 = Y(0.5);
    return (lt, d) => { const f = lt / d; flashRect.attr("opacity", 0); ups.forEach((u) => u(lt, f, d));
      if (p.still) return;
      const cm = camAt(f, d), z = Math.max(1, cm.z ?? 1), hw = 0.5 / z, x = Math.min(1 - hw, Math.max(hw, cm.x)), y = Math.min(1 - hw, Math.max(hw, cm.y));
      world.attr("transform", `translate(${cx0},${cy0}) scale(${z}) translate(${-X(x)},${-Y(y)})`);
      const zb = 1 + (z - 1) * 0.35, xb = 0.5 + (x - 0.5) * 0.35, yb = 0.5 + (y - 0.5) * 0.35;      // the background moves less: depth
      bgG.attr("transform", `translate(${cx0},${cy0}) scale(${zb}) translate(${-X(xb)},${-Y(yb)})`); };
  };

  // ---- shared helpers for the hand-made "set" scenes (1000 x 1000 units, filmed by a camera) ----
  function setKit(g, c, id) {
    const defs = M.svg.select("defs"), st = c.stage, U = Math.min(st.w, st.h) / 1000;
    const lg = (nm, stops, x2 = 0, y2 = 1) => { const gr = defs.append("linearGradient").attr("id", id + nm).attr("x1", 0).attr("y1", 0).attr("x2", x2).attr("y2", y2); stops.forEach(([o, col]) => gr.append("stop").attr("offset", o).attr("stop-color", col)); return `url(#${id + nm})`; };
    const rg = (nm, stops) => { const gr = defs.append("radialGradient").attr("id", id + nm); stops.forEach(([o, col, op]) => gr.append("stop").attr("offset", o).attr("stop-color", col).attr("stop-opacity", op ?? 1)); return `url(#${id + nm})`; };
    const blur = (nm, sd) => { defs.append("filter").attr("id", id + nm).attr("x", "-20%").attr("y", "-20%").attr("width", "140%").attr("height", "140%").append("feGaussianBlur").attr("stdDeviation", sd); return `url(#${id + nm})`; };
    const sh = defs.append("filter").attr("id", id + "dsh").attr("x", "-30%").attr("y", "-30%").attr("width", "160%").attr("height", "170%"); sh.append("feDropShadow").attr("dx", 0).attr("dy", 6).attr("stdDeviation", 6).attr("flood-color", "#2a1a10").attr("flood-opacity", 0.3);
    const glw = defs.append("filter").attr("id", id + "glw").attr("x", "-50%").attr("y", "-50%").attr("width", "200%").attr("height", "200%"); glw.append("feGaussianBlur").attr("stdDeviation", 6).attr("result", "b"); const m = glw.append("feMerge"); m.append("feMergeNode").attr("in", "b"); m.append("feMergeNode").attr("in", "SourceGraphic");
    const cam = g.append("g"), set = cam.append("g");
    const pill2 = (x, y, ml, en, col) => { const pg = set.append("g").attr("transform", `translate(${x},${y})`).attr("opacity", 0).attr("filter", `url(#${id}dsh)`); const w = 250, h = en ? 74 : 56;
      pg.append("rect").attr("x", -w / 2).attr("y", -h / 2).attr("width", w).attr("height", h).attr("rx", h / 2.4).attr("fill", col || "#c8442f");
      const t = pg.append("text").attr("y", en ? -2 : 9).attr("text-anchor", "middle").attr("fill", "#fff").attr("font-family", MAL).attr("font-weight", 800).text(ml); fit(t, 30, w - 24, 14);
      if (en) { const e = pg.append("text").attr("y", 24).attr("text-anchor", "middle").attr("fill", "#fff").attr("fill-opacity", 0.85).attr("font-weight", 700).attr("letter-spacing", 2).text(en); fit(e, 15, w - 24, 9); }
      return pg; };
    const camMover = (cams0) => { const cams = (cams0 && cams0.length ? cams0 : [{ at: 0, x: 500, y: 500, z: 1 }]).slice().sort((a2, b2) => a2.at - b2.at);
      return (f, d) => { let i = 0; while (i + 1 < cams.length && cams[i + 1].at <= f) i++; const cur = cams[i], prev = cams[Math.max(0, i - 1)];
        const v = i === 0 || cur.cut ? cur : (() => { const k = E.inOut(clamp(((f - cur.at) * d) / (cur.dur || 0.9))); return { x: lerp(prev.x, cur.x, k), y: lerp(prev.y, cur.y, k), z: lerp(prev.z, cur.z, k) }; })();
        cam.attr("transform", `translate(${st.x + st.w / 2},${st.y + st.h / 2}) scale(${U * v.z}) translate(${-v.x},${-v.y})`); }; };
    return { defs, lg, rg, blur, cam, set, pill2, camMover, sh: `url(#${id}dsh)`, glow: `url(#${id}glw)` };
  }

  // ================= home: a Kerala living room with a ceiling fan, an LED bulb, an AC and the electricity meter; each appliance shows how long it runs on 1 unit =================
  // p.items = [{icon: led|fan|ac, ml, en, at}], p.at = {meter}, p.cams (set units)
  K.home = (g, p, c) => {
    const id = c.id + rid(), k = setKit(g, c, id), s = k.set, a = p.at || {};
    s.append("rect").attr("x", -1300).attr("y", -300).attr("width", 3600).attr("height", 1600).attr("fill", k.lg("wall", [[0, "#f6e3c6"], [1, "#ecd2ab"]]));
    s.append("rect").attr("x", -1300).attr("y", 760).attr("width", 3600).attr("height", 600).attr("fill", k.lg("floor", [[0, "#a8774a"], [1, "#7a5232"]]));
    for (let i = 0; i < 30; i++) s.append("rect").attr("x", -1300 + i * 120).attr("y", 760).attr("width", 4).attr("height", 600).attr("fill", "#6d4a2c").attr("opacity", 0.35);
    s.append("rect").attr("x", -1300).attr("y", 744).attr("width", 3600).attr("height", 18).attr("fill", "#8a5d38");
    const win = s.append("g"); win.append("rect").attr("x", 330).attr("y", 300).attr("width", 260).attr("height", 300).attr("rx", 14).attr("fill", k.lg("win", [[0, "#bfe3f6"], [1, "#e9f6fc"]])).attr("stroke", "#8a5d38").attr("stroke-width", 14);
    win.append("rect").attr("x", 455).attr("y", 300).attr("width", 10).attr("height", 300).attr("fill", "#8a5d38"); win.append("rect").attr("x", 330).attr("y", 445).attr("width", 260).attr("height", 10).attr("fill", "#8a5d38");
    for (const [x, h] of [[370, 90], [420, 120], [540, 100]]) win.append("path").attr("d", `M ${x} 600 Q ${x + 6} ${600 - h / 2} ${x - 4} ${600 - h}`).attr("stroke", "#5b7a3a").attr("stroke-width", 5).attr("fill", "none");
    s.append("circle").attr("cx", 460).attr("cy", 450).attr("r", 330).attr("fill", k.rg("wl", [[0, "#fff6dd", 0.5], [1, "#fff6dd", 0]]));
    // sofa
    const sofa = s.append("g").attr("filter", k.sh); sofa.append("rect").attr("x", 300).attr("y", 640).attr("width", 330).attr("height", 120).attr("rx", 30).attr("fill", "#2f7d4f"); sofa.append("rect").attr("x", 285).attr("y", 600).attr("width", 360).attr("height", 70).attr("rx", 30).attr("fill", "#3a915d");
    // appliances
    const fan = s.append("g").attr("transform", "translate(460,140)"); fan.append("rect").attr("x", -5).attr("y", -140).attr("width", 10).attr("height", 120).attr("fill", "#6b6f75"); fan.append("circle").attr("r", 26).attr("fill", "#8d939b").attr("filter", k.sh);
    const blades = fan.append("g"); for (let i = 0; i < 3; i++) blades.append("path").attr("d", "M 0 -8 L 210 -22 Q 226 0 210 22 L 0 8 Z").attr("fill", "#d9d2c6").attr("stroke", "#9b9488").attr("stroke-width", 3).attr("transform", `rotate(${i * 120})`);
    const bulb = s.append("g").attr("transform", "translate(150,250)"); bulb.append("rect").attr("x", -3).attr("y", -260).attr("width", 6).attr("height", 230).attr("fill", "#555");
    const bglow = bulb.append("circle").attr("r", 150).attr("fill", k.rg("bg", [[0, "#fff1a8", 0.85], [1, "#fff1a8", 0]])).attr("opacity", 0);
    bulb.append("path").attr("d", "M -30 -30 L 30 -30 L 22 0 L -22 0 Z").attr("fill", "#3c3c42"); const bb = bulb.append("circle").attr("cy", 22).attr("r", 30).attr("fill", "#fffbe6").attr("stroke", "#c9c2a8").attr("stroke-width", 3);
    const ac = s.append("g").attr("transform", "translate(800,230)").attr("filter", k.sh); ac.append("rect").attr("x", -140).attr("y", -45).attr("width", 280).attr("height", 90).attr("rx", 18).attr("fill", "#f4f6f8").attr("stroke", "#b9c1c8").attr("stroke-width", 3);
    ac.append("rect").attr("x", -120).attr("y", 18).attr("width", 240).attr("height", 10).attr("rx", 5).attr("fill", "#c9d1d8"); const acLed = ac.append("circle").attr("cx", 110).attr("cy", -22).attr("r", 6).attr("fill", "#2ecc71").attr("opacity", 0);
    const airs = Array.from({ length: 7 }, (_, i) => s.append("path").attr("fill", "none").attr("stroke", "#9fd8f5").attr("stroke-width", 6).attr("stroke-linecap", "round").attr("opacity", 0).datum(i));
    const meterBox = s.append("g").attr("transform", "translate(860,520)").attr("filter", k.sh); meterBox.append("rect").attr("x", -70).attr("y", -95).attr("width", 140).attr("height", 190).attr("rx", 14).attr("fill", "#e9e2d4").attr("stroke", "#7b6e5a").attr("stroke-width", 5);
    meterBox.append("rect").attr("x", -52).attr("y", -70).attr("width", 104).attr("height", 44).attr("rx", 6).attr("fill", "#0e1a14"); const digits = meterBox.append("text").attr("y", -38).attr("text-anchor", "middle").attr("fill", "#7dffb0").attr("font-weight", 800).attr("font-size", 30).text("0000");
    meterBox.append("circle").attr("cy", 30).attr("r", 30).attr("fill", "none").attr("stroke", "#4a3a28").attr("stroke-width", 5); const needle = meterBox.append("path").attr("d", "M 0 30 L 0 6").attr("stroke", "#c8442f").attr("stroke-width", 5).attr("stroke-linecap", "round");
    meterBox.append("text").attr("y", 82).attr("text-anchor", "middle").attr("fill", "#4a3a28").attr("font-weight", 800).attr("font-size", 18).text("kWh");
    const where = { led: [150, 330], fan: [460, 240], ac: [800, 330] };
    const items = (p.items || []).map((it) => { const [x, y] = where[it.icon] || [500, 500]; return { it, tag: k.pill2(x, y + 80, it.ml, it.en, it.col || "#c8442f") }; });
    const meterTag = k.pill2(860, 680, "1 യൂണിറ്റ് = 1 kWh", "ONE UNIT", "#2f7d4f");
    const move = k.camMover(p.cams);
    return (lt, d) => { const f = lt / d; move(f, d);
      const on = (key) => items.some((q) => q.it.icon === key && f >= (q.it.at ?? 0));
      blades.attr("transform", `rotate(${on("fan") ? lt * 620 : lt * 20})`);
      bglow.attr("opacity", on("led") ? 0.9 + 0.1 * Math.sin(lt * 3) : 0); bb.attr("fill", on("led") ? "#fff7b8" : "#f4f1e6");
      acLed.attr("opacity", on("ac") ? 1 : 0); airs.forEach((q) => { const i = q.datum(), u = (lt * 0.7 + i / 7) % 1; q.attr("d", `M ${700 + i * 30} ${280 + u * 160} q 10 18 0 36`).attr("opacity", on("ac") ? 0.7 * (1 - u) : 0); });
      items.forEach((q) => { const kk = E.back(clamp(((f - (q.it.at ?? 0)) * d) / 0.4)); q.tag.attr("opacity", clamp(kk * 2)).attr("transform", `translate(${(where[q.it.icon] || [500])[0]},${(where[q.it.icon] || [0, 500])[1] + 80}) scale(${0.6 + 0.4 * kk})`); });
      const units = (on("led") ? 0.2 : 0) + (on("fan") ? 1 : 0) + (on("ac") ? 6 : 0); digits.text(String(Math.floor(lt * (1 + units) * 3) % 10000).padStart(4, "0")); needle.attr("transform", `rotate(${lt * (40 + units * 90)} 0 30)`);
      const mk = E.back(clamp(((f - at(a, "meter")) * d) / 0.4)); meterTag.attr("opacity", clamp(mk * 2)).attr("transform", `translate(860,680) scale(${0.6 + 0.4 * mk})`); };
  };

  // ================= damx: the Idukki story drawn as a valley: reservoir behind an arch dam, a tunnel through the rock, and the underground power house with spinning turbines =================
  // p.at = {height, tunnel, house, spin, flow}, p.cams (set units)
  K.damx = (g, p, c) => {
    const id = c.id + rid(), k = setKit(g, c, id), s = k.set, a = p.at || {};
    s.append("rect").attr("x", -1400).attr("y", -400).attr("width", 3800).attr("height", 1800).attr("fill", k.lg("sky", [[0, "#7cc4ec"], [0.5, "#d6eef9"], [1, "#eef8fd"]]));
    s.append("path").attr("d", "M -1400 380 Q -800 200 -400 420 Q -100 140 200 300 Q 360 380 470 330 Q 620 160 900 260 Q 1100 330 1400 220 Q 1900 160 2400 300 L 2400 1400 L -1400 1400 Z").attr("fill", "#7fa77a").attr("filter", k.blur("far", 3));
    // the cut-away rock and ground
    s.append("path").attr("d", "M -1400 470 L -400 470 Q 100 430 330 470 L 470 470 Q 700 520 1400 500 L 2400 500 L 2400 1400 L -1400 1400 Z").attr("fill", k.lg("rock", [[0, "#9b7a55"], [1, "#5d432c"]]));
    s.append("path").attr("d", "M -1400 470 L -400 470 Q 100 430 330 470 L 470 470 Q 700 520 1400 500 L 2400 500 L 2400 528 L 1400 528 Q 700 548 470 498 L 330 498 Q 100 458 -400 498 L -1400 498 Z").attr("fill", "#4f8f3a");
    for (let i = 0; i < 80; i++) s.append("circle").attr("cx", -1300 + rnd(i + 5) * 3600).attr("cy", 560 + rnd(i + 9) * 600).attr("r", 4 + rnd(i) * 9).attr("fill", "#4a3524").attr("opacity", 0.35);
    // reservoir water with a shine, and the arch dam
    const water = s.append("path").attr("fill", k.lg("water", [[0, "#2f8fc0"], [1, "#165d84"]]));
    const shine = s.append("path").attr("fill", "none").attr("stroke", "#bfe8fb").attr("stroke-width", 4).attr("opacity", 0.6);
    const dam = s.append("g").attr("filter", k.sh);
    dam.append("path").attr("d", "M 320 300 Q 360 285 400 300 L 440 520 L 300 520 Z").attr("fill", k.lg("dam", [[0, "#c9cfd4"], [0.5, "#aab3ba"], [1, "#8b959d"]], 1, 0));
    for (let i = 1; i < 6; i++) dam.append("path").attr("d", `M ${320 + i * 3} ${300 + i * 37} L ${400 + i * 7} ${300 + i * 37}`).attr("stroke", "#9aa3aa").attr("stroke-width", 2);
    const hArrow = s.append("g").attr("opacity", 0); hArrow.append("path").attr("d", "M 470 300 L 470 520 M 460 312 L 470 298 L 480 312 M 460 508 L 470 522 L 480 508").attr("stroke", "#c8442f").attr("stroke-width", 6).attr("fill", "none");
    const hTag = k.pill2(590, 410, "≈ 169 മീറ്റർ", "DAM HEIGHT", "#c8442f");
    // the tunnel: an intake below the water, through the rock to the power house
    const tunnel = [[300, 470], [380, 600], [560, 660], [760, 700], [840, 760]];
    s.append("path").attr("d", smooth(tunnel)).attr("fill", "none").attr("stroke", "#2b1d12").attr("stroke-width", 40).attr("stroke-linecap", "round").attr("opacity", 0.75);
    const flowP = s.append("path").attr("d", smooth(tunnel)).attr("fill", "none").attr("stroke", "#7fd0ee").attr("stroke-width", 20).attr("stroke-linecap", "round").attr("stroke-dasharray", "30 24").attr("opacity", 0);
    const tTag = k.pill2(580, 610, "തുരങ്കം", "TUNNEL", "#4a2a17");
    // the underground power house, cut open
    const ph = s.append("g"); ph.append("rect").attr("x", 760).attr("y", 720).attr("width", 300).attr("height", 200).attr("rx", 26).attr("fill", k.lg("ph", [[0, "#3a2a1d"], [1, "#22170f"]])).attr("stroke", "#c49260").attr("stroke-width", 6);
    ph.append("rect").attr("x", 780).attr("y", 880).attr("width", 260).attr("height", 14).attr("fill", "#5a4532");
    const lamps = [820, 900, 980].map((x) => ph.append("circle").attr("cx", x).attr("cy", 740).attr("r", 40).attr("fill", k.rg("lp" + x, [[0, "#ffe9a8", 0.6], [1, "#ffe9a8", 0]])));
    const turbines = [840, 940].map((x) => { const tg = ph.append("g").attr("transform", `translate(${x},830)`); tg.append("circle").attr("r", 40).attr("fill", "#5e6b78");
      const rot = tg.append("g"); for (let i = 0; i < 8; i++) rot.append("path").attr("d", "M 0 -38 Q 14 -50 22 -36 L 6 -20 Z").attr("fill", "#f6b945").attr("transform", `rotate(${i * 45})`); tg.append("circle").attr("r", 9).attr("fill", "#2a2f35"); return rot; });
    const gens = [1000].map((x) => { const gg = ph.append("g").attr("transform", `translate(${x},825)`); gg.append("rect").attr("x", -32).attr("y", -40).attr("width", 64).attr("height", 80).attr("rx", 12).attr("fill", "#8d99a6"); const bolt = gg.append("path").attr("d", "M 6 -26 L -12 4 L 0 4 L -6 28 L 14 -4 L 2 -4 Z").attr("fill", "#ffd84a").attr("filter", k.glow); return bolt; });
    const pTag = k.pill2(910, 980, "ഭൂഗർഭ പവർഹൗസ്", "UNDERGROUND POWER HOUSE", "#2f7d4f");
    const jets = Array.from({ length: 12 }, () => ph.append("circle").attr("r", 7).attr("fill", "#bfe8fb").attr("opacity", 0));
    const move = k.camMover(p.cams);
    return (lt, d) => { const f = lt / d; move(f, d);
      const lvl = 350 + Math.sin(lt * 0.8) * 3; water.attr("d", `M -1400 ${lvl} Q 0 ${lvl - 4} 330 ${lvl} L 330 520 L -1400 520 Z`);
      shine.attr("d", `M -300 ${lvl + 20} q 60 ${-6 + Math.sin(lt * 2) * 4} 120 0 t 120 0 t 120 0`);
      const hk = E.back(clamp(((f - at(a, "height")) * d) / 0.4)); hArrow.attr("opacity", clamp(hk * 2)); hTag.attr("opacity", clamp(hk * 2)).attr("transform", `translate(590,410) scale(${0.6 + 0.4 * hk})`);
      const fl = prog(f, at(a, "flow", at(a, "tunnel")), 0.03); flowP.attr("opacity", fl).attr("stroke-dashoffset", -lt * 140);
      const tk = E.back(clamp(((f - at(a, "tunnel")) * d) / 0.4)); tTag.attr("opacity", clamp(tk * 2)).attr("transform", `translate(580,610) scale(${0.6 + 0.4 * tk})`);
      const pk = E.back(clamp(((f - at(a, "house")) * d) / 0.4)); pTag.attr("opacity", clamp(pk * 2)).attr("transform", `translate(910,980) scale(${0.6 + 0.4 * pk})`);
      const sp = prog(f, at(a, "spin"), 0.04); turbines.forEach((r, i) => r.attr("transform", `rotate(${lt * 420 * sp + i * 20})`)); gens.forEach((b) => b.attr("opacity", sp > 0.5 ? 0.6 + 0.4 * Math.sin(lt * 12) : 0.15));
      lamps.forEach((l, i) => l.attr("opacity", 0.7 + 0.3 * Math.sin(lt * 2 + i)));
      jets.forEach((q, i) => { const u = (lt * 0.9 + i / 12) % 1; q.attr("cx", 800 + u * 40).attr("cy", 770 + u * 50).attr("opacity", fl * (1 - u)); }); };
  };

  // ================= crow: a richly drawn power-line scene with a directed camera (wide shot, close-ups on the feet, the danger moment) =================
  // the scene is drawn in a 1000 x 1000 "set" and filmed by a camera: p.cams = [{at, x, y, z, cut}] (at = fraction of the scene); p.at = {badges, meter, ok, danger, man}
  K.crow = (g, p, c) => {
    const { stage } = c, id = c.id + rid(), a = p.at || {}, defs = M.svg.select("defs");
    const sx = stage.w / 1000, sy = stage.h / 1000, U = Math.min(sx, sy);
    const lg = (nm, stops, x2 = 0, y2 = 1) => { const gr = defs.append("linearGradient").attr("id", id + nm).attr("x1", 0).attr("y1", 0).attr("x2", x2).attr("y2", y2); stops.forEach(([o, col]) => gr.append("stop").attr("offset", o).attr("stop-color", col)); return `url(#${id + nm})`; };
    const rg = (nm, stops) => { const gr = defs.append("radialGradient").attr("id", id + nm); stops.forEach(([o, col, op]) => gr.append("stop").attr("offset", o).attr("stop-color", col).attr("stop-opacity", op ?? 1)); return `url(#${id + nm})`; };
    const blur = (nm, sd) => { defs.append("filter").attr("id", id + nm).attr("x", "-20%").attr("y", "-20%").attr("width", "140%").attr("height", "140%").append("feGaussianBlur").attr("stdDeviation", sd); return `url(#${id + nm})`; };
    const glowF = defs.append("filter").attr("id", id + "glow").attr("x", "-50%").attr("y", "-50%").attr("width", "200%").attr("height", "200%");
    glowF.append("feGaussianBlur").attr("stdDeviation", 6).attr("result", "b"); const mg = glowF.append("feMerge"); mg.append("feMergeNode").attr("in", "b"); mg.append("feMergeNode").attr("in", "SourceGraphic");
    // the camera group: everything below is in set units (0..1000), mapped onto the stage, then moved by the camera
    const cam = g.append("g"), set = cam.append("g");
    set.append("rect").attr("x", -400).attr("y", -400).attr("width", 1800).attr("height", 1800).attr("fill", lg("sky", [[0, "#7cc4ec"], [0.6, "#cfeaf8"], [1, "#eef8fd"]]));
    set.append("circle").attr("cx", 820).attr("cy", 150).attr("r", 260).attr("fill", rg("sun", [[0, "#fff6c8", 0.95], [0.35, "#fff1b0", 0.5], [1, "#fff1b0", 0]]));
    const clouds = [[150, 160, 1], [520, 90, 0.8], [900, 260, 1.2]].map(([x, y, k], i) => { const cg = set.append("g").attr("filter", blur("cb" + i, 2)); for (const [dx, dy, r] of [[-40, 8, 34], [0, -10, 46], [44, 6, 32], [10, 16, 36]]) cg.append("circle").attr("cx", dx * k).attr("cy", dy * k).attr("r", r * k).attr("fill", "#fff").attr("opacity", 0.92); return { cg, x, y, sp: 6 + i * 3 }; });
    set.append("path").attr("d", "M -400 640 Q 100 520 420 600 Q 700 660 1000 560 Q 1200 520 1400 600 L 1400 1400 L -400 1400 Z").attr("fill", "#8fbf8a").attr("filter", blur("hill", 3));
    const palms = set.append("g").attr("filter", blur("palm", 1.6)).attr("opacity", 0.95);
    for (const [x, h, k] of [[60, 260, 1], [230, 300, 1.15], [700, 280, 1.05], [880, 320, 1.2], [1020, 260, 1]]) { const pg = palms.append("g").attr("transform", `translate(${x},640) scale(${k})`);
      pg.append("path").attr("d", `M 0 0 Q 10 ${-h / 2} -6 ${-h}`).attr("fill", "none").attr("stroke", "#6b5034").attr("stroke-width", 9);
      for (let i = 0; i < 8; i++) pg.append("path").attr("d", `M -6 ${-h} q ${40 * Math.cos(i * 0.8)} ${-30 + 20 * Math.sin(i * 0.8)} ${80 * Math.cos(i * 0.8)} ${30 + 30 * Math.abs(Math.sin(i * 0.8))}`).attr("fill", "none").attr("stroke", "#3f7d3a").attr("stroke-width", 10).attr("stroke-linecap", "round"); }
    set.append("rect").attr("x", -400).attr("y", 700).attr("width", 1800).attr("height", 700).attr("fill", lg("grass", [[0, "#86c35b"], [1, "#4c8f36"]]));
    for (let i = 0; i < 160; i++) { const x = -300 + rnd(i) * 1600, y = 710 + rnd(i + 7) * 290; set.append("path").attr("d", `M ${x} ${y} l ${-4 + rnd(i + 3) * 8} -14`).attr("stroke", "#3d7a2c").attr("stroke-width", 3).attr("opacity", 0.6); }
    // poles, crossarms, insulators, three wires with sag
    const poleX = [130, 870], wireY = [300, 380, 460], sag = 34;
    poleX.forEach((x) => { set.append("rect").attr("x", x - 13).attr("y", 250).attr("width", 26).attr("height", 560).attr("fill", lg("pole" + x, [[0, "#8a6a48"], [0.5, "#b08a60"], [1, "#6d5136"]], 1, 0));
      set.append("rect").attr("x", x - 80).attr("y", 262).attr("width", 160).attr("height", 16).attr("rx", 4).attr("fill", "#6d5136");
      wireY.forEach((y) => set.append("rect").attr("x", x - 7).attr("y", y - 22).attr("width", 14).attr("height", 24).attr("rx", 5).attr("fill", "#e8eef2").attr("stroke", "#9aa6ad")); });
    const wirePt = (k, x) => { const u = (x - poleX[0]) / (poleX[1] - poleX[0]); return wireY[k] + sag * Math.sin(Math.PI * Math.min(1, Math.max(0, u))); };
    const wires = wireY.map((y, k) => { const pts = []; for (let x = poleX[0] - 200; x <= poleX[1] + 200; x += 20) pts.push([x, wirePt(k, x)]); set.append("path").attr("d", basis(pts)).attr("fill", "none").attr("stroke", "#20262b").attr("stroke-width", 5);
      return set.append("path").attr("d", basis(pts)).attr("fill", "none").attr("stroke", "#9fdcff").attr("stroke-width", 3).attr("stroke-dasharray", "10 26").attr("opacity", 0.55); });
    // the crow, on the middle wire
    const bx = 500, by = wirePt(1, 500);
    const crow = set.append("g").attr("transform", `translate(${bx},${by})`);
    const legs = crow.append("g");
    for (const lx of [-18, 16]) { legs.append("path").attr("d", `M ${lx} -34 L ${lx + 2} -6`).attr("stroke", "#2c2c30").attr("stroke-width", 6).attr("stroke-linecap", "round");
      legs.append("path").attr("d", `M ${lx - 10} -2 Q ${lx + 2} -12 ${lx + 14} -2`).attr("fill", "none").attr("stroke", "#2c2c30").attr("stroke-width", 5).attr("stroke-linecap", "round"); }
    const body = crow.append("g").attr("transform", "translate(0,-40)");
    body.append("path").attr("d", "M -120 -10 L -175 18 L -160 30 L -110 14 Z").attr("fill", "#141418");
    body.append("ellipse").attr("cx", -6).attr("cy", -14).attr("rx", 92).attr("ry", 52).attr("fill", lg("body", [[0, "#2b2b31"], [1, "#0d0d10"]]));
    const wing = body.append("g");
    wing.append("path").attr("d", "M -90 -30 Q -10 -64 60 -30 Q 20 10 -100 6 Z").attr("fill", lg("wing", [[0, "#26262c"], [1, "#09090b"]]));
    for (let i = 0; i < 5; i++) wing.append("path").attr("d", `M ${-80 + i * 26} -18 q 14 10 24 4`).attr("fill", "none").attr("stroke", "#3b3b44").attr("stroke-width", 3);
    const head = body.append("g").attr("transform", "translate(78,-60)");
    head.append("ellipse").attr("cx", -18).attr("cy", 24).attr("rx", 46).attr("ry", 36).attr("fill", "#7a7a82");
    head.append("circle").attr("r", 40).attr("fill", lg("head", [[0, "#2a2a30"], [1, "#101014"]]));
    head.append("path").attr("d", "M 30 -10 L 96 4 L 30 16 Z").attr("fill", "#1e1e22"); head.append("path").attr("d", "M 30 -10 L 96 4 L 30 2 Z").attr("fill", "#3a3a42");
    const eye = head.append("g").attr("transform", "translate(14,-8)"); eye.append("circle").attr("r", 13).attr("fill", "#f4f1e8"); const pupil = eye.append("circle").attr("cx", 3).attr("r", 7).attr("fill", "#111"); eye.append("circle").attr("cx", 6).attr("cy", -4).attr("r", 3).attr("fill", "#fff");
    // overlays: voltage badges at the feet, a meter, check and cross, the current path and spark for the danger moment
    const badge = (x, y, txt) => { const bgp = set.append("g").attr("transform", `translate(${x},${y})`).attr("opacity", 0); bgp.append("rect").attr("x", -62).attr("y", -20).attr("width", 124).attr("height", 40).attr("rx", 20).attr("fill", "#c8442f"); bgp.append("text").attr("y", 8).attr("text-anchor", "middle").attr("fill", "#fff").attr("font-weight", 800).attr("font-size", 22).text(txt); return bgp; };
    const b1 = badge(bx - 60, by + 46, "11,000 V"), b2 = badge(bx + 60, by + 46, "11,000 V");
    const meter = set.append("g").attr("transform", `translate(${bx},${by + 150})`).attr("opacity", 0);
    meter.append("rect").attr("x", -120).attr("y", -56).attr("width", 240).attr("height", 112).attr("rx", 22).attr("fill", "#1b2226").attr("stroke", "#5b6a72").attr("stroke-width", 4);
    meter.append("rect").attr("x", -100).attr("y", -40).attr("width", 200).attr("height", 58).attr("rx", 10).attr("fill", "#0c1a12");
    meter.append("text").attr("y", 6).attr("text-anchor", "middle").attr("fill", "#7dffb0").attr("font-weight", 800).attr("font-size", 46).text("0 V");
    meter.append("text").attr("y", 44).attr("text-anchor", "middle").attr("fill", "#cfd8dc").attr("font-family", MAL).attr("font-weight", 700).attr("font-size", 17).text("വോൾട്ടേജ് വ്യത്യാസം");
    const mark = (ok) => { const mg2 = set.append("g").attr("opacity", 0); mg2.append("circle").attr("r", 34).attr("fill", ok ? "#2f9d57" : "#d23c2a").attr("stroke", "#fff").attr("stroke-width", 5); mg2.append("path").attr("d", ok ? "M -16 0 L -4 12 L 18 -12" : "M -13 -13 L 13 13 M 13 -13 L -13 13").attr("fill", "none").attr("stroke", "#fff").attr("stroke-width", 8).attr("stroke-linecap", "round"); return mg2; };
    const okM = mark(true), noM = mark(false);
    const path = set.append("path").attr("d", `M ${bx - 18} ${by} Q ${bx - 40} ${by - 80} ${bx - 30} ${by - 120} Q ${bx - 10} ${by - 150} ${bx - 20} ${wirePt(0, bx - 20)}`).attr("fill", "none").attr("stroke", "#ffd84a").attr("stroke-width", 9).attr("stroke-dasharray", "18 14").attr("filter", `url(#${id}glow)`).attr("opacity", 0);
    const spark = set.append("g").attr("transform", `translate(${bx - 20},${wirePt(0, bx - 20)})`).attr("opacity", 0);
    for (let i = 0; i < 10; i++) spark.append("path").attr("d", `M 0 0 L ${Math.cos(i * 0.63) * 46} ${Math.sin(i * 0.63) * 46}`).attr("stroke", "#fff2a8").attr("stroke-width", 6).attr("stroke-linecap", "round");
    const cams = (p.cams && p.cams.length ? p.cams : [{ at: 0, x: 500, y: 450, z: 1 }]).slice().sort((u, v) => u.at - v.at);
    const camAt = (f, d) => { let i = 0; while (i + 1 < cams.length && cams[i + 1].at <= f) i++; const cur = cams[i], prev = cams[Math.max(0, i - 1)];
      if (i === 0 || cur.cut) return cur; const k = E.inOut(clamp(((f - cur.at) * d) / (cur.dur || 0.9))); return { x: lerp(prev.x, cur.x, k), y: lerp(prev.y, cur.y, k), z: lerp(prev.z, cur.z, k) }; };
    return (lt, d) => {
      const f = lt / d, cm = camAt(f, d), dang = prog(f, at(a, "danger"), 0.02), shake = dang > 0 && f - at(a, "danger") < 0.06 ? Math.sin(lt * 70) * 6 : 0;
      cam.attr("transform", `translate(${stage.x + stage.w / 2 + shake},${stage.y + stage.h / 2}) scale(${U * cm.z}) translate(${-cm.x},${-cm.y})`);
      clouds.forEach((q) => q.cg.attr("transform", `translate(${((q.x + lt * q.sp) % 1300) - 150},${q.y})`));
      wires.forEach((w, k) => w.attr("stroke-dashoffset", -lt * (40 + k * 6)));
      const bob = Math.sin(lt * 3.2) * 2, look = Math.sin(lt * 0.9) > 0.6 ? 6 : 0;
      body.attr("transform", `translate(0,${-40 + bob})`); head.attr("transform", `translate(78,${-60 + bob * 0.5}) rotate(${Math.sin(lt * 1.3) * 6})`); pupil.attr("cx", 3 + look);
      wing.attr("transform", dang > 0 ? `rotate(${-58 * E.out(dang)} -60 -20)` : `rotate(${Math.sin(lt * 9) * 1.5} -60 -20)`);
      const bb = E.back(prog(f, at(a, "badges"), 0.04)); b1.attr("opacity", clamp(bb * 2)).attr("transform", `translate(${bx - 60},${by + 46}) scale(${0.6 + 0.4 * bb})`); b2.attr("opacity", clamp(bb * 2)).attr("transform", `translate(${bx + 60},${by + 46}) scale(${0.6 + 0.4 * bb})`);
      meter.attr("opacity", prog(f, at(a, "meter"), 0.04) * (1 - dang));
      const ok = E.back(prog(f, at(a, "ok"), 0.04)); okM.attr("opacity", clamp(ok * 2) * (1 - dang)).attr("transform", `translate(${bx + 170},${by + 150}) scale(${0.5 + 0.5 * ok})`);
      path.attr("opacity", dang).attr("stroke-dashoffset", -lt * 160); spark.attr("opacity", dang > 0 ? 0.5 + 0.5 * Math.sin(lt * 50) : 0).attr("transform", `translate(${bx - 20},${wirePt(0, bx - 20)}) scale(${0.7 + 0.3 * Math.sin(lt * 31)})`);
      const nx = E.back(prog(f, at(a, "danger") + 0.04, 0.04)); noM.attr("opacity", clamp(nx * 2)).attr("transform", `translate(${bx + 150},${by - 190}) scale(${0.5 + 0.5 * nx})`);
    };
  };

  // ================= the runner (v3): bilingual cards on top (as in the first videos), scenes change with a cut, whip, zoom or flash, a gentle punch on every beat =================
  SCENES.chaya = (g, s) => {
    const W = M.W, H = M.H, wide = W > H, id = "cz" + rid();
    const stage = wide ? { x: 0, y: 215, w: W, h: H - 215 - 20 } : { x: 0, y: 330, w: W, h: 1420 };
    const c = { W, H, wide, stage, X: (u) => stage.x + u * stage.w, Y: (v) => stage.y + v * stage.h, S: Math.min(stage.w, stage.h) / 1000, id };
    const defs = M.svg.select("defs"), cx = W / 2, cy = stage.y + stage.h / 2;
    const sh = defs.append("filter").attr("id", id + "sh").attr("x", "-20%").attr("y", "-20%").attr("width", "140%").attr("height", "150%");
    sh.append("feDropShadow").attr("dx", 0).attr("dy", 8).attr("stdDeviation", 9).attr("flood-color", P.ink).attr("flood-opacity", 0.35);
    defs.append("clipPath").attr("id", id + "cl").append("rect").attr("x", 0).attr("y", stage.y).attr("width", W).attr("height", H - stage.y);
    g.append("rect").attr("width", W).attr("height", H).attr("fill", P.cream);
    const dotsBg = g.append("g").attr("opacity", 0.07);
    for (let x = 30; x < W; x += 70) for (let y = 30; y < H; y += 70) dotsBg.append("circle").attr("cx", x).attr("cy", y).attr("r", 4).attr("fill", P.brown);
    const world = g.append("g").attr("clip-path", `url(#${id}cl)`);
    const scenes = s.scenes.map((sc) => { const grp = world.append("g").attr("opacity", 0).attr("display", "none"); const upd = K[sc.kind](grp, sc.p || {}, c); return { grp, upd, t0: sc.t0, t1: sc.t1, tr: sc.tr || "fade", kind: sc.kind }; });
    const cardW = wide ? Math.min(1200, W * 0.64) : 900, cardH = wide ? 150 : 190, cardY = wide ? 118 : 215;
    const cards = (s.cards || []).map((cd) => { const grp = g.append("g").attr("opacity", 0), col = cd.col || P.brown;
      grp.append("rect").attr("x", -cardW / 2).attr("y", -cardH / 2).attr("width", cardW).attr("height", cardH).attr("rx", 40).attr("fill", col).attr("filter", `url(#${id}sh)`);
      grp.append("rect").attr("x", -cardW / 2 + 8).attr("y", -cardH / 2 + 8).attr("width", cardW - 16).attr("height", cardH - 16).attr("rx", 34).attr("fill", "none").attr("stroke", "#fff").attr("stroke-opacity", 0.28).attr("stroke-width", 3);
      const tml = grp.append("text").attr("y", -cardH * 0.02).attr("text-anchor", "middle").attr("fill", "#fff").attr("font-weight", 800).attr("font-family", MAL).text(cd.ml); fit(tml, wide ? 76 : 84, cardW - 70, 30);
      if (cd.en) { const ten = grp.append("text").attr("y", cardH * (wide ? 0.38 : 0.37)).attr("text-anchor", "middle").attr("fill", "#fff").attr("fill-opacity", 0.86).attr("font-weight", 600).attr("letter-spacing", 4).text(cd.en); fit(ten, wide ? 26 : 30, cardW - 70, 12); }
      return { grp, t0: cd.t0, t1: cd.t1 }; });
    const flash = g.append("rect").attr("width", W).attr("height", H).attr("fill", "#fffbe8").attr("opacity", 0);
    const bar = g.append("rect").attr("x", 0).attr("y", H - 8).attr("height", 8).attr("fill", P.amber);
    g.append("text").attr("x", wide ? 36 : 40).attr("y", wide ? 52 : 84).attr("fill", P.brown).attr("fill-opacity", 0.7).attr("font-family", MAL).attr("font-weight", 800).attr("font-size", wide ? 34 : 38).text("സയൻസ് ചായ");
    const T = s.duration, beats = s.beats || [];
    return (t) => {
      let b0 = -99; for (const b of beats) { if (b <= t) b0 = b; else break; }
      let fl = 0;
      scenes.forEach((sc, i) => {
        const last = i === scenes.length - 1, next = scenes[i + 1], out = next ? ({ whip: 0.3, fade: 0.3 }[next.tr] || 0) : 0, vis = t >= sc.t0 - 0.02 && (last || t < sc.t1 + out);
        sc.grp.attr("display", vis ? null : "none");
        if (!vis) return;
        const tin = clamp((t - sc.t0) / 0.3), te = E.out(tin);
        let dx = 0, sz = 1, op = 1;
        if (sc.tr === "whip") dx = (1 - te) * W * 0.6; else if (sc.tr === "zoom") { sz = 1.22 - 0.22 * te; op = Math.min(1, tin * 3); } else if (sc.tr === "fade") op = tin; else if (sc.tr === "flash" && t - sc.t0 < 0.25) fl = Math.max(fl, 0.85 * (1 - (t - sc.t0) / 0.25));
        if (next && t >= sc.t1) { const k = clamp((t - sc.t1) / Math.max(0.01, out)); if (next.tr === "whip") dx = -Math.pow(k, 2) * W * 0.6; else op *= 1 - k; }
        const punch = sc.kind === "outro" ? 0 : 0.035 * (1 - E.out(clamp((t - b0) / 0.35)));       // a small push on every new sentence, never a crop
        sz *= 1 + punch;
        sc.grp.attr("opacity", op).attr("transform", `translate(${dx},0) translate(${cx},${cy}) scale(${sz}) translate(${-cx},${-cy})`);
        sc.upd(Math.max(0, t - sc.t0), Math.max(0.5, sc.t1 - sc.t0));
      });
      flash.attr("opacity", fl);
      cards.forEach((cd) => { const a = clamp(prog(t, cd.t0, 0.28) * (1 - prog(t, cd.t1 - 0.12, 0.12))), pop = E.back(prog(t, cd.t0, 0.36));
        cd.grp.attr("opacity", a).attr("transform", `translate(${W / 2},${cardY + 16 * (1 - pop)}) scale(${0.92 + 0.08 * pop})`); });
      bar.attr("width", W * clamp(t / T));
    };
  };
})();
