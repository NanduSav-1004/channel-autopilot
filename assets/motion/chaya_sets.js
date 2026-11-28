// Science Chaya hand-made scenes, second set: slope (a landslide in cross-section), wave (waves and the coast), moonland (to the Moon and down), cells (a mobile call), series (Madhava's pi), rainbow (light in a raindrop).
// Each is drawn in a 1000 x 1000 "set" and filmed by a camera like K.crow / K.home / K.damx: p.cams = [{at, x, y, z, cut}], p.at = {name: fraction of the scene}.
(() => {
  const M = window.MOTION, d3 = window.d3, { E, prog, clamp, lerp, rid, rnd, smooth, at, fit, K } = M;
  const pop = (pg, x, y, f, d, when) => { const kk = E.back(clamp(((f - when) * d) / 0.4)); pg.attr("opacity", clamp(kk * 2)).attr("transform", `translate(${x},${y}) scale(${0.6 + 0.4 * kk})`); };
  const arrow = (gp, col, w = 12) => { const pth = gp.append("path").attr("fill", "none").attr("stroke", col).attr("stroke-width", w).attr("stroke-linecap", "round").attr("stroke-linejoin", "round"); const hd = gp.append("path").attr("fill", col);
    return (x0, y0, x1, y1, op = 1) => { const L = Math.hypot(x1 - x0, y1 - y0) || 1, ux = (x1 - x0) / L, uy = (y1 - y0) / L, hl = 34;
      pth.attr("d", `M ${x0} ${y0} L ${x1 - ux * hl * 0.6} ${y1 - uy * hl * 0.6}`).attr("opacity", op); hd.attr("d", `M ${x1} ${y1} L ${x1 - ux * hl - uy * 20} ${y1 - uy * hl + ux * 20} L ${x1 - ux * hl + uy * 20} ${y1 - uy * hl - ux * 20} Z`).attr("opacity", op); }; };
  const house = (gp, x, y, w = 110, col = "#e9d3a8", roof = "#c8442f") => { const h = gp.append("g").attr("transform", `translate(${x},${y})`); h.append("rect").attr("x", -w / 2).attr("y", -w * 0.62).attr("width", w).attr("height", w * 0.62).attr("fill", col).attr("stroke", "#7b4a2b").attr("stroke-width", 3);
    h.append("path").attr("d", `M ${-w * 0.62} ${-w * 0.62} L 0 ${-w * 1.08} L ${w * 0.62} ${-w * 0.62} Z`).attr("fill", roof).attr("stroke", "#7b4a2b").attr("stroke-width", 3); h.append("rect").attr("x", -12).attr("y", -w * 0.38).attr("width", 24).attr("height", w * 0.38).attr("fill", "#7b4a2b"); return h; };

  // ================= slope: a hillside cut open; roots, rain soaking in, weight up and grip down, the slide, the debris flow, a rain gauge and the alert =================
  // p.at = {rain, roots, wet, weight, crack, slide, flow, gauge, alert}
  K.slope = (g, p, c) => {
    const id = c.id + rid(), k = M.setKit(g, c, id), s = k.set, a = p.at || {};
    const surf = [[-1400, 190], [-300, 230], [0, 300], [300, 470], [520, 640], [700, 700], [2400, 700]];
    const sy = (x) => { for (let i = 1; i < surf.length; i++) if (x <= surf[i][0]) { const [x0, y0] = surf[i - 1], [x1, y1] = surf[i]; return lerp(y0, y1, (x - x0) / (x1 - x0)); } return 700; };
    const D = 90, B0 = 40, B1 = 560;
    const band = (x0, x1, dy = D) => { const top = [], bot = []; for (let x = x0; x <= x1; x += 20) { top.push([x, sy(x)]); bot.push([x, sy(x) + dy]); } return "M " + top.concat(bot.reverse()).map((q) => q.join(" ")).join(" L ") + " Z"; };
    s.append("rect").attr("x", -1400).attr("y", -400).attr("width", 3800).attr("height", 1800).attr("fill", k.lg("sky", [[0, "#9fb6c4"], [0.6, "#d9e4e8"], [1, "#eef2f2"]]));
    s.append("path").attr("d", "M -1400 380 Q -900 120 -500 300 Q -200 60 100 200 L 100 800 L -1400 800 Z").attr("fill", "#7a9a86").attr("opacity", 0.6).attr("filter", k.blur("far", 4));
    s.append("path").attr("d", "M " + surf.map((q) => q.join(" ")).join(" L ") + " L 2400 1400 L -1400 1400 Z").attr("fill", k.lg("rock", [[0, "#8d8f94"], [1, "#4f5258"]]));
    for (let i = 0; i < 40; i++) s.append("path").attr("d", `M ${-1300 + rnd(i) * 3500} ${300 + rnd(i + 4) * 900} l ${40 + rnd(i + 8) * 90} ${rnd(i + 2) * 20 - 10}`).attr("stroke", "#3d4046").attr("stroke-width", 3).attr("opacity", 0.4);
    const soilFill = k.lg("soil", [[0, "#9a6f45"], [1, "#6a4a2c"]]);
    for (const [x0, x1] of [[-1400, B0], [B1, 2400]]) s.append("path").attr("d", band(x0, x1)).attr("fill", soilFill);
    s.append("path").attr("d", "M " + surf.map((q) => q.join(" ")).join(" L ")).attr("fill", "none").attr("stroke", "#4f8f3a").attr("stroke-width", 12);
    const blk = s.append("g").attr("filter", k.sh);
    blk.append("path").attr("d", band(B0, B1)).attr("fill", soilFill);
    blk.append("path").attr("d", "M " + Array.from({ length: 27 }, (_, i) => [B0 + i * 20, sy(B0 + i * 20)]).map((q) => q.join(" ")).join(" L ")).attr("fill", "none").attr("stroke", "#4f8f3a").attr("stroke-width", 12);
    const wet = [s.append("path").attr("d", band(-600, B0)).attr("fill", "#2a77a8"), blk.append("path").attr("d", band(B0, B1)).attr("fill", "#2a77a8")].map((q) => q.attr("opacity", 0));
    const trees = [-250, -110, 90, 210, 340, 470].map((x, i) => { const parent = x >= B0 && x <= B1 ? blk : s; const tg = parent.append("g").attr("transform", `translate(${x},${sy(x)})`); const tl = tg.append("g");
      const roots = []; for (let j = 0; j < 7; j++) { const dx = (j - 3) * 26, pth = `M 0 0 Q ${dx * 0.3} ${D * 0.5} ${dx} ${D * 0.92}`; tg.append("path").attr("d", pth).attr("fill", "none").attr("stroke", "#4a2a17").attr("stroke-width", 4).attr("opacity", 0.7);
        roots.push(tg.append("path").attr("d", pth).attr("fill", "none").attr("stroke", "#ffd23f").attr("stroke-width", 7).attr("opacity", 0)); }
      tl.append("rect").attr("x", -7).attr("y", -86).attr("width", 14).attr("height", 90).attr("fill", "#5a3a22"); tl.append("circle").attr("cy", -112).attr("r", 48).attr("fill", "#2f7d4f"); tl.append("circle").attr("cx", -28).attr("cy", -88).attr("r", 34).attr("fill", "#3a915d"); tl.append("circle").attr("cx", 30).attr("cy", -90).attr("r", 32).attr("fill", "#277043");
      return { tl, roots, x, inBlk: parent === blk }; });
    const cracks = blk.append("path").attr("d", `M 120 ${sy(120) - 6} l 14 22 l -12 18 l 16 24 M 250 ${sy(250) - 6} l -12 20 l 14 22 l -10 20`).attr("fill", "none").attr("stroke", "#2a1a10").attr("stroke-width", 7).attr("stroke-linecap", "round").attr("opacity", 0);
    const seeps = Array.from({ length: 36 }, (_, i) => s.append("circle").attr("r", 5).attr("fill", "#8fd0f0").attr("opacity", 0).datum(i));
    const villageG = s.append("g"); [[900, 700], [1080, 700], [1260, 700]].forEach(([x, y], i) => house(villageG, x, y, 110, ["#e9d3a8", "#f1dcc0", "#e2c89a"][i % 3]));
    const flow = s.append("path").attr("fill", "#6b4a2e").attr("opacity", 0).attr("filter", k.sh);
    const bits = Array.from({ length: 26 }, (_, i) => s.append("circle").attr("r", 6 + rnd(i) * 9).attr("fill", i % 3 ? "#6b4a2e" : "#4a3524").attr("opacity", 0).datum(i));
    const clouds = [[-100, 70, 360], [280, 40, 420], [700, 90, 340]].map(([x, y, sz]) => M.chayaIcon(s, "cloudDark", x, y, sz));
    const rain = Array.from({ length: 70 }, (_, i) => s.append("path").attr("stroke", "#5aaee0").attr("stroke-width", 4).attr("stroke-linecap", "round").attr("opacity", 0).datum(i));
    const gauge = s.append("g").attr("transform", "translate(1340,700)"); gauge.append("rect").attr("x", -22).attr("y", -190).attr("width", 44).attr("height", 190).attr("rx", 8).attr("fill", "#e8f4fa").attr("stroke", "#4a5560").attr("stroke-width", 5);
    const gw = gauge.append("rect").attr("x", -17).attr("width", 34).attr("fill", "#2a77a8"); for (let i = 1; i < 6; i++) gauge.append("line").attr("x1", 6).attr("x2", 22).attr("y1", -i * 31).attr("y2", -i * 31).attr("stroke", "#4a5560").attr("stroke-width", 3);
    const siren = s.append("g").attr("transform", "translate(1340,440)"); siren.append("rect").attr("x", -14).attr("y", 0).attr("width", 28).attr("height", 110).attr("fill", "#6b6f75"); const sl2 = siren.append("circle").attr("r", 38).attr("fill", "#e23b2e"); const slg = siren.append("circle").attr("r", 90).attr("fill", k.rg("sg", [[0, "#ff5a3c", 0.7], [1, "#ff5a3c", 0]]));
    const wArrow = arrow(s.append("g"), "#c8442f", 14), fArrow = arrow(s.append("g"), "#2f7d4f", 14);
    const T = { roots: k.pill2(120, 100, "വേരുകളുടെ വല", "ROOTS HOLD THE SOIL", "#2f7d4f"), wet: k.pill2(-150, 330, "വെള്ളം നിറയുന്നു", "WATER FILLS THE SOIL", "#2d6fa0"), weight: k.pill2(160, 600, "ഭാരം ↑   പിടിത്തം ↓", "HEAVIER, WEAKER", "#c8442f"),
      slide: k.pill2(520, 330, "താഴേക്ക് തെന്നുന്നു", "THE SLOPE SLIDES", "#7b4a2b"), flow: k.pill2(940, 520, "ഡെബ്രി ഫ്ലോ", "A DEBRIS FLOW", "#4a2a17"), gauge: k.pill2(1340, 480, "മഴമാപിനി", "RAIN GAUGE", "#2d6fa0"), alert: k.pill2(1340, 300, "അലർട്ട് → മാറൂ", "ALERT MEANS MOVE", "#c8442f") };
    const TP = { roots: [120, 100], wet: [-150, 330], weight: [160, 600], slide: [520, 330], flow: [940, 520], gauge: [1340, 480], alert: [1340, 300] };
    const move = k.camMover(p.cams || [{ at: 0, x: 500, y: 520, z: 1 }]);
    const dir = [0.79, 0.61], bc = [300, sy(300) + 40];
    return (lt, d) => { const f = lt / d; move(f, d);
      const rn = prog(f, at(a, "rain"), 0.03), wt = prog(f, at(a, "wet"), 0.18), sl = prog(f, at(a, "slide"), 0.09), fl = prog(f, at(a, "flow"), 0.1), rt = prog(f, at(a, "roots"), 0.03), cr = prog(f, at(a, "crack"), 0.04), gg = prog(f, at(a, "gauge"), 0.2), al = prog(f, at(a, "alert"), 0.03), wgt = prog(f, at(a, "weight"), 0.1);
      clouds.forEach((q, i) => q.attr("opacity", 0.35 + 0.65 * rn).attr("transform", `translate(${[-100, 280, 700][i] + Math.sin(lt * 0.3 + i) * 20},${[70, 40, 90][i]}) scale(${[3.6, 4.2, 3.4][i]})`));
      rain.forEach((q, i) => { const x = -500 + rnd(i) * 1700, u = (lt * (0.9 + rnd(i + 3) * 0.4) + rnd(i + 6)) % 1, y = 140 + u * 800, gy = x < 700 ? sy(x) : 700; q.attr("d", `M ${x - u * 80} ${y} l -10 28`).attr("opacity", y < gy - 10 ? rn * 0.85 : 0); });
      wet.forEach((q) => q.attr("opacity", 0.5 * wt));
      seeps.forEach((q) => { const i = q.datum(), x = -300 + rnd(i) * 860, u = (lt * 0.5 + rnd(i + 3)) % 1; q.attr("cx", x + u * 14).attr("cy", sy(x) + 6 + u * (D - 14)).attr("opacity", wt * (1 - u) * 0.9); });
      trees.forEach((t) => { t.roots.forEach((r) => r.attr("opacity", rt * (0.6 + 0.4 * Math.sin(lt * 4 + t.x)))); t.tl.attr("transform", `rotate(${cr * (t.x > 0 ? 11 : -3) * (t.inBlk ? 1 : 0.4)})`); });
      cracks.attr("opacity", cr);
      const dist = 520 * sl * sl;
      blk.attr("transform", `translate(${dir[0] * dist},${dir[1] * dist}) rotate(${-5 * sl} ${bc[0]} ${bc[1]})`).attr("opacity", 1 - 0.3 * prog(f, at(a, "flow"), 0.2));
      const fh = 100 * fl; flow.attr("d", `M 500 ${sy(500) + 40} Q 700 ${700 - fh * 0.6} 900 ${700 - fh} T 1400 ${700 - fh * 0.5} L 1400 705 L 520 705 Z`).attr("opacity", 0.92 * fl);
      bits.forEach((q) => { const i = q.datum(), u = (lt * 0.5 + rnd(i)) % 1; q.attr("cx", 560 + u * 760).attr("cy", sy(560 + u * 200) - 20 - rnd(i + 2) * 70 * fl).attr("opacity", fl * (1 - u)); });
      const wl = 190 * gg * 0.55; gw.attr("y", -wl - 3).attr("height", wl);
      const pulse = 0.5 + 0.5 * Math.sin(lt * 9); sl2.attr("opacity", al * (0.5 + 0.5 * pulse)); slg.attr("opacity", al * pulse);
      const wl2 = 60 + 90 * wt, fl2 = 130 * (1 - 0.65 * wt);
      wArrow(bc[0], bc[1], bc[0], bc[1] + wl2, wgt); fArrow(bc[0], bc[1], bc[0] - 0.79 * fl2, bc[1] - 0.61 * fl2, wgt * (1 - sl));
      Object.keys(T).forEach((n) => pop(T[n], TP[n][0], TP[n][1], f, d, at(a, n === "weight" ? "weight" : n))); };
  };

  // ================= wave: the sea in cross-section; wind makes waves, energy (not water) travels, the seabed rises, the wave breaks; a seawall scours the sand; a far-away storm sends a surprise swell =================
  // p.at = {wind, swell, buoy, orbits, shallow, break, wall, scour, far}
  K.wave = (g, p, c) => {
    const id = c.id + rid(), k = M.setKit(g, c, id), s = k.set, a = p.at || {};
    const Y0 = 470, H0 = 350, X0 = -1400, X1 = 1000;
    const bedBase = (x) => (x < -100 ? 820 : x < 1000 ? lerp(820, 560, (x + 100) / 1100) : 560);
    const bed = (x, sc) => bedBase(x) + sc * Math.max(0, 1 - Math.abs(x - 930) / 170) * 80;
    const xs = [], ph = []; let acc = 0; for (let x = X0; x <= X1; x += 10) { const h = Math.max(36, bedBase(x) - Y0); acc += 0.0215 * Math.sqrt(H0 / h) * 10; xs.push(x); ph.push(acc); }
    const ampAt = (x, A0) => { const h = Math.max(36, bedBase(x) - Y0); return Math.min(A0 * Math.pow(H0 / h, 0.3), h * 0.62); };
    s.append("rect").attr("x", -1400).attr("y", -500).attr("width", 3800).attr("height", 1000).attr("fill", k.lg("sky", [[0, "#7cc4ec"], [1, "#e6f5fb"]]));
    s.append("circle").attr("cx", 1200).attr("cy", 120).attr("r", 70).attr("fill", "#ffe08a"); s.append("circle").attr("cx", 1200).attr("cy", 120).attr("r", 190).attr("fill", k.rg("sun", [[0, "#fff1b0", 0.6], [1, "#fff1b0", 0]]));
    const farStorm = M.chayaIcon(s, "cloudDark", -1250, 150, 480).attr("opacity", 0), bolt = M.chayaIcon(s, "bolt", -1230, 300, 160).attr("opacity", 0);
    const windG = s.append("g"), winds = Array.from({ length: 9 }, (_, i) => windG.append("path").attr("fill", "none").attr("stroke", "#fff").attr("stroke-width", 7).attr("stroke-linecap", "round").attr("opacity", 0).datum(i));
    const cloud = M.chayaIcon(s, "cloud", -700, 110, 380);
    const sand = s.append("path").attr("fill", k.lg("sand", [[0, "#e6cf98"], [1, "#b8975a"]])), water = s.append("path").attr("fill", k.lg("wat", [[0, "#3aa0cf"], [1, "#146a95"]])).attr("opacity", 0.92);
    const surf = s.append("path").attr("fill", "none").attr("stroke", "#e9f8ff").attr("stroke-width", 6).attr("stroke-linejoin", "round");
    const wall = s.append("g").attr("opacity", 0); wall.append("rect").attr("x", 944).attr("y", 440).attr("width", 80).attr("height", 150).attr("rx", 8).attr("fill", "#5d6168").attr("stroke", "#33363b").attr("stroke-width", 5); for (let i = 0; i < 4; i++) wall.append("line").attr("x1", 944).attr("x2", 1024).attr("y1", 480 + i * 34).attr("y2", 480 + i * 34).attr("stroke", "#33363b").attr("stroke-width", 3);
    const foam = Array.from({ length: 34 }, (_, i) => s.append("circle").attr("r", 5 + rnd(i) * 9).attr("fill", "#fff").attr("opacity", 0).datum(i));
    const orbG = s.append("g").attr("opacity", 0), OX = -700, orbs = [0, 70, 140, 210].map((dp) => { const r = 42 * Math.exp(-dp / 190); orbG.append("circle").attr("cx", OX).attr("cy", Y0 + dp).attr("r", r).attr("fill", "none").attr("stroke", "#fff").attr("stroke-width", 4).attr("stroke-dasharray", "8 8"); return [r, dp, orbG.append("circle").attr("r", 11).attr("fill", "#ffd23f").attr("stroke", "#4a2a17").attr("stroke-width", 3)]; });
    const buoy = s.append("g").attr("opacity", 0); buoy.append("rect").attr("x", -6).attr("y", -70).attr("width", 12).attr("height", 70).attr("fill", "#4a2a17"); buoy.append("circle").attr("cy", -78).attr("r", 18).attr("fill", "#e23b2e"); buoy.append("ellipse").attr("rx", 40).attr("ry", 16).attr("fill", "#fff").attr("stroke", "#4a2a17").attr("stroke-width", 4);
    const T = { wind: k.pill2(-640, 250, "കാറ്റ് → അലകൾ", "WIND MAKES RIPPLES", "#2d6fa0"), energy: k.pill2(-300, 340, "ഊർജം മാത്രം സഞ്ചരിക്കുന്നു", "ONLY ENERGY TRAVELS", "#c8442f"), shallow: k.pill2(500, 330, "ആഴം കുറയുന്നു", "THE SEABED RISES", "#7b4a2b"), break: k.pill2(760, 300, "ഉയർന്ന് പൊട്ടുന്നു", "THE WAVE BREAKS", "#c8442f"),
      wall: k.pill2(980, 380, "കരിങ്കൽഭിത്തി", "A SEAWALL", "#4a2a17"), scour: k.pill2(880, 700, "മണൽ നഷ്ടം", "THE SAND IS SCOURED", "#c8442f"), far: k.pill2(-1100, 330, "ദൂരെ ഒരു കൊടുങ്കാറ്റ്", "A FAR-AWAY STORM", "#4a2a17") };
    const TP = { wind: [-640, 250], energy: [-300, 340], shallow: [500, 330], break: [760, 300], wall: [980, 380], scour: [880, 700], far: [-1100, 330] };
    const move = k.camMover(p.cams || [{ at: 0, x: 500, y: 520, z: 1 }]);
    return (lt, d) => { const f = lt / d; move(f, d);
      const wd = prog(f, at(a, "wind"), 0.03), sw = prog(f, at(a, "swell"), 0.12), by = prog(f, at(a, "buoy"), 0.03), ob = prog(f, at(a, "orbits"), 0.03), bk = prog(f, at(a, "break"), 0.05), wl = prog(f, at(a, "wall"), 0.04), sc = prog(f, at(a, "scour"), 0.15), fr = prog(f, at(a, "far"), 0.1);
      const A0 = 12 + 26 * sw + 22 * fr, om = 3.4, th = (i) => ph[i] - om * lt, xdraw = (i, y) => xs[i] + Math.max(0, Math.min(1, (xs[i] - 640) / 280)) * Math.max(0, Y0 - y) * 1.4 * bk * 0 + (xs[i] > 600 ? Math.max(0, Y0 - y) * 1.1 * clamp((xs[i] - 600) / 300) * (0.4 + 0.6 * bk) : 0);
      const pts = xs.map((x, i) => { const A = ampAt(x, A0), ss = Math.sin(th(i)); const y = Y0 - A * (ss + 0.18 * Math.sin(2 * th(i) + 1.2) * clamp((x - 300) / 600)); return [xdraw(i, y), y]; });
      const line = "M " + pts.map((q) => q[0].toFixed(1) + " " + q[1].toFixed(1)).join(" L ");
      surf.attr("d", line);
      const bd = xs.map((x) => [x, bed(x, sc)]).reverse(); water.attr("d", line + " L " + bd.map((q) => q.join(" ")).join(" L ") + " Z");
      sand.attr("d", "M " + xs.map((x) => `${x} ${bed(x, sc)}`).join(" L ") + " L 1100 520 L 2400 520 L 2400 1400 L -1400 1400 Z");
      cloud.attr("transform", `translate(${-700 + Math.sin(lt * 0.4) * 24},110) scale(3.8)`).attr("opacity", 0.55 + 0.45 * wd);
      winds.forEach((q) => { const i = q.datum(), u = (lt * 0.55 + i / 9) % 1, y = 190 + (i % 4) * 46; q.attr("d", `M ${-1000 + u * 700} ${y} l 140 0`).attr("opacity", wd * (1 - Math.abs(u - 0.5) * 2) * (1 - fr * 0.9)); });
      farStorm.attr("opacity", fr).attr("transform", `translate(-1250,150) scale(4.8)`); bolt.attr("opacity", fr * (Math.sin(lt * 8) > 0.5 ? 1 : 0.2)).attr("transform", "translate(-1230,330) scale(1.6)");
      const bi = xs.findIndex((x) => x >= -300), bA = ampAt(-300, A0), bth = th(bi);
      buoy.attr("opacity", by).attr("transform", `translate(${-300 + bA * Math.cos(bth) * 0.9},${Y0 - bA * Math.sin(bth) + 4})`);
      orbG.attr("opacity", ob); orbs.forEach(([r, dp, dot]) => dot.attr("cx", OX + r * Math.cos(om * lt)).attr("cy", Y0 + dp - A0 * 0.0 - r * Math.sin(om * lt)));
      wall.attr("opacity", wl);
      foam.forEach((q) => { const i = q.datum(), u = (lt * 0.8 + rnd(i)) % 1, x = 700 + rnd(i + 1) * 300; q.attr("cx", x + u * 40).attr("cy", Y0 - 30 - u * 40 * rnd(i + 5) + 10 * Math.sin(lt * 5 + i)).attr("opacity", bk * (1 - u) * 0.9); });
      Object.keys(T).forEach((n) => pop(T[n], TP[n][0], TP[n][1], f, d, at(a, n))); };
  };

  // ================= moonland: the trip (rocket, growing orbits, the transfer, capture) and then the landing on the Moon's surface (descent, dust, rover) =================
  // p.at = {launch, orbits, transfer, capture, descend, land, rover}; the surface is drawn far to the right (x from 2600) and the camera cuts to it
  K.moonland = (g, p, c) => {
    const id = c.id + rid(), k = M.setKit(g, c, id), s = k.set, a = p.at || {};
    s.append("rect").attr("x", -1400).attr("y", -900).attr("width", 6800).attr("height", 2600).attr("fill", k.lg("space", [[0, "#050b1f"], [1, "#182a55"]]));
    for (let i = 0; i < 240; i++) s.append("circle").attr("cx", -1300 + rnd(i) * 6600).attr("cy", -800 + rnd(i + 7) * 2400).attr("r", 1.5 + rnd(i + 3) * 3.2).attr("fill", "#fff").attr("opacity", 0.3 + rnd(i + 9) * 0.7);
    const E0 = [-150, 600], ER = 250, MO = [1150, 330], MR = 105;
    // Earth and Moon
    s.append("circle").attr("cx", E0[0]).attr("cy", E0[1]).attr("r", ER + 40).attr("fill", k.rg("eg", [[0.7, "#6ab8ff", 0.45], [1, "#6ab8ff", 0]]));
    s.append("circle").attr("cx", E0[0]).attr("cy", E0[1]).attr("r", ER).attr("fill", k.lg("earth", [[0, "#3aa0e8"], [1, "#1a5fa8"]], 1, 1));
    for (const [dx, dy, rr] of [[-60, -80, 70], [70, 20, 90], [-100, 90, 55], [10, -170, 40]]) s.append("ellipse").attr("cx", E0[0] + dx).attr("cy", E0[1] + dy).attr("rx", rr).attr("ry", rr * 0.7).attr("fill", "#4f9a4a").attr("opacity", 0.9);
    s.append("circle").attr("cx", MO[0]).attr("cy", MO[1]).attr("r", MR).attr("fill", k.lg("moon", [[0, "#e4e1d8"], [1, "#9b988e"]], 1, 1));
    for (const [dx, dy, rr] of [[-30, -20, 22], [28, 30, 16], [20, -40, 10], [-40, 40, 12]]) s.append("circle").attr("cx", MO[0] + dx).attr("cy", MO[1] + dy).attr("r", rr).attr("fill", "#7c7a72").attr("opacity", 0.6);
    // the trail of the spacecraft: three growing loops round the Earth, then the way to the Moon, then loops round the Moon
    const path = [], loops = [[330, 300], [420, 355], [540, 430]];
    loops.forEach(([rx, ry], li) => { for (let t = 0; t <= 100; t++) { const an = -Math.PI / 2 + (t / 100) * Math.PI * 2; path.push([E0[0] + rx * Math.cos(an) * 1.04, E0[1] + ry * Math.sin(an) * 1.04, li]); } });
    const sx0 = E0[0] + 561, sy0 = E0[1] - 5; for (let t = 1; t <= 120; t++) { const u = t / 120, bx = lerp(sx0, MO[0] - 190, u), by = lerp(sy0, MO[1] + 20, u) - Math.sin(u * Math.PI) * 190; path.push([bx, by, 3]); }
    for (let t = 0; t <= 100; t++) { const an = Math.PI + (t / 100) * Math.PI * 4; path.push([MO[0] + 175 * Math.cos(an), MO[1] + 150 * Math.sin(an), 4]); }
    const trail = s.append("path").attr("fill", "none").attr("stroke", "#ffd23f").attr("stroke-width", 5).attr("stroke-dasharray", "14 10").attr("stroke-linecap", "round");
    const craft = M.chayaIcon(s, "satellite", 0, 0, 90).attr("opacity", 0), rocket = M.chayaIcon(s, "rocket", E0[0], E0[1] - ER, 120).attr("opacity", 0);
    // the surface of the Moon, far to the right
    const LX = 3000, GY = 760, sf = s.append("g");
    sf.append("rect").attr("x", LX - 700).attr("y", -900).attr("width", 2600).attr("height", 1700).attr("fill", k.lg("lsky", [[0, "#02040c"], [1, "#0b1430"]]));
    for (let i = 0; i < 120; i++) sf.append("circle").attr("cx", LX - 650 + rnd(i + 40) * 2500).attr("cy", -600 + rnd(i + 17) * 1200).attr("r", 1.5 + rnd(i + 3) * 2.6).attr("fill", "#fff").attr("opacity", 0.4 + rnd(i) * 0.6);
    sf.append("circle").attr("cx", LX + 760).attr("cy", 40).attr("r", 70).attr("fill", "#3aa0e8"); sf.append("ellipse").attr("cx", LX + 745).attr("cy", 30).attr("rx", 28).attr("ry", 20).attr("fill", "#4f9a4a");
    sf.append("path").attr("d", `M ${LX - 700} ${GY - 30} Q ${LX - 300} ${GY - 80} ${LX + 100} ${GY - 20} T ${LX + 900} ${GY - 40} T ${LX + 1900} ${GY - 20} L ${LX + 1900} 1100 L ${LX - 700} 1100 Z`).attr("fill", k.lg("lground", [[0, "#b5b2a8"], [1, "#6d6b64"]]));
    for (const [dx, rx] of [[-400, 120], [180, 160], [700, 100], [1200, 140]]) { sf.append("ellipse").attr("cx", LX + dx).attr("cy", GY + 60).attr("rx", rx).attr("ry", rx * 0.22).attr("fill", "#6d6b64"); sf.append("ellipse").attr("cx", LX + dx).attr("cy", GY + 52).attr("rx", rx * 0.85).attr("ry", rx * 0.15).attr("fill", "#8a887f"); }
    const shadow = sf.append("ellipse").attr("cx", LX + 330).attr("cy", GY + 22).attr("ry", 10).attr("fill", "#2a2925").attr("opacity", 0.4);
    const lander = sf.append("g"); const flame = lander.append("path").attr("d", "M -22 60 Q 0 190 22 60 Z").attr("fill", "#ffd23f").attr("opacity", 0);
    lander.append("path").attr("d", "M -50 40 L -92 82 M 50 40 L 92 82").attr("stroke", "#c9cfd4").attr("stroke-width", 7).attr("stroke-linecap", "round"); lander.append("rect").attr("x", -100).attr("y", 80).attr("width", 16).attr("height", 7).attr("fill", "#c9cfd4"); lander.append("rect").attr("x", 84).attr("y", 80).attr("width", 16).attr("height", 7).attr("fill", "#c9cfd4");
    lander.append("rect").attr("x", -58).attr("y", -36).attr("width", 116).attr("height", 80).attr("rx", 10).attr("fill", k.lg("foil", [[0, "#f6b945"], [1, "#c98a22"]])).attr("stroke", "#4a2a17").attr("stroke-width", 4); lander.append("rect").attr("x", -22).attr("y", 44).attr("width", 44).attr("height", 20).attr("fill", "#5e6b78"); lander.append("path").attr("d", "M -30 -36 L 30 -36 L 20 -62 L -20 -62 Z").attr("fill", "#e9edf0"); lander.append("circle").attr("cx", 24).attr("cy", -8).attr("r", 9).attr("fill", "#1a2733");
    const rover = sf.append("g"); rover.append("rect").attr("x", -34).attr("y", -34).attr("width", 70).attr("height", 30).attr("rx", 6).attr("fill", "#f2f3f4").attr("stroke", "#4a2a17").attr("stroke-width", 4); rover.append("rect").attr("x", -26).attr("y", -52).attr("width", 56).attr("height", 14).attr("fill", "#2d6fa0");
    const wheels = [-26, 0, 26].flatMap((x) => [rover.append("circle").attr("cx", x).attr("cy", -2).attr("r", 12).attr("fill", "#3a3a40").attr("stroke", "#aab3ba").attr("stroke-width", 3)]);
    const dust = Array.from({ length: 30 }, (_, i) => sf.append("circle").attr("r", 8 + rnd(i) * 14).attr("fill", "#cfccc2").attr("opacity", 0).datum(i));
    const speed = sf.append("text").attr("x", LX + 560).attr("y", 120).attr("fill", "#fff").attr("font-size", 66).attr("font-weight", 800).attr("text-anchor", "middle").attr("opacity", 0);
    const T = { launch: k.pill2(E0[0] + 50, 150, "LVM3 റോക്കറ്റ്", "THE ROCKET LIFTS OFF", "#c8442f"), orbits: k.pill2(E0[0] + 640, 620, "ഭ്രമണപഥം വലുതാകുന്നു", "THE ORBIT GROWS", "#2d6fa0"), transfer: k.pill2(550, 80, "ചന്ദ്രനിലേക്ക്", "TOWARDS THE MOON", "#7b4a2b"), capture: k.pill2(1150, 560, "ചന്ദ്രൻ പിടിച്ചെടുക്കുന്നു", "CAPTURED BY MOON'S GRAVITY", "#4a2a17"),
      descend: k.pill2(LX + 120, 120, "എൻജിൻ കൊണ്ട് ബ്രേക്ക്", "BRAKING WITH ENGINES", "#c8442f"), land: k.pill2(LX + 560, 540, "വിക്രം ഇറങ്ങി", "VIKRAM HAS LANDED", "#2f7d4f"), rover: k.pill2(LX + 900, 620, "പ്രഗ്യാൻ റോവർ", "PRAGYAAN ROLLS OUT", "#2d6fa0") };
    const TP = { launch: [E0[0] + 50, 150], orbits: [E0[0] + 640, 620], transfer: [550, 80], capture: [1150, 560], descend: [LX + 120, 120], land: [LX + 560, 540], rover: [LX + 900, 620] };
    const move = k.camMover(p.cams || [{ at: 0, x: 500, y: 480, z: 0.9 }]);
    return (lt, d) => { const f = lt / d; move(f, d);
      const la = prog(f, at(a, "launch"), 0.06), or = prog(f, at(a, "orbits"), 0.35), tr = prog(f, at(a, "transfer"), 0.12), cp = prog(f, at(a, "capture"), 0.14), de = prog(f, at(a, "descend"), 0.18), ld = prog(f, at(a, "land"), 0.03), rv = prog(f, at(a, "rover"), 0.25);
      const u = Math.min(1, or * 0.62 + tr * 0.2 + cp * 0.18), idx = Math.min(path.length - 1, Math.floor(u * (path.length - 1)));
      trail.attr("d", idx > 1 ? "M " + path.slice(0, idx + 1).map((q) => q[0].toFixed(1) + " " + q[1].toFixed(1)).join(" L ") : "M 0 0").attr("stroke-dashoffset", -lt * 30).attr("opacity", or > 0 ? 1 : 0);
      const pt = path[idx]; craft.attr("opacity", or > 0 && de === 0 ? 1 : 0).attr("transform", `translate(${pt[0]},${pt[1]}) scale(0.9)`);
      rocket.attr("opacity", la > 0 && or < 0.03 ? 1 : 0).attr("transform", `translate(${E0[0] + 100 * la},${E0[1] - ER - 300 * la}) rotate(${25 * la}) scale(1.2)`);
      const dy = lerp(-330, 660, E.out(de)), lx = LX + 330; lander.attr("transform", `translate(${lx},${GY - 60 + dy - 660 + 660 * 0})`.replace(/,[^)]*\)$/, `,${dy}) scale(1)`));
      lander.attr("transform", `translate(${lx},${dy})`); flame.attr("opacity", de > 0 && ld < 0.5 ? 0.7 + 0.3 * Math.sin(lt * 40) : 0).attr("transform", `scale(${0.7 + 0.5 * (1 - de)},${0.5 + 1.2 * (1 - de)})`); shadow.attr("rx", 20 + 70 * de);
      const spd = Math.max(0, 1.5 * (1 - E.out(de))); speed.attr("opacity", de > 0 && ld < 0.5 ? 1 : 0).text(spd.toFixed(1) + " km/s");
      dust.forEach((q) => { const i = q.datum(), uu = clamp((f - at(a, "land")) * d / 2.2), an = rnd(i) * Math.PI; q.attr("cx", lx + Math.cos(an) * uu * (160 + rnd(i + 3) * 300) * (rnd(i + 5) > 0.5 ? 1 : -1)).attr("cy", GY - 10 - Math.sin(an) * uu * 90 - uu * 10).attr("opacity", ld > 0 ? 0.7 * (1 - uu) : 0); });
      const rx = lx + 90 + 520 * rv; rover.attr("opacity", rv > 0 ? 1 : 0).attr("transform", `translate(${rx},${GY - 18 + Math.sin(rv * 25) * 2})`); wheels.forEach((w) => w.attr("stroke-dasharray", "5 5").attr("stroke-dashoffset", -rv * 400));
      Object.keys(T).forEach((n) => pop(T[n], TP[n][0], TP[n][1], f, d, at(a, n))); };
  };

  // ================= cells: a map of hexagon cells with towers; a call hops from phone to phone, frequencies repeat far apart, a bus is handed from tower to tower =================
  // p.at = {tower, cells, freq, wave, fibre, call, reuse, bus}
  K.cells = (g, p, c) => {
    const id = c.id + rid(), k = M.setKit(g, c, id), s = k.set, a = p.at || {};
    s.append("rect").attr("x", -1400).attr("y", -400).attr("width", 4600).attr("height", 1900).attr("fill", k.lg("map", [[0, "#cfe8d8"], [1, "#f1e8cf"]]));
    s.append("path").attr("d", "M -1400 760 Q -300 700 500 800 T 2300 720").attr("fill", "none").attr("stroke", "#fff").attr("stroke-width", 16).attr("opacity", 0.7);
    const R = 150, W = Math.sqrt(3) * R, COLS = 9, ROWS = 4, ox = -330, oy = 150, cen = (cl, r) => [ox + cl * W + (r % 2) * W / 2, oy + r * R * 1.5];
    const colors = ["#ffd98a", "#9fd8e8", "#f4a99a"], cells = [];
    for (let r = 0; r < ROWS; r++) for (let cl = 0; cl < COLS; cl++) { const [x, y] = cen(cl, r), col = (cl + 2 * r) % 3; const poly = d3.range(6).map((i) => [x + R * 0.97 * Math.cos(Math.PI / 6 + i * Math.PI / 3), y + R * 0.97 * Math.sin(Math.PI / 6 + i * Math.PI / 3)]);
      const hx = s.append("path").attr("d", "M " + poly.map((q) => q.join(" ")).join(" L ") + " Z").attr("fill", "#fff7e6").attr("stroke", "#fff").attr("stroke-width", 6).attr("opacity", 0); cells.push({ hx, col, cl, r, x, y }); }
    const chain = Array.from({ length: COLS }, (_, cl) => cen(cl, 1)).map(([x, y]) => [x + W / 4, y]);
    const fibre = s.append("path").attr("d", "M " + chain.map((q) => q.join(" ")).join(" L ")).attr("fill", "none").attr("stroke", "#e8a33d").attr("stroke-width", 10).attr("stroke-linecap", "round").attr("stroke-dasharray", "22 14").attr("opacity", 0);
    const towers = cells.filter((q) => (q.cl + q.r) % 1 === 0).map((q) => { const tg = s.append("g").attr("opacity", 0); M.chayaIcon(tg, "pylon", q.x, q.y - 4, 74); return { tg, q }; });
    const packets = Array.from({ length: 7 }, () => s.append("circle").attr("r", 13).attr("fill", "#c8442f").attr("stroke", "#fff").attr("stroke-width", 4).attr("opacity", 0));
    const rings = Array.from({ length: 3 }, () => s.append("circle").attr("fill", "none").attr("stroke", "#2d6fa0").attr("stroke-width", 6).attr("opacity", 0));
    const phA = M.chayaIcon(s, "phone", chain[0][0] - 120, chain[0][1] + 20, 90), phB = M.chayaIcon(s, "phone", chain[COLS - 1][0] + 120, chain[COLS - 1][1] + 20, 90);
    const busY = cen(0, 3)[1] + 40, bus = s.append("g").attr("opacity", 0); bus.append("rect").attr("x", -70).attr("y", -44).attr("width", 140).attr("height", 60).attr("rx", 12).attr("fill", "#c8442f").attr("stroke", "#4a2a17").attr("stroke-width", 4); for (let i = 0; i < 4; i++) bus.append("rect").attr("x", -58 + i * 30).attr("y", -34).attr("width", 22).attr("height", 22).attr("fill", "#bfe3f6"); bus.append("circle").attr("cx", -40).attr("cy", 18).attr("r", 12).attr("fill", "#2a1a10"); bus.append("circle").attr("cx", 40).attr("cy", 18).attr("r", 12).attr("fill", "#2a1a10");
    const link = s.append("line").attr("stroke", "#2f7d4f").attr("stroke-width", 7).attr("stroke-dasharray", "10 8").attr("opacity", 0);
    const T = { tower: k.pill2(chain[1][0], chain[1][1] - 140, "മൊബൈൽ ടവർ", "A MOBILE TOWER", "#4a2a17"), cells: k.pill2(chain[3][0], 40, "ഓരോ ഹെക്സഗണും ഒരു സെൽ", "EACH HEXAGON IS A CELL", "#2d6fa0"), freq: k.pill2(chain[4][0], 700, "അയൽ സെല്ലുകൾക്ക് വ്യത്യസ്ത ആവൃത്തി", "NEIGHBOURS USE OTHER FREQUENCIES", "#c8442f"), fibre: k.pill2(chain[5][0], chain[5][1] - 120, "ടവറുകൾ ഫൈബറിൽ", "TOWERS JOINED BY FIBRE", "#e8a33d"),
      reuse: k.pill2(chain[6][0], 40, "ദൂരെ അതേ ആവൃത്തി വീണ്ടും", "THE SAME FREQUENCY, FAR AWAY", "#2f7d4f"), bus: k.pill2(cen(4, 3)[0], busY + 120, "ഹാൻഡ്ഓവർ", "HANDOVER TO THE NEXT TOWER", "#7b4a2b") };
    const TP = { tower: [chain[1][0], chain[1][1] - 140], cells: [chain[3][0], 40], freq: [chain[4][0], 700], fibre: [chain[5][0], chain[5][1] - 120], reuse: [chain[6][0], 40], bus: [cen(4, 3)[0], busY + 120] };
    const move = k.camMover(p.cams || [{ at: 0, x: 500, y: 450, z: 1 }]);
    return (lt, d) => { const f = lt / d; move(f, d);
      const ce = prog(f, at(a, "cells"), 0.1), fq = prog(f, at(a, "freq"), 0.1), tw = prog(f, at(a, "tower"), 0.08), fb = prog(f, at(a, "fibre"), 0.05), cl = prog(f, at(a, "call"), 0.02), ru = prog(f, at(a, "reuse"), 0.05), bs = prog(f, at(a, "bus"), 0.25), wv = prog(f, at(a, "wave"), 0.02);
      cells.forEach((q) => { q.hx.attr("opacity", ce); q.hx.attr("fill", fq > 0.01 ? colors[q.col] : "#fff7e6").attr("stroke-width", ru > 0 && q.col === 0 && (q.cl === 0 || q.cl >= COLS - 2) && q.r === 1 ? 6 + 6 * Math.sin(lt * 6) : 6); });
      towers.forEach((t, i) => t.tg.attr("opacity", clamp((tw * (cells.length * 0.4) - i * 0.5) * 0.6)));
      fibre.attr("opacity", fb).attr("stroke-dashoffset", -lt * 60);
      rings.forEach((r, i) => { const u = (lt * 0.6 + i / 3) % 1; r.attr("cx", chain[0][0] - 120).attr("cy", chain[0][1] + 20).attr("r", 30 + u * 190).attr("opacity", wv * (1 - u) * 0.9); });
      packets.forEach((q, i) => { const u = clamp(((f - at(a, "call")) * d * 0.16 - i * 0.09) % 1.4), pos = (u * (COLS - 1)), ii = Math.min(COLS - 2, Math.floor(pos)), fr = pos - ii; q.attr("cx", lerp(chain[ii][0], chain[ii + 1][0], fr)).attr("cy", lerp(chain[ii][1], chain[ii + 1][1], fr)).attr("opacity", cl > 0 && u > 0 && u < 1 ? 1 : 0); });
      const bx = cen(1, 3)[0] + bs * (cen(7, 3)[0] - cen(1, 3)[0]); bus.attr("opacity", bs > 0 ? 1 : 0).attr("transform", `translate(${bx},${busY})`);
      const near = chain.reduce((b, q, i) => (Math.abs(q[0] - bx) < Math.abs(chain[b][0] - bx) ? i : b), 0); link.attr("x1", bx).attr("y1", busY - 40).attr("x2", chain[near][0]).attr("y2", chain[near][1] + 20).attr("opacity", bs > 0 ? 1 : 0).attr("stroke", ["#2f7d4f", "#2d6fa0"][near % 2]).attr("stroke-dashoffset", -lt * 40);
      Object.keys(T).forEach((n) => pop(T[n], TP[n][0], TP[n][1], f, d, at(a, n))); };
  };

  // ================= series: Madhava's series for pi; the partial sums swing round pi and slowly close in; the correction term lets them hug the line =================
  // p.at = {terms, pi, fix}
  K.series = (g, p, c) => {
    const id = c.id + rid(), k = M.setKit(g, c, id), s = k.set, a = p.at || {}, N = 40;
    s.append("rect").attr("x", -1400).attr("y", -400).attr("width", 4200).attr("height", 1800).attr("fill", k.lg("bg", [[0, "#fff7e6"], [1, "#f1e2c4"]]));
    const v1 = [], v2 = []; let sum = 0; for (let n = 1; n <= N; n++) { sum += (n % 2 ? 1 : -1) / (2 * n - 1); v1.push(4 * sum); v2.push(4 * (sum + (n % 2 ? -1 : 1) * (n * n + 1) / (4 * n ** 3 + 5 * n))); }
    const X = (n) => -250 + n * 38, Yv = (v) => 860 - ((v - 2.6) / 1.5) * 480;
    s.append("rect").attr("x", -300).attr("y", 350).attr("width", 1620).attr("height", 560).attr("rx", 24).attr("fill", "#fffdf6").attr("stroke", "#c9a77a").attr("stroke-width", 5);
    const piLine = s.append("g").attr("opacity", 0); piLine.append("line").attr("x1", -280).attr("x2", 1300).attr("y1", Yv(Math.PI)).attr("y2", Yv(Math.PI)).attr("stroke", "#c8442f").attr("stroke-width", 6).attr("stroke-dasharray", "16 10"); piLine.append("text").attr("x", 1290).attr("y", Yv(Math.PI) - 14).attr("text-anchor", "end").attr("fill", "#c8442f").attr("font-weight", 800).attr("font-size", 40).text("π = 3.14159…");
    const z1 = s.append("path").attr("fill", "none").attr("stroke", "#2d6fa0").attr("stroke-width", 4).attr("opacity", 0.7), z2 = s.append("path").attr("fill", "none").attr("stroke", "#2f7d4f").attr("stroke-width", 4).attr("opacity", 0.8);
    const d1 = v1.map((v, i) => s.append("circle").attr("cx", X(i + 1)).attr("cy", Yv(v)).attr("r", 9).attr("fill", "#2d6fa0").attr("stroke", "#fff").attr("stroke-width", 3).attr("opacity", 0)), d2 = v2.map((v, i) => s.append("circle").attr("cx", X(i + 1)).attr("cy", Yv(v)).attr("r", 9).attr("fill", "#2f7d4f").attr("stroke", "#fff").attr("stroke-width", 3).attr("opacity", 0));
    const title = s.append("text").attr("x", 500).attr("y", 130).attr("text-anchor", "middle").attr("fill", "#4a2a17").attr("font-weight", 800).attr("font-size", 78).text("4 × (1 − 1/3 + 1/5 − 1/7 + …)"), val = s.append("text").attr("x", 500).attr("y", 230).attr("text-anchor", "middle").attr("fill", "#2d6fa0").attr("font-weight", 800).attr("font-size", 72), val2 = s.append("text").attr("x", 500).attr("y", 330).attr("text-anchor", "middle").attr("fill", "#2f7d4f").attr("font-weight", 800).attr("font-size", 0);
    const T = { pi: k.pill2(380, 800, "ഇതിലേക്ക് അടുക്കുന്നു", "CREEPING TOWARDS PI", "#c8442f"), fix: k.pill2(820, 800, "മാധവന്റെ തിരുത്തൽ പദം", "MADHAVA'S CORRECTION TERM", "#2f7d4f") };
    const TP = { pi: [380, 800], fix: [820, 800] };
    const move = k.camMover(p.cams || [{ at: 0, x: 500, y: 520, z: 1 }]);
    return (lt, d) => { const f = lt / d; move(f, d);
      const tm = prog(f, at(a, "terms"), 0.45), pi = prog(f, at(a, "pi"), 0.03), fx = prog(f, at(a, "fix"), 0.3), n = Math.max(1, Math.min(N, Math.floor(1 + (N - 1) * tm))), m = Math.max(0, Math.min(N, Math.floor(1 + (N - 1) * fx)));
      piLine.attr("opacity", pi); d1.forEach((q, i) => q.attr("opacity", tm > 0 && i < n ? 1 : 0)); d2.forEach((q, i) => q.attr("opacity", fx > 0 && i < m ? 1 : 0));
      z1.attr("d", n > 1 && tm > 0 ? "M " + v1.slice(0, n).map((v, i) => `${X(i + 1)} ${Yv(v)}`).join(" L ") : "M 0 0"); z2.attr("d", m > 1 && fx > 0 ? "M " + v2.slice(0, m).map((v, i) => `${X(i + 1)} ${Yv(v)}`).join(" L ") : "M 0 0");
      val.text(tm > 0 ? `${n} പദങ്ങൾ  →  ${v1[n - 1].toFixed(5)}` : "").attr("font-size", 64); val2.attr("font-size", fx > 0 ? 64 : 0).text(fx > 0 ? `+ തിരുത്തൽ  →  ${v2[Math.max(0, m - 1)].toFixed(7)}` : "").attr("y", 330);
      Object.keys(T).forEach((nn) => pop(T[nn], TP[nn][0], TP[nn][1], f, d, at(a, nn))); };
  };

  // ================= rainbow: a ray of sunlight inside one raindrop (refraction, one reflection, refraction), the colours fan out, the 42 degree angle, and then the full circle seen from above =================
  // p.at = {ray, split, reflect, exit, angle, circle}
  K.rainbow = (g, p, c) => {
    const id = c.id + rid(), k = M.setKit(g, c, id), s = k.set, a = p.at || {};
    s.append("rect").attr("x", -1400).attr("y", -900).attr("width", 6800).attr("height", 2800).attr("fill", k.lg("sky", [[0, "#5fa8d6"], [1, "#dff1fa"]]));
    const O = [520, 500], R = 300, b = 0.86, cols = ["#e23b2e", "#f08a24", "#f6d12a", "#3aa84a", "#2d8fd0", "#3b4fb8", "#7a3fb0"], nn = cols.map((_, i) => 1.30 + (0.075 * i) / 6);
    const P = (an) => [O[0] + R * Math.cos(an), O[1] - R * Math.sin(an)], ang = (v) => Math.atan2(-v[1], v[0]);                 // math angles (y up) mapped to screen
    const i1 = Math.asin(b), phi1 = Math.PI - i1, p1 = P(phi1);
    const paths = nn.map((n) => { const r = Math.asin(b / n), phi2 = phi1 - (Math.PI - 2 * r), p2 = P(phi2), phi3 = phi2 - (Math.PI - 2 * r), p3 = P(phi3);
      const d1 = [Math.cos(phi1 + Math.PI + r), Math.sin(phi1 + Math.PI + r)], nrm = [Math.cos(phi2), Math.sin(phi2)], dt = d1[0] * nrm[0] + d1[1] * nrm[1], d2 = [d1[0] - 2 * dt * nrm[0], d1[1] - 2 * dt * nrm[1]];
      const n3 = phi3, aa = Math.atan2(d2[1], d2[0]) - n3, a2 = Math.atan2(Math.sin(aa), Math.cos(aa)), t = Math.asin(Math.min(1, n * Math.sin(Math.abs(a2)))), ex = n3 + Math.sign(a2) * t;
      return { p2, p3, ex: [Math.cos(ex), -Math.sin(ex)] }; });
    const sun = s.append("g"); sun.append("circle").attr("cx", -980).attr("cy", 140).attr("r", 120).attr("fill", "#ffe08a"); sun.append("circle").attr("cx", -980).attr("cy", 140).attr("r", 300).attr("fill", k.rg("sun", [[0, "#fff1b0", 0.6], [1, "#fff1b0", 0]]));
    for (const yy of [200, 300, 400, 560, 640]) s.append("line").attr("x1", -870).attr("x2", O[0] - R * 0.95).attr("y1", yy).attr("y2", yy).attr("stroke", "#fff8d0").attr("stroke-width", 5).attr("opacity", 0.55).attr("stroke-dasharray", "30 18");
    s.append("circle").attr("cx", O[0]).attr("cy", O[1]).attr("r", R).attr("fill", "#bfe8fb").attr("fill-opacity", 0.55).attr("stroke", "#fff").attr("stroke-width", 8).attr("filter", k.sh);
    s.append("circle").attr("cx", O[0] - 80).attr("cy", O[1] - 100).attr("r", 60).attr("fill", "#fff").attr("opacity", 0.25);
    const yRay = O[1] - R * b, ray = s.append("line").attr("x1", -870).attr("y1", yRay).attr("x2", p1[0]).attr("y2", yRay).attr("stroke", "#fff6c8").attr("stroke-width", 12).attr("stroke-linecap", "round").attr("opacity", 0);
    const inner = paths.map((q, i) => s.append("path").attr("d", `M ${p1[0]} ${p1[1]} L ${q.p2[0]} ${q.p2[1]} L ${q.p3[0]} ${q.p3[1]}`).attr("fill", "none").attr("stroke", cols[i]).attr("stroke-width", 6).attr("stroke-linecap", "round").attr("opacity", 0));
    const outer = paths.map((q, i) => s.append("path").attr("d", `M ${q.p3[0]} ${q.p3[1]} l ${q.ex[0] * 760} ${q.ex[1] * 760}`).attr("fill", "none").attr("stroke", cols[i]).attr("stroke-width", 8).attr("stroke-linecap", "round").attr("opacity", 0));
    const flash = s.append("circle").attr("cx", paths[3].p2[0]).attr("cy", paths[3].p2[1]).attr("r", 30).attr("fill", "#fff").attr("opacity", 0);
    const eye = s.append("g").attr("opacity", 0).attr("transform", `translate(${paths[3].p3[0] + paths[3].ex[0] * 790},${paths[3].p3[1] + paths[3].ex[1] * 790})`); eye.append("ellipse").attr("rx", 56).attr("ry", 34).attr("fill", "#fff").attr("stroke", "#4a2a17").attr("stroke-width", 6); eye.append("circle").attr("cx", 14).attr("r", 18).attr("fill", "#4a2a17");
    const arcR = 230, ex = paths[0].ex, a0 = Math.atan2(0, -1), a1 = Math.atan2(ex[1], ex[0]), q3 = paths[3].p3;
    const angG = s.append("g").attr("opacity", 0); angG.append("line").attr("x1", q3[0]).attr("y1", q3[1]).attr("x2", q3[0] - 520).attr("y2", q3[1]).attr("stroke", "#fff").attr("stroke-width", 5).attr("stroke-dasharray", "12 10");
    angG.append("path").attr("d", `M ${q3[0] - arcR} ${q3[1]} A ${arcR} ${arcR} 0 0 0 ${q3[0] + ex[0] * arcR} ${q3[1] + ex[1] * arcR}`).attr("fill", "none").attr("stroke", "#c8442f").attr("stroke-width", 9);
    const RX = 2700, RY = 520, rings = cols.map((col, i) => s.append("circle").attr("cx", RX).attr("cy", RY).attr("r", 520 - i * 38).attr("fill", "none").attr("stroke", col).attr("stroke-width", 40).attr("opacity", 0.9));
    const ground = s.append("rect").attr("x", RX - 800).attr("y", RY + 80).attr("width", 1600).attr("height", 900).attr("fill", k.lg("grd", [[0, "#6aa84f"], [1, "#3f7a35"]]));
    const T = { ray: k.pill2(-300, yRay - 70, "സൂര്യപ്രകാശം", "SUNLIGHT ENTERS THE DROP", "#c8a000"), split: k.pill2(560, 160, "വളഞ്ഞ് നിറങ്ങളായി പിരിയുന്നു", "IT BENDS AND SPLITS INTO COLOURS", "#c8442f"), reflect: k.pill2(900, 520, "ഉള്ളിൽ ഒരു പ്രതിഫലനം", "ONE REFLECTION INSIDE", "#2d6fa0"),
      angle: k.pill2(q3[0] - 250, q3[1] + 140, "≈ 42°", "ANGLE FROM THE SUN'S OPPOSITE", "#c8442f"), circle: k.pill2(RX, RY - 640, "എല്ലാ തുള്ളികളും ചേർന്ന വൃത്തം", "ALL THE DROPS MAKE A CIRCLE", "#2f7d4f"), ground: k.pill2(RX, RY + 220, "നിലം മറയ്ക്കുന്നു", "THE GROUND HIDES THE REST", "#7b4a2b") };
    const TP = { ray: [-300, yRay - 70], split: [560, 160], reflect: [900, 520], angle: [q3[0] - 250, q3[1] + 140], circle: [RX, RY - 640], ground: [RX, RY + 220] };
    const move = k.camMover(p.cams || [{ at: 0, x: 500, y: 500, z: 1 }]);
    return (lt, d) => { const f = lt / d; move(f, d);
      const ry = prog(f, at(a, "ray"), 0.04), sp = prog(f, at(a, "split"), 0.05), rf = prog(f, at(a, "reflect"), 0.03), ext = prog(f, at(a, "exit"), 0.06), an = prog(f, at(a, "angle"), 0.04), ci = prog(f, at(a, "circle"), 0.04), gr = prog(f, at(a, "ground"), 0.06), full = prog(f, at(a, "full"), 0.15);
      ray.attr("opacity", ry); inner.forEach((q) => q.attr("opacity", sp)); flash.attr("opacity", rf * (0.4 + 0.5 * Math.sin(lt * 6))).attr("r", 24 + 10 * Math.sin(lt * 6)); outer.forEach((q) => q.attr("opacity", ext)); eye.attr("opacity", ext); angG.attr("opacity", an);
      ground.attr("opacity", gr > 0 ? 1 - full : 1); rings.forEach((q) => q.attr("opacity", ci * 0.9));
      Object.keys(T).forEach((n) => pop(T[n], TP[n][0], TP[n][1], f, d, at(a, n === "ground" ? "ground" : n))); };
  };
})();
