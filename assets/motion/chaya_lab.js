// Science Chaya "lab" scenes: one scene kind, K.lab, with many cut-away modes (a close look inside something). p = {mode, bg, at: {stage: fraction}, tags: [{ml, en, x, y, col, at}], cams}.
// Drawn in a 1000 x 1000 set like the other hand-made scenes; the object sits near (500, 560). Add a mode by adding a function to MODES.
(() => {
  const M = window.MOTION, d3 = window.d3, { E, prog, clamp, lerp, rid, rnd, smooth, at, K } = M;
  const pop = (pg, x, y, f, d, when) => { const kk = E.back(clamp(((f - when) * d) / 0.4)); pg.attr("opacity", clamp(kk * 2)).attr("transform", `translate(${x},${y}) scale(${0.6 + 0.4 * kk})`); };
  const dots = (g, n, fill, r, seed = 0) => Array.from({ length: n }, (_, i) => g.append("circle").attr("r", r * (0.7 + 0.6 * rnd(i + seed))).attr("fill", fill).attr("opacity", 0).datum(i));
  const BG = (s, k, kind) => {
    const g = { kitchen: [["#f6e3c6", "#ecd2ab"], "#a8774a"], night: [["#050b1f", "#1b2c55"], "#10241a"], sky: [["#9fb6c4", "#e3ebee"], "#6a8f3a"], dusk: [["#f0a679", "#fde7c8"], "#7a5a3a"], dark: [["#17110c", "#3a2a1d"], "#2a1c12"] }[kind || "kitchen"];
    s.append("rect").attr("x", -1400).attr("y", -600).attr("width", 3800).attr("height", 1800).attr("fill", k.lg("bg", g[0].map((c, i) => [i, c])));
    s.append("rect").attr("x", -1400).attr("y", 880).attr("width", 3800).attr("height", 600).attr("fill", g[1]).attr("opacity", 0.9);
  };
  const MODES = {};

  // ---- first rain on dry soil: plant oil + geosmin from bacteria, a raindrop lands and throws scented droplets into the air ----   at: oil, geos, drop, spray
  MODES.petrichor = (s, k, a) => {
    s.append("rect").attr("x", -1400).attr("y", 600).attr("width", 3800).attr("height", 700).attr("fill", k.lg("soil", [[0, "#9a6f45"], [1, "#5a3e24"]])); s.append("rect").attr("x", -1400).attr("y", 590).attr("width", 3800).attr("height", 22).attr("fill", "#6aa04a");
    for (let i = 0; i < 70; i++) s.append("circle").attr("cx", -300 + rnd(i) * 1600).attr("cy", 640 + rnd(i + 3) * 380).attr("r", 3 + rnd(i + 7) * 7).attr("fill", "#3f2c1a").attr("opacity", 0.4);
    const st = s.append("g").attr("transform", "translate(230,590)"); st.append("path").attr("d", "M 0 0 Q 10 -80 0 -170").attr("stroke", "#3f8a3a").attr("stroke-width", 10).attr("fill", "none"); for (const [x, y, r] of [[-40, -110, -30], [38, -150, 30], [-30, -60, -20]]) st.append("ellipse").attr("cx", x).attr("cy", y).attr("rx", 44).attr("ry", 18).attr("fill", "#4fa044").attr("transform", `rotate(${r} ${x} ${y})`);
    const oil = dots(s, 34, "#ffd23f", 8, 1).map((q, i) => q.attr("cx", 60 + rnd(i + 20) * 880).attr("cy", 650 + rnd(i + 8) * 300)), bact = Array.from({ length: 16 }, (_, i) => s.append("ellipse").attr("rx", 15).attr("ry", 8).attr("fill", "#8fd05a").attr("stroke", "#3f6a2a").attr("stroke-width", 2).attr("opacity", 0).attr("cx", 80 + rnd(i + 40) * 840).attr("cy", 660 + rnd(i + 5) * 280).datum(i));
    const geo = dots(s, 22, "#2fb86a", 6, 4), drop = s.append("path").attr("d", "M 0 -34 Q 22 4 18 14 Q 14 30 0 30 Q -14 30 -18 14 Q -22 4 0 -34 Z").attr("fill", "#2a8fd0").attr("opacity", 0), ring = s.append("ellipse").attr("cx", 560).attr("cy", 604).attr("fill", "none").attr("stroke", "#cfeefc").attr("stroke-width", 6).attr("opacity", 0);
    const spr = dots(s, 40, "#f3e6b0", 7, 9), waves = [0, 1, 2].map((i) => s.append("path").attr("fill", "none").attr("stroke", "#ffd23f").attr("stroke-width", 6).attr("stroke-linecap", "round").attr("opacity", 0).datum(i));
    return (lt, f, d, S) => { const o = S("oil"), g2 = S("geos"), dr = S("drop", 0.07), sp = S("spray", 0.18);
      oil.forEach((q, i) => q.attr("opacity", o).attr("r", 8 * (0.8 + 0.3 * Math.sin(lt * 3 + i)))); bact.forEach((q) => q.attr("opacity", g2).attr("transform", `rotate(${Math.sin(lt * 2 + q.datum()) * 20} ${q.attr("cx")} ${q.attr("cy")})`));
      geo.forEach((q, i) => { const u = (lt * 0.5 + rnd(i)) % 1; q.attr("cx", 100 + rnd(i + 30) * 800 + Math.sin(u * 6) * 12).attr("cy", 880 - u * 260).attr("opacity", g2 * (1 - u) * 0.9); });
      drop.attr("opacity", dr > 0 && dr < 1 ? 1 : 0).attr("transform", `translate(560,${lerp(-200, 575, dr)})`);
      const hit = clamp((f - at(a, "drop") - 0.07 * 0.9) * d / 0.6); ring.attr("opacity", dr >= 1 ? 1 - hit : 0).attr("rx", 20 + 170 * hit).attr("ry", 6 + 26 * hit);
      spr.forEach((q, i) => { const u = clamp(sp * 1.1 - rnd(i) * 0.15), an = (rnd(i + 2) - 0.5) * 2.4; q.attr("cx", 560 + Math.sin(an) * 330 * u).attr("cy", 590 - (Math.cos(an) * 260 * u - 190 * u * u)).attr("opacity", u > 0 && u < 1 ? 0.9 * (1 - u * 0.6) : 0); });
      waves.forEach((q, i) => { const u = (lt * 0.4 + i / 3) % 1; q.attr("d", `M ${420 + i * 100} ${520 - u * 150} q 20 -22 0 -44 t 0 -44`).attr("opacity", sp > 0.3 ? 0.7 * (1 - u) : 0); }); };
  };

  // ---- a firefly's cold light: luciferin meets oxygen inside the lantern; compare with a bulb that wastes most as heat ----   at: glow, chem, cold, bulb
  MODES.firefly = (s, k, a) => {
    for (let i = 0; i < 60; i++) s.append("circle").attr("cx", -1200 + rnd(i) * 3400).attr("cy", -400 + rnd(i + 5) * 900).attr("r", 1.5 + rnd(i + 3) * 2.4).attr("fill", "#fff").attr("opacity", 0.4 + rnd(i) * 0.6);
    for (let i = 0; i < 28; i++) s.append("path").attr("d", `M ${-1300 + i * 120} 900 q 4 -${70 + rnd(i) * 80} ${rnd(i + 2) * 30} -${110 + rnd(i + 3) * 80}`).attr("stroke", "#1b3a24").attr("stroke-width", 9).attr("fill", "none");
    const body = s.append("g").attr("transform", "translate(380,330)"); body.append("ellipse").attr("cx", 20).attr("cy", -60).attr("rx", 120).attr("ry", 50).attr("fill", "#d8dde8").attr("opacity", 0.55).attr("transform", "rotate(-25 20 -60)"); body.append("ellipse").attr("rx", 150).attr("ry", 60).attr("fill", "#3a2a1d"); body.append("circle").attr("cx", -150).attr("cy", 4).attr("r", 40).attr("fill", "#2a1c12"); body.append("path").attr("d", "M -176 -34 q -30 -50 -60 -40 M -160 -40 q -10 -60 -34 -64").attr("stroke", "#2a1c12").attr("stroke-width", 6).attr("fill", "none");
    const abd = body.append("ellipse").attr("cx", 118).attr("cy", 10).attr("rx", 62).attr("ry", 48).attr("fill", "#d8ff5a"), glow = s.append("circle").attr("cx", 500).attr("cy", 340).attr("r", 300).attr("fill", k.rg("fg", [[0, "#e6ff6a", 0.75], [1, "#e6ff6a", 0]])).attr("opacity", 0);
    const lens = s.append("g"); lens.append("circle").attr("cx", 520).attr("cy", 760).attr("r", 210).attr("fill", "#101a14").attr("stroke", "#d8ff5a").attr("stroke-width", 8); s.append("path").attr("d", "M 498 380 L 440 600 M 560 372 L 590 600").attr("stroke", "#d8ff5a").attr("stroke-width", 4).attr("stroke-dasharray", "10 8").attr("opacity", 0.7);
    const luci = dots(s, 14, "#ffd23f", 9, 1), oxy = dots(s, 14, "#4aa8ff", 9, 5), flashes = dots(s, 12, "#fff", 14, 7), phot = Array.from({ length: 16 }, (_, i) => s.append("line").attr("stroke", "#e6ff6a").attr("stroke-width", 5).attr("stroke-linecap", "round").attr("opacity", 0).datum(i));
    const bars = s.append("g").attr("opacity", 0).attr("transform", "translate(900,540)"), bw = 360; bars.append("text").attr("x", 0).attr("y", -20).attr("fill", "#fff").attr("font-weight", 800).attr("font-size", 30).text("മിന്നാമിനുങ്ങ്"); bars.append("rect").attr("width", bw).attr("height", 46).attr("rx", 10).attr("fill", "#e23b2e").attr("opacity", 0.5); bars.append("rect").attr("width", bw * 0.94).attr("height", 46).attr("rx", 10).attr("fill", "#d8ff5a");
    bars.append("text").attr("y", 130).attr("fill", "#fff").attr("font-weight", 800).attr("font-size", 30).text("ബൾബ്"); bars.append("rect").attr("y", 150).attr("width", bw).attr("height", 46).attr("rx", 10).attr("fill", "#e23b2e").attr("opacity", 0.9); bars.append("rect").attr("y", 150).attr("width", bw * 0.1).attr("height", 46).attr("rx", 10).attr("fill", "#ffe9a8");
    bars.append("text").attr("x", 0).attr("y", 235).attr("fill", "#ffe9a8").attr("font-size", 24).attr("font-weight", 700).text("മഞ്ഞ = വെളിച്ചം   ചുവപ്പ് = ചൂട്");
    const bulb = M.chayaIcon(s, "bulb", 1100, 380, 200).attr("opacity", 0), heat = Array.from({ length: 5 }, (_, i) => s.append("path").attr("fill", "none").attr("stroke", "#ff7a3c").attr("stroke-width", 7).attr("stroke-linecap", "round").attr("opacity", 0).datum(i));
    return (lt, f, d, S) => { const gl = S("glow", 0.04), ch = S("chem"), co = S("cold"), bu = S("bulb");
      const pulse = 0.55 + 0.45 * Math.sin(lt * 2.4); glow.attr("opacity", gl * pulse); abd.attr("fill", gl > 0 ? "#f0ff7a" : "#8a9a3a").attr("opacity", 0.55 + 0.45 * gl * pulse);
      luci.forEach((q, i) => q.attr("cx", 520 + Math.cos(lt * 0.9 + i * 1.7) * 140 * (0.4 + 0.6 * rnd(i))).attr("cy", 760 + Math.sin(lt * 1.1 + i * 2.1) * 120 * (0.4 + 0.6 * rnd(i + 1))).attr("opacity", ch > 0 ? 0.95 : 0));
      oxy.forEach((q, i) => q.attr("cx", 520 + Math.cos(lt * 1.2 + i * 2.3 + 1) * 140 * (0.4 + 0.6 * rnd(i + 2))).attr("cy", 760 + Math.sin(lt * 0.8 + i * 1.3) * 120 * (0.4 + 0.6 * rnd(i + 3))).attr("opacity", ch > 0 ? 0.95 : 0));
      flashes.forEach((q, i) => { const u = (lt * 0.8 + rnd(i)) % 1; q.attr("cx", 520 + (rnd(i + 3) - 0.5) * 260).attr("cy", 760 + (rnd(i + 8) - 0.5) * 240).attr("opacity", ch * (u < 0.3 ? 1 - u / 0.3 : 0)); });
      phot.forEach((q, i) => { const u = (lt * 1.1 + rnd(i)) % 1, an = rnd(i + 4) * Math.PI * 2, r0 = 40 + u * 150; q.attr("x1", 520 + Math.cos(an) * r0).attr("y1", 760 + Math.sin(an) * r0).attr("x2", 520 + Math.cos(an) * (r0 + 24)).attr("y2", 760 + Math.sin(an) * (r0 + 24)).attr("opacity", ch * (1 - u)); });
      bars.attr("opacity", co); bulb.attr("opacity", bu).attr("transform", "translate(1100,380) scale(2)"); heat.forEach((q, i) => { const u = (lt * 0.7 + i / 5) % 1; q.attr("d", `M ${1040 + i * 30} ${300 - u * 120} q 12 -18 0 -36 t 0 -36`).attr("opacity", bu * (1 - u)); }); };
  };

  // ---- the goli soda bottle: gas pressure holds the marble against a rubber ring; push it in and the gas rushes out ----   at: bubbles, press, seal, push
  MODES.goli = (s, k, a) => {
    s.append("rect").attr("x", 330).attr("y", 880).attr("width", 340).attr("height", 24).attr("rx", 8).attr("fill", "#8a5a36");
    const bottle = "M 460 250 L 540 250 L 540 400 Q 540 440 610 470 Q 640 490 640 540 L 640 860 Q 640 880 620 880 L 380 880 Q 360 880 360 860 L 360 540 Q 360 490 390 470 Q 460 440 460 400 Z";
    s.append("path").attr("d", bottle).attr("fill", "#9fe0e8").attr("fill-opacity", 0.35).attr("stroke", "#5aa8b8").attr("stroke-width", 10).attr("filter", k.sh);
    const liq = s.append("path").attr("d", "M 368 560 L 632 560 L 632 860 Q 632 872 620 872 L 380 872 Q 368 872 368 860 Z").attr("fill", "#4fb8e8").attr("opacity", 0.75);
    s.append("ellipse").attr("cx", 500).attr("cy", 330).attr("rx", 40).attr("ry", 10).attr("fill", "none").attr("stroke", "#8a4a2a").attr("stroke-width", 12);
    const bub = dots(s, 40, "#fff", 8, 2), marble = s.append("circle").attr("r", 33).attr("fill", k.rg("mr", [[0, "#bfe8ff", 1], [1, "#2d8fd0", 1]])).attr("stroke", "#fff").attr("stroke-width", 3);
    const ar = [-24, 0, 24].map((x) => s.append("path").attr("fill", "none").attr("stroke", "#c8442f").attr("stroke-width", 9).attr("stroke-linecap", "round").attr("opacity", 0).datum(x)), glowRing = s.append("ellipse").attr("cx", 500).attr("cy", 330).attr("rx", 44).attr("ry", 14).attr("fill", "none").attr("stroke", "#ffd23f").attr("stroke-width", 7).attr("opacity", 0);
    const thumb = s.append("rect").attr("x", 488).attr("width", 24).attr("height", 160).attr("rx", 12).attr("fill", "#c68b5e").attr("opacity", 0), gas = dots(s, 22, "#e8f6ff", 10, 3);
    return (lt, f, d, S) => { const bb = S("bubbles", 0.05), pr = S("press"), se = S("seal", 0.04), pu = S("push", 0.07);
      bub.forEach((q, i) => { const u = (lt * (0.4 + rnd(i) * 0.4) + rnd(i + 4)) % 1; q.attr("cx", 385 + rnd(i + 9) * 230).attr("cy", 860 - u * 290).attr("opacity", bb * (1 - u * 0.5)); });
      const my = lerp(354, 408, E.out(pu)); marble.attr("cx", 500).attr("cy", my);
      ar.forEach((q) => q.attr("d", `M ${500 + q.datum()} 540 L ${500 + q.datum()} ${470 - 22 * Math.sin(lt * 6)}`).attr("opacity", pr * (1 - pu)));
      glowRing.attr("opacity", se * (1 - pu) * (0.6 + 0.4 * Math.sin(lt * 5)));
      thumb.attr("opacity", pu > 0 ? 1 : 0).attr("y", lerp(80, 220, E.out(pu)) - 160 + 160);
      gas.forEach((q, i) => { const u = clamp(pu * 1.2 - rnd(i) * 0.3); q.attr("cx", 500 + (rnd(i + 2) - 0.5) * 60 + Math.sin(u * 8 + i) * 40 * u).attr("cy", 330 - u * 330).attr("opacity", u > 0 && u < 1 ? 0.85 * (1 - u) : 0); }); };
  };

  // ---- a cassette: magnetic particles on the tape line up with the sound while recording, and play back as a signal ----   at: tape, record, play
  MODES.cassette = (s, k, a) => {
    const cs = s.append("g").attr("filter", k.sh); cs.append("rect").attr("x", 230).attr("y", 220).attr("width", 540).attr("height", 340).attr("rx", 26).attr("fill", "#3a3a40").attr("stroke", "#1b1b20").attr("stroke-width", 8); cs.append("rect").attr("x", 270).attr("y", 260).attr("width", 460).attr("height", 150).attr("rx", 14).attr("fill", "#f3efe6"); cs.append("path").attr("d", "M 300 520 L 340 450 L 660 450 L 700 520 Z").attr("fill", "#2a2a30");
    const reels = [[380, 335], [620, 335]].map(([x, y]) => { const g2 = s.append("g").attr("transform", `translate(${x},${y})`); g2.append("circle").attr("r", 58).attr("fill", "#2a1a10"); g2.append("circle").attr("r", 30).attr("fill", "#f3efe6"); const sp = g2.append("g"); for (let i = 0; i < 6; i++) sp.append("rect").attr("x", -4).attr("y", -30).attr("width", 8).attr("height", 14).attr("fill", "#2a1a10").attr("transform", `rotate(${i * 60})`); return sp; });
    s.append("path").attr("d", "M 380 393 L 330 520 L 670 520 L 620 393").attr("fill", "none").attr("stroke", "#6b3f1f").attr("stroke-width", 7);
    const strip = s.append("g"), N = 24, parts = Array.from({ length: N }, (_, i) => { const g2 = strip.append("g").attr("transform", `translate(${130 + i * 32},800)`); g2.append("rect").attr("x", -12).attr("y", -4).attr("width", 12).attr("height", 8).attr("fill", "#e23b2e"); g2.append("rect").attr("x", 0).attr("y", -4).attr("width", 12).attr("height", 8).attr("fill", "#2d6fa0"); return g2; });
    strip.append("rect").attr("x", 100).attr("y", 770).attr("width", 800).attr("height", 60).attr("rx", 8).attr("fill", "none").attr("stroke", "#6b3f1f").attr("stroke-width", 5); strip.attr("opacity", 0);
    const wave = s.append("path").attr("fill", "none").attr("stroke", "#2f7d4f").attr("stroke-width", 8).attr("stroke-linecap", "round").attr("opacity", 0), head = s.append("rect").attr("y", 706).attr("width", 20).attr("height", 40).attr("rx", 6).attr("fill", "#5e6b78").attr("opacity", 0);
    const sig = s.append("path").attr("fill", "none").attr("stroke", "#c8442f").attr("stroke-width", 8).attr("stroke-linecap", "round").attr("opacity", 0), spk = s.append("g").attr("transform", "translate(940,640)").attr("opacity", 0); spk.append("rect").attr("x", -26).attr("y", -42).attr("width", 52).attr("height", 84).attr("rx", 10).attr("fill", "#2a1a10"); spk.append("circle").attr("r", 20).attr("fill", "#8d99a6"); spk.append("circle").attr("cy", -26).attr("r", 7).attr("fill", "#8d99a6");
    const sw = (x) => Math.sin(x * 0.011) * 0.7 + Math.sin(x * 0.027 + 1) * 0.3;
    return (lt, f, d, S) => { const tp = S("tape"), rc = S("record", 0.3), pl = S("play", 0.3);
      reels.forEach((r, i) => r.attr("transform", `rotate(${lt * (i ? -90 : 90)})`)); strip.attr("opacity", tp);
      parts.forEach((q, i) => { const aligned = i / N < rc ? sw(130 + i * 32) * 70 : (rnd(i) - 0.5) * 360; q.attr("transform", `translate(${130 + i * 32},800) rotate(${aligned})`); });
      const wpts = Array.from({ length: 41 }, (_, i) => [130 + i * 19.2, 700 - sw(130 + i * 19.2) * 50]); wave.attr("d", "M " + wpts.filter((q, i) => (q[0] - 130) / 770 <= rc).map((q) => q.join(" ")).join(" L ")).attr("opacity", rc > 0 ? 1 : 0);
      head.attr("opacity", pl > 0 ? 1 : 0).attr("x", 130 + pl * 740); const sp2 = Array.from({ length: 30 }, (_, i) => [130 + i * 26.5, 700 + 0]); sig.attr("d", "M " + sp2.filter((q) => (q[0] - 130) / 770 <= pl).map((q) => `${q[0]} ${620 - sw(q[0]) * 60}`).join(" L ")).attr("opacity", pl > 0 ? 1 : 0); spk.attr("opacity", pl); };
  };

  // ---- osmosis: salt on a cut fruit draws the water out through the cell walls ----   at: salt, flow, mouth
  MODES.osmosis = (s, k, a) => {
    const fr = s.append("g").attr("filter", k.sh); fr.append("path").attr("d", "M 200 620 Q 500 330 800 620 Q 760 800 500 840 Q 240 800 200 620 Z").attr("fill", "#f6b945").attr("stroke", "#c8442f").attr("stroke-width", 10);
    const cells = Array.from({ length: 16 }, (_, i) => { const x = 280 + (i % 6) * 88 + (Math.floor(i / 6) % 2) * 40, y = 640 + Math.floor(i / 6) * 70; s.append("circle").attr("cx", x).attr("cy", y).attr("r", 34).attr("fill", "#ffe08a").attr("stroke", "#c98a22").attr("stroke-width", 4); return [x, y]; });
    const crystals = Array.from({ length: 18 }, (_, i) => s.append("rect").attr("width", 16).attr("height", 16).attr("rx", 3).attr("fill", "#fff").attr("stroke", "#9aa3aa").attr("stroke-width", 2).attr("opacity", 0).datum(i)), water = Array.from({ length: 26 }, (_, i) => s.append("circle").attr("r", 8).attr("fill", "#4fb8e8").attr("opacity", 0).datum(i));
    const ar = s.append("path").attr("d", "M 850 760 L 850 520 M 820 560 L 850 520 L 880 560").attr("fill", "none").attr("stroke", "#c8442f").attr("stroke-width", 12).attr("stroke-linecap", "round").attr("opacity", 0), per = M.chayaIcon(s, "person", 140, 420, 200).attr("opacity", 0), dr = M.chayaIcon(s, "drop", 140, 520, 60).attr("opacity", 0);
    return (lt, f, d, S) => { const sl = S("salt", 0.05), fl = S("flow", 0.12), mo = S("mouth", 0.05);
      crystals.forEach((q) => { const i = q.datum(); q.attr("x", 300 + (i % 9) * 52 + rnd(i) * 10).attr("y", 462 + Math.sin((i % 9) * 0.7) * -20 - Math.floor(i / 9) * 26).attr("opacity", sl).attr("transform", `rotate(${rnd(i + 3) * 40} ${300 + (i % 9) * 52} 470)`); });
      water.forEach((q) => { const i = q.datum(), c2 = cells[i % cells.length], u = (lt * 0.4 + rnd(i)) % 1; q.attr("cx", lerp(c2[0], 330 + (i % 9) * 48, u)).attr("cy", lerp(c2[1], 520, u)).attr("opacity", fl * (u < 0.9 ? 0.9 : 0)); });
      ar.attr("opacity", fl); per.attr("opacity", mo).attr("transform", "translate(140,420) scale(2)"); dr.attr("opacity", mo * (0.5 + 0.5 * Math.sin(lt * 4))).attr("transform", `translate(130,${520 + ((lt * 60) % 80)}) scale(0.8)`); };
  };

  // ---- a kerosene lamp: the wick lifts the fuel by capillary action, only the vapour burns, the chimney draws air ----   at: wick, vapor, flame, chimney
  MODES.lamp = (s, k, a) => {
    s.append("circle").attr("cx", 500).attr("cy", 480).attr("r", 420).attr("fill", k.rg("lg", [[0, "#ffd88a", 0.55], [1, "#ffd88a", 0]]));
    const base = s.append("g").attr("filter", k.sh); base.append("path").attr("d", "M 360 700 Q 360 600 500 600 Q 640 600 640 700 Q 640 840 500 860 Q 360 840 360 700 Z").attr("fill", "#d9e8ec").attr("fill-opacity", 0.55).attr("stroke", "#8fb0b8").attr("stroke-width", 8); base.append("path").attr("d", "M 372 700 Q 380 840 500 852 Q 620 840 628 700 Z").attr("fill", "#e8a33d").attr("opacity", 0.85); base.append("rect").attr("x", 450).attr("y", 560).attr("width", 100).attr("height", 40).attr("fill", "#b8872a");
    s.append("rect").attr("x", 484).attr("y", 400).attr("width", 32).attr("height", 330).attr("fill", "#efe4c4").attr("stroke", "#a89878").attr("stroke-width", 3); s.append("rect").attr("x", 456).attr("y", 380).attr("width", 88).attr("height", 30).attr("rx", 8).attr("fill", "#b8872a");
    const chim = s.append("path").attr("d", "M 450 560 Q 380 540 410 330 Q 430 150 460 120 L 540 120 Q 570 150 590 330 Q 620 540 550 560 Z").attr("fill", "#d9e8ec").attr("fill-opacity", 0.28).attr("stroke", "#8fb0b8").attr("stroke-width", 7);
    const oilup = dots(s, 16, "#e8a33d", 7, 2), vap = Array.from({ length: 5 }, (_, i) => s.append("path").attr("fill", "none").attr("stroke", "#fff6c8").attr("stroke-width", 6).attr("stroke-linecap", "round").attr("opacity", 0).datum(i));
    const flame = s.append("g").attr("transform", "translate(500,382)").attr("opacity", 0); flame.append("path").attr("d", "M 0 -150 Q 52 -70 40 -18 Q 30 14 0 14 Q -30 14 -40 -18 Q -52 -70 0 -150 Z").attr("fill", "#ff9a2e"); flame.append("path").attr("d", "M 0 -90 Q 26 -44 20 -12 Q 14 8 0 8 Q -14 8 -20 -12 Q -26 -44 0 -90 Z").attr("fill", "#ffe27a");
    const air = Array.from({ length: 6 }, (_, i) => s.append("path").attr("fill", "none").attr("stroke", "#7fb8e8").attr("stroke-width", 7).attr("stroke-linecap", "round").attr("opacity", 0).datum(i));
    return (lt, f, d, S) => { const wk = S("wick", 0.06), vp = S("vapor", 0.05), fl = S("flame", 0.04), ch = S("chimney", 0.06);
      oilup.forEach((q, i) => { const u = (lt * 0.35 + rnd(i)) % 1; q.attr("cx", 494 + (rnd(i + 3) - 0.5) * 18).attr("cy", 700 - u * 290).attr("opacity", wk * (1 - u * 0.4)); });
      vap.forEach((q, i) => { const u = (lt * 0.6 + i / 5) % 1; q.attr("d", `M ${480 + i * 10} ${370 - u * 80} q 10 -16 0 -30`).attr("opacity", vp * (1 - u) * (1 - fl * 0.5)); });
      flame.attr("opacity", fl).attr("transform", `translate(500,382) scale(${0.95 + 0.07 * Math.sin(lt * 17)},${1 + 0.1 * Math.sin(lt * 13)})`);
      air.forEach((q, i) => { const u = (lt * 0.5 + i / 6) % 1, x = i < 3 ? 380 + i * 8 : 620 - (i - 3) * 8; q.attr("d", `M ${x} ${580 - u * 380} q ${(i < 3 ? 1 : -1) * 40} -30 ${(i < 3 ? 1 : -1) * 66} -60`).attr("opacity", ch * (1 - u)); }); };
  };

  // ---- zero shadow day: the Sun climbs to straight overhead and a stick's shadow shrinks to nothing ----   at: sun, noon
  MODES.sunshadow = (s, k, a) => {
    s.append("rect").attr("x", -1400).attr("y", 760).attr("width", 3800).attr("height", 700).attr("fill", k.lg("gr", [[0, "#c9b27a"], [1, "#8a6f3c"]]));
    const sun = s.append("g"); sun.append("circle").attr("r", 70).attr("fill", "#ffd23f"); sun.append("circle").attr("r", 210).attr("fill", k.rg("sg", [[0, "#fff1b0", 0.65], [1, "#fff1b0", 0]]));
    const ray = s.append("line").attr("stroke", "#ffe08a").attr("stroke-width", 6).attr("stroke-dasharray", "16 12").attr("opacity", 0.8), pole = s.append("rect").attr("x", 486).attr("y", 560).attr("width", 28).attr("height", 200).attr("rx", 6).attr("fill", "#6b3f1f"), shadow = s.append("path").attr("fill", "#2a1a10").attr("opacity", 0.55), tip = s.append("circle").attr("cx", 500).attr("cy", 560).attr("r", 18).attr("fill", "#6b3f1f");
    const lab = s.append("text").attr("x", 500).attr("y", 850).attr("text-anchor", "middle").attr("fill", "#fff6e2").attr("font-weight", 800).attr("font-size", 56).attr("opacity", 0);
    return (lt, f, d, S) => { const su = S("sun", 0.5), nz = S("noon", 0.05), ang = lerp(62, 0, E.inOut(su)) * Math.PI / 180, r = 640, sx = 500 - Math.sin(ang) * r, sy = 760 - Math.cos(ang) * r;
      sun.attr("transform", `translate(${sx},${sy})`); ray.attr("x1", sx).attr("y1", sy).attr("x2", 500).attr("y2", 560); const L = Math.tan(ang) * 200;
      shadow.attr("d", `M 486 760 L 514 760 L ${514 + L} 770 L ${486 + L} 770 Z`); tip.attr("transform", `translate(0,0)`); lab.attr("opacity", nz).text("നിഴൽ = 0"); };
  };

  // ---- tea leaf to tea: withering, rolling, oxidation, drying ----   at: wither, roll, oxid, dry
  MODES.tealeaf = (s, k, a) => {
    const leaf = s.append("g").attr("transform", "translate(500,560)"); const body = leaf.append("path").attr("d", "M -300 0 Q -100 -190 300 0 Q -100 190 -300 0 Z").attr("fill", "#3f9a4a").attr("stroke", "#1f5a2a").attr("stroke-width", 8); leaf.append("path").attr("d", "M -300 0 Q 0 6 300 0").attr("stroke", "#1f5a2a").attr("stroke-width", 7).attr("fill", "none");
    const cells = Array.from({ length: 22 }, (_, i) => leaf.append("circle").attr("cx", -230 + (i % 11) * 46).attr("cy", (i < 11 ? -42 : 42) + (rnd(i) - 0.5) * 20).attr("r", 15).attr("fill", "#6fd07a").attr("stroke", "#2f7d4f").attr("stroke-width", 3));
    const drops = dots(s, 14, "#4fb8e8", 9, 2), juice = dots(s, 20, "#ffd23f", 8, 4), o2 = dots(s, 14, "#4aa8ff", 8, 6), heat = Array.from({ length: 5 }, (_, i) => s.append("path").attr("fill", "none").attr("stroke", "#ff7a3c").attr("stroke-width", 8).attr("stroke-linecap", "round").attr("opacity", 0).datum(i));
    const mix = (c1, c2, t) => d3.interpolateRgb(c1, c2)(clamp(t));
    return (lt, f, d, S) => { const wi = S("wither", 0.12), ro = S("roll", 0.12), ox = S("oxid", 0.2), dr = S("dry", 0.1);
      leaf.attr("transform", `translate(500,${560 + 40 * wi}) scale(${1 - 0.18 * wi - 0.25 * ro - 0.1 * dr},${1 - 0.2 * ro - 0.15 * dr}) rotate(${-6 * wi})`);
      body.attr("fill", mix(mix("#3f9a4a", "#c8802f", ox), "#4a2a17", dr * 0.9)); cells.forEach((q, i) => q.attr("r", ro > 0 ? 15 * (1 - ro * 0.5) : 15).attr("fill", ro > 0.3 ? mix("#6fd07a", "#e8c35f", ox) : "#6fd07a").attr("cx", -230 + (i % 11) * 46 + (ro > 0.3 ? (rnd(i) - 0.5) * 30 * ro : 0)));
      drops.forEach((q, i) => { const u = (lt * 0.4 + rnd(i)) % 1; q.attr("cx", 260 + rnd(i + 3) * 480).attr("cy", 520 - u * 220).attr("opacity", wi * (1 - ro) * (1 - u)); });
      juice.forEach((q, i) => { const u = (lt * 0.5 + rnd(i)) % 1; q.attr("cx", 330 + rnd(i + 5) * 340).attr("cy", 540 + (rnd(i + 2) - 0.5) * 120 - u * 40).attr("opacity", ro * (1 - ox * 0.6) * 0.9); });
      o2.forEach((q, i) => { const u = (lt * 0.5 + rnd(i)) % 1; q.attr("cx", 180 + rnd(i + 7) * 640).attr("cy", 320 + u * 230).attr("opacity", ox * (1 - dr) * (1 - u * 0.4)); });
      heat.forEach((q, i) => { const u = (lt * 0.7 + i / 5) % 1; q.attr("d", `M ${340 + i * 80} ${700 - u * 130} q 16 -22 0 -44 t 0 -44`).attr("opacity", dr * (1 - u)); }); };
  };

  // ---- caffeine blocks adenosine at the brain's receptors ----   at: adenosine, caffeine
  MODES.adenosine = (s, k, a) => {
    s.append("path").attr("d", "M 100 760 Q 500 700 900 760 L 900 900 L 100 900 Z").attr("fill", "#d98a8a").attr("opacity", 0.9);
    const recs = [200, 340, 480, 620, 760].map((x) => { const g2 = s.append("g").attr("transform", `translate(${x},730)`); g2.append("path").attr("d", "M -40 0 L -40 -50 Q 0 -90 40 -50 L 40 0 Z").attr("fill", "#8a5ab8").attr("stroke", "#4a2a6a").attr("stroke-width", 5); return x; });
    const ad = recs.map((x, i) => s.append("circle").attr("r", 24).attr("fill", "#4a90d8").attr("stroke", "#1f4a8a").attr("stroke-width", 5).datum([x, i])), cf = recs.map((x, i) => s.append("path").attr("d", "M 0 -26 L 22 -13 L 22 13 L 0 26 L -22 13 L -22 -13 Z").attr("fill", "#8a5a2a").attr("stroke", "#4a2a17").attr("stroke-width", 5).attr("opacity", 0).datum([x, i]));
    const zzz = s.append("text").attr("x", 500).attr("y", 330).attr("text-anchor", "middle").attr("font-size", 110).attr("font-weight", 800).attr("fill", "#4a90d8").attr("opacity", 0).text("Zzz"), awake = s.append("text").attr("x", 500).attr("y", 330).attr("text-anchor", "middle").attr("font-size", 110).attr("font-weight", 800).attr("fill", "#2f7d4f").attr("opacity", 0).text("!");
    return (lt, f, d, S) => { const aa = S("adenosine", 0.1), cc = S("caffeine", 0.12);
      ad.forEach((q) => { const [x, i] = q.datum(), dock = aa * (1 - cc), u = (lt * 0.5 + i * 0.2) % 1; q.attr("cx", lerp(x + 60 * Math.sin(lt * 2 + i), x, dock)).attr("cy", lerp(380 + 80 * Math.cos(lt * 1.5 + i), 690, dock) + cc * (-180 - 60 * u)).attr("opacity", aa * (1 - cc * 0.35)); });
      cf.forEach((q) => { const [x, i] = q.datum(); q.attr("cx", x).attr("cy", lerp(300, 680, E.out(cc))).attr("opacity", cc); }); zzz.attr("opacity", aa * (1 - cc) * (0.6 + 0.4 * Math.sin(lt * 3))); awake.attr("opacity", cc); };
  };

  // ---- a cup: hot water pulls colour and flavour out of the tea faster; milk binds the harsh part ----   at: leaves, spread, hot, milk
  MODES.steep = (s, k, a) => {
    s.append("path").attr("d", "M 300 480 L 700 480 L 660 820 Q 655 860 610 860 L 390 860 Q 345 860 340 820 Z").attr("fill", "#fff").attr("fill-opacity", 0.3).attr("stroke", "#fff").attr("stroke-width", 8);
    const water = s.append("path").attr("d", "M 312 500 L 688 500 L 654 818 Q 650 846 612 846 L 388 846 Q 350 846 346 818 Z").attr("fill", "#d9eef7").attr("opacity", 0.8), col = s.append("path").attr("d", "M 312 500 L 688 500 L 654 818 Q 650 846 612 846 L 388 846 Q 350 846 346 818 Z").attr("fill", "#b5651d").attr("opacity", 0), milk = dots(s, 24, "#fff6e2", 16, 3);
    const gran = dots(s, 14, "#4a2a17", 11, 5).map((q, i) => q.attr("cx", 400 + rnd(i + 9) * 200).attr("cy", 780 + rnd(i) * 40)), steam = Array.from({ length: 4 }, (_, i) => s.append("path").attr("fill", "none").attr("stroke", "#fff").attr("stroke-width", 7).attr("stroke-linecap", "round").attr("opacity", 0).datum(i)), pips = dots(s, 20, "#b5651d", 7, 7);
    return (lt, f, d, S) => { const lv = S("leaves", 0.05), sp = S("spread", 0.3), ho = S("hot", 0.1), mk = S("milk", 0.1), speed = lerp(0.08, 0.22, ho);
      gran.forEach((q) => q.attr("opacity", lv)); const c = clamp(sp * (0.5 + 0.5 * ho) + ho * 0.1); col.attr("opacity", 0.75 * c).attr("fill", mix2(c, mk));
      pips.forEach((q, i) => { const u = (lt * speed * 3 + rnd(i)) % 1; q.attr("cx", 400 + rnd(i + 3) * 200 + Math.sin(lt * 2 + i) * 20 * c).attr("cy", 800 - u * 280 * c).attr("opacity", lv * (1 - u) * 0.9); });
      steam.forEach((q) => { const i = q.datum(), u = (lt * 0.6 + i / 4) % 1; q.attr("d", `M ${420 + i * 60} ${450 - u * 90} q 14 -20 0 -40`).attr("opacity", ho * (1 - u) * 0.9); });
      milk.forEach((q, i) => { const u = (lt * 0.4 + rnd(i)) % 1; q.attr("cx", 380 + rnd(i + 2) * 240 + Math.sin(lt + i) * 16 * mk).attr("cy", lerp(380, 600 + rnd(i + 4) * 200, E.out(mk)) + (mk > 0.9 ? 0 : -u * 20)).attr("opacity", mk * 0.8); }); };
    function mix2(c, mk) { return d3.interpolateRgb(d3.interpolateRgb("#e8c35f", "#b5651d")(c), "#d9a77a")(mk); }
  };

  // ---- a bowl: bacteria feed on sugar and make acid and gas; batter rises, or milk sets into curd ----   p.kind "idli" | "curd"; at: bact, eat, rise, set
  MODES.ferment = (s, k, a, p) => {
    const body = "M 230 520 L 770 520 Q 760 800 500 850 Q 240 800 230 520 Z";
    s.append("path").attr("d", body).attr("fill", "#fff").attr("fill-opacity", 0.35).attr("stroke", "#d9c9a8").attr("stroke-width", 12).attr("filter", k.sh);
    const fill = s.append("path").attr("fill", "#fff6e2").attr("opacity", 0.95);
    const bact = Array.from({ length: 18 }, (_, i) => s.append("ellipse").attr("rx", 16).attr("ry", 9).attr("fill", "#8fd05a").attr("stroke", "#3f6a2a").attr("stroke-width", 2).attr("opacity", 0).datum(i)), sugar = dots(s, 16, "#ffd23f", 8, 1), acid = dots(s, 16, "#e8613a", 7, 3), gas = dots(s, 34, "#fff", 10, 5), prot = dots(s, 22, "#f3d9a0", 14, 6);
    return (lt, f, d, S) => { const bc = S("bact", 0.08), ea = S("eat", 0.12), ri = S("rise", 0.3), se = S("set", 0.25), curd = p.kind === "curd";
      const top = curd ? 540 : lerp(600, 520, E.out(ri)); fill.attr("d", `M ${236 - (top < 560 ? 0 : 0)} ${top + 10} Q 500 ${top - 10 + (curd ? 0 : -50 * ri)} 764 ${top + 10} Q 756 790 500 840 Q 244 790 236 ${top + 10} Z`).attr("fill", curd ? d3.interpolateRgb("#fffdf6", "#f6e9c4")(se) : "#f4e6c0");
      bact.forEach((q) => { const i = q.datum(); q.attr("cx", 330 + rnd(i) * 340 + Math.sin(lt * 1.5 + i) * 18).attr("cy", 640 + rnd(i + 3) * 150 + Math.cos(lt * 1.3 + i) * 14).attr("opacity", bc).attr("transform", `rotate(${Math.sin(lt + i) * 30} ${330 + rnd(i) * 340} ${640 + rnd(i + 3) * 150})`); });
      sugar.forEach((q, i) => q.attr("cx", 320 + rnd(i + 7) * 360).attr("cy", 620 + rnd(i + 2) * 180).attr("opacity", bc * (1 - ea) * 0.9)); acid.forEach((q, i) => q.attr("cx", 330 + rnd(i + 9) * 340).attr("cy", 640 + rnd(i + 4) * 160 + Math.sin(lt * 2 + i) * 8).attr("opacity", ea * 0.9));
      gas.forEach((q, i) => { const u = (lt * (0.3 + rnd(i) * 0.4) + rnd(i + 6)) % 1; q.attr("cx", 300 + rnd(i + 10) * 400).attr("cy", 820 - u * (820 - top + 60)).attr("opacity", curd ? 0 : (ea > 0.1 ? 0.8 * ea : 0)); });
      prot.forEach((q, i) => { const gx = 500 + (rnd(i) - 0.5) * 120, gy = 700 + (rnd(i + 3) - 0.5) * 80; q.attr("cx", lerp(300 + rnd(i + 8) * 400, gx, E.out(se)) + Math.sin(lt + i) * 6).attr("cy", lerp(600 + rnd(i + 5) * 220, gy, E.out(se))).attr("opacity", curd ? 0.4 + 0.5 * ea : 0); }); };
  };

  // ---- pressure cooker: trapped steam raises pressure and temperature; the valve whistles ----   at: heat, steam, pressure, whistle
  MODES.cooker = (s, k, a) => {
    const bd = s.append("g").attr("filter", k.sh); bd.append("rect").attr("x", 280).attr("y", 520).attr("width", 440).attr("height", 340).attr("rx", 30).attr("fill", "#aab3ba").attr("stroke", "#5e6b78").attr("stroke-width", 10); bd.append("path").attr("d", "M 260 520 L 740 520 L 700 440 Q 500 400 300 440 Z").attr("fill", "#8d99a6").attr("stroke", "#5e6b78").attr("stroke-width", 10); bd.append("rect").attr("x", 470).attr("y", 380).attr("width", 60).attr("height", 70).attr("rx", 10).attr("fill", "#2a2f35"); bd.append("rect").attr("x", 740).attr("y", 470).attr("width", 80).attr("height", 24).attr("rx", 10).attr("fill", "#2a2f35");
    const water = s.append("rect").attr("x", 296).attr("y", 760).attr("width", 408).attr("height", 90).attr("rx", 16).attr("fill", "#4fb8e8").attr("opacity", 0.85), flame = [330, 420, 500, 580, 670].map((x) => s.append("path").attr("d", `M ${x} 920 Q ${x + 24} 860 ${x} 800 Q ${x - 24} 860 ${x} 920 Z`).attr("fill", "#ff9a2e").attr("opacity", 0)), steam = dots(s, 40, "#fff", 12, 2), ar = [340, 440, 560, 660].map((x) => s.append("path").attr("fill", "none").attr("stroke", "#c8442f").attr("stroke-width", 10).attr("stroke-linecap", "round").attr("opacity", 0).datum(x)), puffs = Array.from({ length: 5 }, (_, i) => s.append("circle").attr("fill", "#fff").attr("opacity", 0).datum(i)), temp = s.append("text").attr("x", 500).attr("y", 660).attr("text-anchor", "middle").attr("font-size", 64).attr("font-weight", 800).attr("fill", "#2a1a10").attr("opacity", 0);
    return (lt, f, d, S) => { const he = S("heat", 0.05), st = S("steam", 0.1), pr = S("pressure", 0.2), wh = S("whistle", 0.04);
      flame.forEach((q, i) => q.attr("opacity", he).attr("transform", `scale(1,${0.85 + 0.2 * Math.sin(lt * 9 + i)})`)); steam.forEach((q, i) => { const u = (lt * 0.5 + rnd(i)) % 1; q.attr("cx", 320 + rnd(i + 4) * 360).attr("cy", 750 - u * 190).attr("opacity", st * (1 - u) * 0.8); });
      ar.forEach((q) => q.attr("d", `M ${q.datum()} 600 L ${q.datum() + (q.datum() < 500 ? -38 : 38)} ${570 - 18 * Math.sin(lt * 7) * pr}`).attr("opacity", pr));
      puffs.forEach((q) => { const i = q.datum(), u = (lt * 1.2 + i / 5) % 1; q.attr("cx", 500 + Math.sin(i * 2) * 20).attr("cy", 370 - u * 160).attr("r", 12 + u * 34).attr("opacity", wh * (1 - u) * 0.9); });
      temp.attr("opacity", pr).text(`≈ ${Math.round(100 + 21 * pr)} °C`); };
  };

  // ---- an onion cut open: enzymes meet the released chemicals and a vapour drifts to the eye ----   at: cut, enzyme, vapor, tears
  MODES.onion = (s, k, a) => {
    const on = s.append("g").attr("transform", "translate(420,640)").attr("filter", k.sh); on.append("circle").attr("r", 190).attr("fill", "#f3dcec").attr("stroke", "#a05a8a").attr("stroke-width", 10); for (const r of [150, 110, 70, 30]) on.append("circle").attr("r", r).attr("fill", "none").attr("stroke", "#c98ab0").attr("stroke-width", 6);
    const knife = s.append("g").attr("transform", "translate(420,200)").attr("opacity", 0); knife.append("path").attr("d", "M -20 0 L 20 0 L 20 200 L -20 240 Z").attr("fill", "#d9dfe4").attr("stroke", "#5e6b78").attr("stroke-width", 5); knife.append("rect").attr("x", -22).attr("y", -110).attr("width", 44).attr("height", 110).attr("rx", 10).attr("fill", "#5a3a22");
    const enz = dots(s, 16, "#2d6fa0", 10, 1).map((q, i) => q.attr("cx", 320 + rnd(i + 3) * 200).attr("cy", 560 + rnd(i) * 160)), vap = dots(s, 26, "#e9b6d6", 10, 3), eye = s.append("g").attr("transform", "translate(880,420)"); eye.append("ellipse").attr("rx", 80).attr("ry", 50).attr("fill", "#fff").attr("stroke", "#4a2a17").attr("stroke-width", 7); eye.append("circle").attr("cx", -12).attr("r", 24).attr("fill", "#4a2a17"); const tears = dots(s, 8, "#4fb8e8", 10, 6);
    return (lt, f, d, S) => { const cu = S("cut", 0.05), en = S("enzyme", 0.1), va = S("vapor", 0.12), te = S("tears", 0.08);
      knife.attr("opacity", cu * (1 - en)).attr("transform", `translate(420,${lerp(120, 450, E.out(cu))})`); enz.forEach((q, i) => q.attr("opacity", en * 0.9).attr("cx", 320 + rnd(i + 3) * 200 + Math.sin(lt * 2 + i) * 12));
      vap.forEach((q, i) => { const u = clamp((lt * 0.3 + rnd(i)) % 1); q.attr("cx", lerp(420 + (rnd(i + 3) - 0.5) * 120, 880 - rnd(i) * 40, u)).attr("cy", lerp(560, 420 + (rnd(i + 5) - 0.5) * 60, u) - Math.sin(u * 3.14) * 60).attr("opacity", va * (1 - u * 0.2) * 0.85); });
      tears.forEach((q, i) => { const u = (lt * 0.5 + rnd(i)) % 1; q.attr("cx", 840 + (i % 4) * 22).attr("cy", 470 + u * 160).attr("opacity", te * (1 - u)); }); };
  };

  // ---- molecules of coconut oil: free and wiggling when warm, locked in a lattice when cold ----   at: cool, warm
  MODES.oilsolid = (s, k, a) => {
    s.append("rect").attr("x", 250).attr("y", 380).attr("width", 500).attr("height", 480).attr("rx", 30).attr("fill", "#fff6d8").attr("stroke", "#c9a77a").attr("stroke-width", 10).attr("filter", k.sh);
    const mol = Array.from({ length: 30 }, (_, i) => s.append("g").datum(i)), cols = ["#e8a33d", "#c8802f"]; mol.forEach((g2, i) => { g2.append("ellipse").attr("rx", 24).attr("ry", 12).attr("fill", cols[i % 2]).attr("stroke", "#7b4a2b").attr("stroke-width", 3); });
    const th = M.chayaIcon(s, "thermo", 860, 620, 200), ice = s.append("text").attr("x", 500).attr("y", 330).attr("text-anchor", "middle").attr("font-size", 70).attr("font-weight", 800).attr("fill", "#2d6fa0").attr("opacity", 0);
    return (lt, f, d, S) => { const co = S("cool", 0.18), wa = S("warm", 0.15), ord = co * (1 - wa);
      mol.forEach((g2) => { const i = g2.datum(), gx = 300 + (i % 6) * 80, gy = 450 + Math.floor(i / 6) * 76, rx = 300 + rnd(i) * 400 + Math.sin(lt * 3 + i) * 50, ry = 430 + rnd(i + 4) * 400 + Math.cos(lt * 2.4 + i * 1.3) * 50;
        g2.attr("transform", `translate(${lerp(rx, gx + Math.sin(lt * 8 + i) * 3, ord)},${lerp(ry, gy + Math.cos(lt * 8 + i) * 3, ord)}) rotate(${lerp(Math.sin(lt + i) * 80, 0, ord)})`); });
      th.attr("transform", `translate(860,620) scale(${1.9})`); ice.attr("opacity", ord).text("❄ ≈ 24 °C ↓"); };
  };

  // ---- the Moon's pull: ocean bulges toward and away from it; a backwater's level rises and falls twice a day ----   at: pull, rise, bund
  MODES.tide = (s, k, a) => {
    s.append("circle").attr("cx", 300).attr("cy", 560).attr("r", 300).attr("fill", k.rg("bulge", [[0.6, "#4fb8e8", 0.8], [1, "#4fb8e8", 0]]));
    const bulge = s.append("ellipse").attr("cx", 300).attr("cy", 560).attr("fill", "#2a8fc0").attr("opacity", 0.85); s.append("circle").attr("cx", 300).attr("cy", 560).attr("r", 190).attr("fill", k.lg("earth", [[0, "#6a9a4a"], [1, "#3f6a2a"]]));
    s.append("circle").attr("cx", 960).attr("cy", 380).attr("r", 70).attr("fill", "#e4e1d8"); const pulls = [0, 1, 2].map((i) => s.append("path").attr("fill", "none").attr("stroke", "#ffd23f").attr("stroke-width", 8).attr("stroke-linecap", "round").attr("opacity", 0).datum(i));
    const gauge = s.append("g").attr("transform", "translate(1250,420)").attr("opacity", 0); gauge.append("rect").attr("x", -34).attr("width", 68).attr("height", 420).attr("rx", 10).attr("fill", "#e8f4fa").attr("stroke", "#4a5560").attr("stroke-width", 6); const lvl = gauge.append("rect").attr("x", -28).attr("width", 56).attr("fill", "#2a8fc0"); gauge.append("text").attr("y", -20).attr("text-anchor", "middle").attr("font-size", 36).attr("font-weight", 800).attr("fill", "#fff6e2").text("കായൽ");
    const bundG = s.append("g").attr("opacity", 0).attr("transform", "translate(1600,560)"); bundG.append("rect").attr("x", -20).attr("y", -150).attr("width", 40).attr("height", 300).attr("fill", "#5d6168"); bundG.append("rect").attr("x", -120).attr("y", -130).attr("width", 100).attr("height", 260).attr("fill", "#4fb8e8").attr("opacity", 0.8); bundG.append("rect").attr("x", 20).attr("y", -130).attr("width", 120).attr("height", 260).attr("fill", "#8fd05a").attr("opacity", 0.6);
    return (lt, f, d, S) => { const pu = S("pull", 0.1), ri = S("rise", 0.1), bu = S("bund", 0.1), rot = lt * 0.3;
      bulge.attr("rx", 190 + 80 * pu).attr("ry", 190 + 24 * pu).attr("transform", `rotate(${(Math.atan2(380 - 560, 960 - 300) * 180) / Math.PI} 300 560)`);
      pulls.forEach((q) => { const i = q.datum(), u = (lt * 0.5 + i / 3) % 1; q.attr("d", `M ${560 + u * 200} ${480 - i * 22} q 40 -30 80 -20`).attr("opacity", pu * (1 - u)); });
      gauge.attr("opacity", ri); const h = 160 + 110 * Math.sin(lt * 1.2); lvl.attr("y", 420 - h).attr("height", h); bundG.attr("opacity", bu); };
  };

  // ---- a mud bank: waves crash outside, the muddy water in the middle damps them and the sea stays calm for boats ----   at: waves, mud, boats
  MODES.mudbank = (s, k, a) => {
    s.append("rect").attr("x", -1400).attr("y", 540).attr("width", 3800).attr("height", 600).attr("fill", k.lg("sea", [[0, "#2a8fc0"], [1, "#146a95"]])); const mud = s.append("rect").attr("x", 360).attr("y", 600).attr("width", 380).attr("height", 400).attr("fill", "#8a6a45").attr("opacity", 0);
    const surf = s.append("path").attr("fill", "none").attr("stroke", "#e9f8ff").attr("stroke-width", 7), boats = [500, 640].map((x) => { const b = s.append("g").attr("opacity", 0); b.append("path").attr("d", "M -50 0 L 50 0 L 36 30 L -36 30 Z").attr("fill", "#c8442f").attr("stroke", "#4a2a17").attr("stroke-width", 4); b.append("rect").attr("x", -3).attr("y", -60).attr("width", 6).attr("height", 60).attr("fill", "#4a2a17"); return [b, x]; });
    return (lt, f, d, S) => { const wv = S("waves", 0.05), mu = S("mud", 0.1), bo = S("boats", 0.05);
      const y = (x) => { const damp = mu * Math.exp(-Math.pow((x - 550) / 140, 2)); return 540 - (50 * wv + 4) * (1 - 0.88 * damp) * Math.sin(x * 0.03 - lt * 3.2); };
      const pts = Array.from({ length: 111 }, (_, i) => [-300 + i * 18, y(-300 + i * 18)]); surf.attr("d", "M " + pts.map((q) => q.join(" ")).join(" L ")); mud.attr("opacity", mu * 0.55);
      boats.forEach(([b, x]) => b.attr("opacity", bo).attr("transform", `translate(${x},${y(x) - 20})`)); };
  };

  // ---- a fan: sweat evaporates faster in moving air and carries heat off the skin; the room itself does not cool ----   at: sweat, evap, fan, room
  MODES.sweat = (s, k, a) => {
    s.append("path").attr("d", "M 200 700 Q 500 660 800 700 L 800 900 L 200 900 Z").attr("fill", "#d9a77a").attr("stroke", "#a8774a").attr("stroke-width", 8);
    const dr = Array.from({ length: 8 }, (_, i) => s.append("path").attr("d", "M 0 -22 Q 14 2 11 10 Q 8 20 0 20 Q -8 20 -11 10 Q -14 2 0 -22 Z").attr("fill", "#4fb8e8").attr("opacity", 0).datum(i)), mols = dots(s, 30, "#9fd8f5", 8, 2), heat = Array.from({ length: 5 }, (_, i) => s.append("path").attr("fill", "none").attr("stroke", "#ff7a3c").attr("stroke-width", 8).attr("stroke-linecap", "round").attr("opacity", 0).datum(i));
    const fan = M.chayaIcon(s, "fan", 130, 450, 200).attr("opacity", 0), wind = Array.from({ length: 5 }, (_, i) => s.append("path").attr("fill", "none").attr("stroke", "#7fb8e8").attr("stroke-width", 7).attr("stroke-linecap", "round").attr("opacity", 0).datum(i)), th = M.chayaIcon(s, "thermo", 880, 480, 150).attr("opacity", 0), eq = s.append("text").attr("x", 880).attr("y", 600).attr("text-anchor", "middle").attr("font-size", 60).attr("font-weight", 800).attr("fill", "#2a1a10").attr("opacity", 0).text("=");
    return (lt, f, d, S) => { const sw = S("sweat", 0.05), ev = S("evap", 0.1), fa = S("fan", 0.05), ro = S("room", 0.05), sp = lerp(0.35, 1.1, fa);
      dr.forEach((q) => { const i = q.datum(); q.attr("transform", `translate(${260 + i * 68},${690 + Math.sin(i * 2) * 6})`).attr("opacity", sw * (1 - ev * 0.5)); });
      mols.forEach((q, i) => { const u = (lt * sp * 0.6 + rnd(i)) % 1; q.attr("cx", 250 + rnd(i + 3) * 500 + u * 60 * fa).attr("cy", 680 - u * 330).attr("opacity", ev * (1 - u)); });
      heat.forEach((q, i) => { const u = (lt * sp * 0.5 + i / 5) % 1; q.attr("d", `M ${300 + i * 100} ${620 - u * 200} q 14 -20 0 -40`).attr("opacity", ev * (1 - u) * 0.9); });
      fan.attr("opacity", fa).attr("transform", "translate(130,450) scale(2)"); wind.forEach((q, i) => { const u = (lt * 1.2 + i / 5) % 1; q.attr("d", `M ${230 + u * 300} ${400 + i * 60} l 80 0`).attr("opacity", fa * (1 - u) * 0.9); });
      th.attr("opacity", ro).attr("transform", "translate(880,480) scale(1.5)"); eq.attr("opacity", ro); };
  };

  // ---- a snake boat: a long hull, many paddlers pulling at the same instant ----   at: long, rhythm, push
  MODES.snakeboat = (s, k, a) => {
    s.append("rect").attr("x", -1400).attr("y", 600).attr("width", 3800).attr("height", 700).attr("fill", k.lg("w", [[0, "#2a8fc0"], [1, "#146a95"]]));
    const boat = s.append("g").attr("filter", k.sh); boat.append("path").attr("d", "M -560 570 L 560 590 Q 640 540 700 440 Q 650 600 560 640 L -520 640 Q -620 620 -640 560 Z").attr("fill", "#2a2f35").attr("stroke", "#f6b945").attr("stroke-width", 6); boat.append("rect").attr("x", -540).attr("y", 556).attr("width", 1080).attr("height", 14).attr("fill", "#c8442f");
    const men = Array.from({ length: 12 }, (_, i) => { const x = -440 + i * 82, g2 = boat.append("g").attr("transform", `translate(${x},560)`); g2.append("circle").attr("cy", -76).attr("r", 18).attr("fill", "#c68b5e"); g2.append("rect").attr("x", -16).attr("y", -56).attr("width", 32).attr("height", 50).attr("rx", 8).attr("fill", i % 2 ? "#f3efe6" : "#e23b2e"); const oar = g2.append("line").attr("x1", 0).attr("y1", -36).attr("stroke", "#7b4a2b").attr("stroke-width", 8).attr("stroke-linecap", "round"); return { g2, oar, i }; });
    const dim = s.append("g").attr("opacity", 0); dim.append("line").attr("x1", -560).attr("x2", 640).attr("y1", 700).attr("y2", 700).attr("stroke", "#fff").attr("stroke-width", 6); dim.append("text").attr("x", 40).attr("y", 760).attr("text-anchor", "middle").attr("fill", "#fff").attr("font-weight", 800).attr("font-size", 52).text("100 – 138 അടി");
    const ar = s.append("path").attr("d", "M 700 700 L 560 700 M 590 670 L 560 700 L 590 730").attr("fill", "none").attr("stroke", "#ffd23f").attr("stroke-width", 12).attr("stroke-linecap", "round").attr("opacity", 0), wk = dots(s, 20, "#fff", 8, 3);
    return (lt, f, d, S) => { const lo = S("long", 0.06), rh = S("rhythm", 0.06), pu = S("push", 0.06); dim.attr("opacity", lo);
      men.forEach(({ oar, i }) => { const ph = lt * 4.2 + (rh > 0.5 ? 0 : i * 0.9), sw = Math.sin(ph); oar.attr("x2", 70 + 30 * sw).attr("y2", 90 + 40 * Math.max(0, Math.cos(ph))).attr("transform", `rotate(${-15 * sw} 0 -36)`); });
      ar.attr("opacity", pu); wk.forEach((q, i) => { const u = (lt * 0.8 + rnd(i)) % 1; q.attr("cx", 640 - u * 1200).attr("cy", 650 + rnd(i + 2) * 120).attr("opacity", 0.7 * (1 - u)); }); };
  };

  // ---- what is in tender coconut water: mostly water, a little sugar and minerals, most of all potassium ----   at: water, minerals, potassium
  MODES.coconutwater = (s, k, a) => {
    const nut = M.chayaIcon(s, "coconut", 300, 580, 330), arc = d3.arc().innerRadius(120).outerRadius(220), g2 = s.append("g").attr("transform", "translate(760,580)");
    const parts = [["#4fb8e8", 0.945, "വെള്ളം"], ["#ffd23f", 0.03, "പഞ്ചസാര"], ["#c8442f", 0.025, "ധാതുക്കൾ"]]; let acc = 0; const segs = parts.map(([col, v, ml]) => { const a0 = acc * Math.PI * 2, a1 = (acc + v) * Math.PI * 2; acc += v; return { col, a0, a1, ml, p: g2.append("path").attr("fill", col).attr("opacity", 0) }; });
    const pt = g2.append("text").attr("y", 24).attr("text-anchor", "middle").attr("font-size", 64).attr("font-weight", 800).attr("fill", "#2a1a10").attr("opacity", 0), kk = s.append("g").attr("opacity", 0).attr("transform", "translate(980,340)"); kk.append("circle").attr("r", 62).attr("fill", "#c8442f").attr("stroke", "#fff").attr("stroke-width", 6); kk.append("text").attr("y", 18).attr("text-anchor", "middle").attr("font-size", 56).attr("font-weight", 800).attr("fill", "#fff").text("K⁺");
    return (lt, f, d, S) => { const wa = S("water", 0.1), mi = S("minerals", 0.1), po = S("potassium", 0.08);
      segs.forEach((sg, i) => { const g = i === 0 ? wa : mi; sg.p.attr("d", arc({ startAngle: sg.a0, endAngle: sg.a0 + (sg.a1 - sg.a0) * (i === 0 ? wa : 1) })).attr("opacity", g > 0 ? 1 : 0); }); pt.attr("opacity", wa).text("94–95 % വെള്ളം".slice(0, 0) + "94%"); kk.attr("opacity", po).attr("transform", `translate(980,${340 + 6 * Math.sin(lt * 3)}) scale(${1 + 0.1 * po * Math.sin(lt * 4)})`); };
  };

  // ---- an elephant's call: low sound in the air, and a tremor through the ground to a listening elephant's feet ----   at: call, ground, feet, far
  MODES.seismic = (s, k, a) => {
    s.append("rect").attr("x", -1400).attr("y", 640).attr("width", 3800).attr("height", 700).attr("fill", k.lg("g", [[0, "#9a6f45"], [1, "#5a3e24"]])); s.append("rect").attr("x", -1400).attr("y", 628).attr("width", 3800).attr("height", 20).attr("fill", "#6aa04a");
    const e1 = M.chayaIcon(s, "elephant", 160, 560, 280), e2 = M.chayaIcon(s, "elephant", 860, 560, 280).attr("transform", "translate(860,560) scale(-2.8,2.8)");
    const air = [0, 1, 2].map((i) => s.append("circle").attr("cx", 260).attr("cy", 470).attr("fill", "none").attr("stroke", "#9fd8f5").attr("stroke-width", 6).attr("opacity", 0).datum(i)), gnd = [0, 1, 2, 3].map((i) => s.append("path").attr("fill", "none").attr("stroke", "#ffd23f").attr("stroke-width", 7).attr("stroke-linecap", "round").attr("opacity", 0).datum(i)), feet = s.append("circle").attr("cx", 820).attr("cy", 660).attr("r", 40).attr("fill", "none").attr("stroke", "#c8442f").attr("stroke-width", 8).attr("opacity", 0), dist = s.append("g").attr("opacity", 0); dist.append("line").attr("x1", 160).attr("x2", 860).attr("y1", 900).attr("y2", 900).attr("stroke", "#fff6e2").attr("stroke-width", 6); dist.append("text").attr("x", 510).attr("y", 960).attr("text-anchor", "middle").attr("font-size", 52).attr("font-weight", 800).attr("fill", "#fff6e2").text("≈ 2 km വരെ?");
    return (lt, f, d, S) => { const ca = S("call", 0.05), gr = S("ground", 0.06), fe = S("feet", 0.05), fa = S("far", 0.06);
      e1.attr("transform", `translate(160,560) scale(2.8)`); e2.attr("transform", "translate(860,560) scale(-2.8,2.8)");
      air.forEach((q) => { const i = q.datum(), u = (lt * 0.4 + i / 3) % 1; q.attr("r", 40 + u * 500).attr("opacity", ca * (1 - u) * 0.8); });
      gnd.forEach((q) => { const i = q.datum(), u = (lt * 0.6 + i / 4) % 1, x = 220 + u * 620; q.attr("d", `M ${x} ${680 + i * 40} q 14 -22 28 0 t 28 0`).attr("opacity", gr * (1 - Math.abs(u - 0.5) * 1.2)); });
      feet.attr("opacity", fe * (0.5 + 0.5 * Math.sin(lt * 6))).attr("r", 40 + 20 * Math.sin(lt * 6)); dist.attr("opacity", fa); };
  };

  // ================= the scene: background + a mode + tags =================
  K.lab = (g, p, c) => {
    const id = c.id + rid(), k = M.setKit(g, c, id), s = k.set, a = p.at || {};
    BG(s, k, p.bg || (p.mode === "firefly" ? "night" : p.mode === "petrichor" ? "sky" : "kitchen"));
    const mode = (MODES[p.mode] || (() => () => {}))(s, k, a, p), tags = (p.tags || []).map((t) => ({ t, pg: k.pill2(t.x, t.y, t.ml, t.en, t.col || "#c8442f") }));
    const DEF = { sunshadow: [500, 440, 1.1], tealeaf: [500, 560, 1.5], adenosine: [500, 560, 1.5], steep: [500, 650, 1.8], ferment: [500, 650, 1.8], cooker: [500, 640, 1.7], onion: [620, 600, 1.4], oilsolid: [550, 540, 1.5], tide: [800, 560, 1.0], mudbank: [550, 560, 1.4], sweat: [500, 580, 1.5], snakeboat: [40, 540, 1.1], coconutwater: [620, 570, 1.5], seismic: [510, 640, 1.4], petrichor: [500, 560, 1.5], firefly: [700, 600, 1.35], goli: [500, 560, 1.9], cassette: [520, 640, 1.5], osmosis: [450, 640, 1.7], lamp: [500, 500, 1.9] }[p.mode] || [500, 540, 1.2], tall = c.stage.h > c.stage.w;
    const move = k.camMover(p.cams || [{ at: 0, x: DEF[0], y: DEF[1], z: DEF[2] * (tall ? 0.8 : 1) }]);
    return (lt, d) => { const f = lt / d; move(f, d); mode(lt, f, d, (name, w = 0.1) => prog(f, at(a, name), w));
      tags.forEach(({ t, pg }, i) => { pop(pg, t.x, t.y, f, d, t.at ?? 9); const nxt = tags[i + 1] ? tags[i + 1].t.at : 9; pg.attr("opacity", +pg.attr("opacity") * (1 - prog(f, Math.min((t.at ?? 9) + 0.2, nxt + 0.02), 0.03))); }); };
  };
})();
