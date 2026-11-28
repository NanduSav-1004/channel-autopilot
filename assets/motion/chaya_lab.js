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

  // ---- sea breeze: land heats faster than sea, warm air rises over land and cool sea air flows in; the pattern reverses at night ----   at: heat, rise, flow, night
  MODES.seabreeze = (s, k, a) => {
    s.append("rect").attr("x", -400).attr("y", 600).attr("width", 1400).attr("height", 400).attr("fill", k.lg("sea", [[0, "#2a8fc0"], [1, "#146a95"]])); s.append("rect").attr("x", 500).attr("y", 600).attr("width", 1000).attr("height", 400).attr("fill", k.lg("land", [[0, "#8fb24a"], [1, "#5d7a2a"]]));
    s.append("path").attr("d", "M 480 600 L 500 600 L 500 640 Z").attr("fill", "#e6cf98"); const sun = M.chayaIcon(s, "sun", 900, 200, 200), moon = s.append("circle").attr("cx", 900).attr("cy", 200).attr("r", 70).attr("fill", "#e4e1d8").attr("opacity", 0), tr = M.chayaIcon(s, "tree", 800, 560, 130), bt = M.chayaIcon(s, "boat", 200, 560, 150);
    const warm = Array.from({ length: 6 }, (_, i) => s.append("path").attr("fill", "none").attr("stroke", "#ff7a3c").attr("stroke-width", 9).attr("stroke-linecap", "round").attr("opacity", 0).datum(i)), arrows = Array.from({ length: 7 }, (_, i) => s.append("path").attr("fill", "none").attr("stroke", "#4aa8e8").attr("stroke-width", 10).attr("stroke-linecap", "round").attr("opacity", 0).datum(i));
    return (lt, f, d, S) => { const he = S("heat", 0.05), ri = S("rise", 0.06), fl = S("flow", 0.06), ni = S("night", 0.08);
      sun.attr("opacity", 1 - ni).attr("transform", "translate(900,200) scale(2)"); moon.attr("opacity", ni);
      warm.forEach((q, i) => { const u = (lt * 0.5 + i / 6) % 1, x = 620 + i * 60; q.attr("d", `M ${x} ${580 - u * 330} q 14 -20 0 -40 t 0 -40`).attr("opacity", ri * (1 - ni) * (1 - u) + ni * ri * 0.0); });
      arrows.forEach((q, i) => { const u = (lt * 0.4 + i / 7) % 1, dir = ni > 0.5 ? 1 : -1, x0 = ni > 0.5 ? 760 : 240; q.attr("d", `M ${x0 + dir * u * 300 * (ni > 0.5 ? -1 : 1) * -1} ${560 - (i % 3) * 36} l ${(ni > 0.5 ? 1 : -1) * 60} 0`).attr("opacity", fl * (1 - Math.abs(u - 0.5) * 2)); }); };
  };

  // ---- humid air: the air is already full of water vapour, so sweat has nowhere to go ----   at: humid, sweat, stuck
  MODES.humid = (s, k, a) => {
    s.append("path").attr("d", "M 200 720 Q 500 680 800 720 L 800 900 L 200 900 Z").attr("fill", "#d9a77a").attr("stroke", "#a8774a").attr("stroke-width", 8);
    const vap = dots(s, 70, "#9fd8f5", 9, 2), dr = Array.from({ length: 8 }, (_, i) => s.append("circle").attr("r", 15).attr("fill", "#4fb8e8").attr("opacity", 0).datum(i)), x = s.append("text").attr("x", 500).attr("y", 600).attr("text-anchor", "middle").attr("font-size", 120).attr("font-weight", 800).attr("fill", "#c8442f").attr("opacity", 0).text("✕");
    return (lt, f, d, S) => { const hu = S("humid", 0.1), sw = S("sweat", 0.05), st = S("stuck", 0.05);
      vap.forEach((q, i) => q.attr("cx", 120 + rnd(i) * 760 + Math.sin(lt * 1.2 + i) * 24).attr("cy", 260 + rnd(i + 3) * 400 + Math.cos(lt + i) * 20).attr("opacity", hu * 0.9));
      dr.forEach((q) => { const i = q.datum(); q.attr("cx", 260 + i * 68).attr("cy", 706 + Math.sin(i * 2) * 6).attr("opacity", sw); }); x.attr("opacity", st * (0.6 + 0.4 * Math.sin(lt * 4))); };
  };

  // ---- hail: updrafts carry drops up into freezing air; layers of ice build until it is too heavy ----   at: updraft, rise, layers, fall
  MODES.hail = (s, k, a) => {
    M.chayaIcon(s, "cloudDark", 500, 230, 700); const ups = [260, 420, 580, 740].map((x) => s.append("path").attr("fill", "none").attr("stroke", "#ff9a3c").attr("stroke-width", 12).attr("stroke-linecap", "round").attr("opacity", 0).datum(x));
    const stone = s.append("g"), layers = [60, 48, 36, 24, 12].map((r, i) => stone.append("circle").attr("r", r).attr("fill", i % 2 ? "#e8f6ff" : "#bfe3f6").attr("stroke", "#7fb8e8").attr("stroke-width", 3));
    const frost = s.append("text").attr("x", 860).attr("y", 330).attr("font-size", 80).attr("fill", "#7fd0f8").attr("opacity", 0).text("❄");
    return (lt, f, d, S) => { const up = S("updraft", 0.05), ri = S("rise", 0.15), la = S("layers", 0.2), fa = S("fall", 0.1);
      ups.forEach((q) => { const x = q.datum(), u = (lt * 0.6) % 1; q.attr("d", `M ${x} ${860 - u * 30} L ${x} ${520 - u * 30}`).attr("opacity", up * 0.8); });
      const y = lerp(820, 420, E.out(ri)) + fa * 520 * fa; stone.attr("transform", `translate(${440 + 60 * Math.sin(lt * 1.2) * (1 - fa)},${y}) scale(${0.5 + 0.9 * la})`); layers.forEach((q, i) => q.attr("opacity", i === 0 ? 1 : clamp(la * 6 - (4 - i) * 0.9 + 0.3))); frost.attr("opacity", ri * (1 - fa)); };
  };

  // ---- cloud weight: a cloud holds hundreds of tonnes of water as tiny drops, about eighty elephants ----   at: cloud, weight, elephants, float
  MODES.cloudweight = (s, k, a) => {
    const c = M.chayaIcon(s, "cloud", 500, 280, 520), drops = dots(s, 60, "#4fb8e8", 6, 3), els = Array.from({ length: 8 }, (_, i) => M.chayaIcon(s, "elephant", 150 + i * 100, 780, 110).attr("opacity", 0)), n = s.append("text").attr("x", 500).attr("y", 960).attr("text-anchor", "middle").attr("font-size", 70).attr("font-weight", 800).attr("fill", "#2a1a10").attr("opacity", 0).text("× 80 ആനകൾ");
    return (lt, f, d, S) => { const cl = S("cloud", 0.05), we = S("weight", 0.1), el = S("elephants", 0.2), fl = S("float", 0.08);
      c.attr("opacity", 1).attr("transform", `translate(500,${280 + 8 * Math.sin(lt * 1.2)}) scale(5.2)`); drops.forEach((q, i) => q.attr("cx", 250 + rnd(i) * 500 + Math.sin(lt + i) * 10).attr("cy", 200 + rnd(i + 3) * 160 + Math.cos(lt * 0.8 + i) * 8).attr("opacity", cl * (1 - fl * 0.2) * 0.9));
      els.forEach((e, i) => e.attr("opacity", clamp(el * 10 - i) * we).attr("transform", `translate(${150 + i * 100},780) scale(1.1)`)); n.attr("opacity", el); };
  };

  // ---- a falling raindrop: gravity pulls down, air drag grows until the two balance ----   at: fall, drag, balance
  MODES.raindropspeed = (s, k, a) => {
    s.append("rect").attr("x", -1400).attr("y", -400).attr("width", 3800).attr("height", 1400).attr("fill", k.lg("sky", [[0, "#7e8d9a"], [1, "#d9e3e8"]]));
    const dr = s.append("path").attr("d", "M 0 -52 Q 34 8 28 24 Q 22 52 0 52 Q -22 52 -28 24 Q -34 8 0 -52 Z").attr("fill", "#2a8fd0").attr("stroke", "#fff").attr("stroke-width", 4), g2 = arrowK(s, "#c8442f"), dg = arrowK(s, "#2f7d4f"), sp = s.append("text").attr("x", 760).attr("y", 330).attr("font-size", 80).attr("font-weight", 800).attr("fill", "#2a1a10").attr("opacity", 0), eq = s.append("text").attr("x", 500).attr("y", 840).attr("text-anchor", "middle").attr("font-size", 60).attr("font-weight", 800).attr("fill", "#2a1a10").attr("opacity", 0).text("ഗുരുത്വം = വായു തടസ്സം");
    return (lt, f, d, S) => { const fa = S("fall", 0.12), da = S("drag", 0.15), ba = S("balance", 0.1), v = 32 * E.out(da);
      const y = 150 + 520 * ((lt * 0.45) % 1); dr.attr("transform", `translate(500,${y})`).attr("opacity", fa); const gd = 90, dd = 90 * da * (0.2 + 0.8 * da);
      g2(500, y + 54, 500, y + 54 + gd, fa); dg(500, y - 54, 500, y - 54 - dd, da); sp.attr("opacity", da).text(Math.round(v) + " km/h"); eq.attr("opacity", ba); };
    function arrowK(g, col) { const p2 = g.append("path").attr("fill", "none").attr("stroke", col).attr("stroke-width", 12).attr("stroke-linecap", "round"), h = g.append("path").attr("fill", col); return (x0, y0, x1, y1, op) => { const L = Math.hypot(x1 - x0, y1 - y0) || 1, ux = (x1 - x0) / L, uy = (y1 - y0) / L; p2.attr("d", `M ${x0} ${y0} L ${x1} ${y1}`).attr("opacity", op); h.attr("d", `M ${x1 + ux * 22} ${y1 + uy * 22} L ${x1 - uy * 16} ${y1 + ux * 16} L ${x1 + uy * 16} ${y1 - ux * 16} Z`).attr("opacity", op); }; }
  };

  // ---- the blue sky: sunlight meets air molecules; blue scatters everywhere, red goes on; at sunset the path is longer ----   at: ray, scatter, sunset
  MODES.bluesky = (s, k, a) => {
    s.append("rect").attr("x", -1400).attr("y", -400).attr("width", 3800).attr("height", 1000).attr("fill", k.lg("sky", [[0, "#2a6fb8"], [1, "#9fd0f0"]])); s.append("rect").attr("x", -1400).attr("y", 760).attr("width", 3800).attr("height", 500).attr("fill", "#5d7a2a");
    const sun = M.chayaIcon(s, "sun", 140, 180, 220), ray = s.append("line").attr("stroke", "#fff6c8").attr("stroke-width", 14).attr("stroke-linecap", "round").attr("opacity", 0), mol = dots(s, 40, "#fff", 8, 2), blues = dots(s, 40, "#3a6fe8", 9, 5), reds = Array.from({ length: 6 }, (_, i) => s.append("circle").attr("r", 10).attr("fill", "#e23b2e").attr("opacity", 0).datum(i));
    const eye = M.chayaIcon(s, "person", 820, 700, 150);
    return (lt, f, d, S) => { const ra = S("ray", 0.05), sc = S("scatter", 0.1), ss = S("sunset", 0.12);
      sun.attr("transform", `translate(${lerp(140, 230, ss)},${lerp(180, 640, ss)}) scale(2.2)`); ray.attr("x1", lerp(200, 280, ss)).attr("y1", lerp(220, 640, ss)).attr("x2", 780).attr("y2", 680).attr("opacity", ra);
      mol.forEach((q, i) => q.attr("cx", 280 + rnd(i) * 500).attr("cy", lerp(220 + rnd(i + 3) * 400, 600 + rnd(i + 3) * 120, ss) + Math.sin(lt + i) * 6).attr("opacity", ra * 0.6));
      blues.forEach((q, i) => { const u = (lt * 0.7 + rnd(i)) % 1, an = rnd(i + 8) * Math.PI * 2, cx = 280 + rnd(i) * 500, cy = lerp(220 + rnd(i + 3) * 400, 600 + rnd(i + 3) * 120, ss); q.attr("cx", cx + Math.cos(an) * u * 150).attr("cy", cy + Math.sin(an) * u * 150).attr("opacity", sc * (1 - ss * 0.8) * (1 - u)); });
      reds.forEach((q) => { const i = q.datum(), u = (lt * 0.5 + i / 6) % 1; q.attr("cx", lerp(280, 780, u)).attr("cy", lerp(lerp(220, 640, ss), 680, u)).attr("opacity", sc * (0.5 + ss * 0.5) * 0.9); }); eye.attr("transform", "translate(820,700) scale(1.5)"); };
  };

  // ---- twinkling: starlight bends as it crosses shifting layers of air; a planet is a small disc so it averages out ----   at: ray, bend, planet
  MODES.twinkle = (s, k, a) => {
    for (let i = 0; i < 20; i++) s.append("circle").attr("cx", -300 + rnd(i) * 1600).attr("cy", rnd(i + 5) * 500).attr("r", 2).attr("fill", "#fff").attr("opacity", 0.6);
    const air = [380, 520, 660].map((y, i) => s.append("path").attr("fill", "#8fb8e8").attr("opacity", 0.18 + i * 0.08).datum(y)), star = s.append("text").attr("x", 500).attr("y", 130).attr("text-anchor", "middle").attr("font-size", 120).attr("fill", "#ffe9a8").text("★"), planet = s.append("circle").attr("cx", 820).attr("cy", 110).attr("r", 34).attr("fill", "#e8a33d").attr("opacity", 0), ray = s.append("path").attr("fill", "none").attr("stroke", "#ffe9a8").attr("stroke-width", 7).attr("opacity", 0), ray2 = s.append("path").attr("fill", "none").attr("stroke", "#e8a33d").attr("stroke-width", 22).attr("opacity", 0);
    const eye = s.append("g").attr("transform", "translate(500,880)"); eye.append("ellipse").attr("rx", 70).attr("ry", 44).attr("fill", "#fff"); eye.append("circle").attr("r", 20).attr("fill", "#4a2a17");
    return (lt, f, d, S) => { const ra = S("ray", 0.04), be = S("bend", 0.12), pl = S("planet", 0.06);
      air.forEach((q) => { const y = q.datum(); q.attr("d", `M -400 ${y} Q 200 ${y + 40 * Math.sin(lt * 2 + y)} 500 ${y} T 1400 ${y} L 1400 ${y + 110} L -400 ${y + 110} Z`); });
      const wob = (x0) => `M ${x0} 170 L ${x0 + 12 * be * Math.sin(lt * 7)} 380 L ${500 + 24 * be * Math.sin(lt * 9 + 1)} 520 L ${500 + 14 * be * Math.sin(lt * 11)} 660 L 500 840`; ray.attr("d", wob(500)).attr("opacity", ra); star.attr("opacity", 1).attr("font-size", 120 + 20 * be * Math.sin(lt * 8));
      planet.attr("opacity", pl); ray2.attr("d", `M 820 150 L 640 380 L 540 520 L 510 660 L 500 840`).attr("opacity", pl * 0.6); };
  };

  // ---- the Moon illusion: a horizon Moon beside trees looks big; the same Moon overhead looks small; through a tube they match ----   at: horizon, overhead, tube
  MODES.moonillusion = (s, k, a) => {
    s.append("rect").attr("x", -1400).attr("y", -400).attr("width", 3800).attr("height", 1300).attr("fill", k.lg("sky", [[0, "#17214a"], [1, "#f0a679"]])); s.append("rect").attr("x", -1400).attr("y", 740).attr("width", 3800).attr("height", 500).attr("fill", "#17241a");
    [60, 200, 780, 900].forEach((x, i) => M.chayaIcon(s, "tree", x, 720, 200 + i * 20)); const moonH = s.append("circle").attr("cx", 500).attr("cy", 620).attr("r", 90).attr("fill", "#f3e6b0"), moonO = s.append("circle").attr("cx", 500).attr("cy", 180).attr("r", 90).attr("fill", "#f3e6b0").attr("opacity", 0);
    const ruler = s.append("g").attr("opacity", 0); ruler.append("line").attr("x1", 410).attr("x2", 590).attr("y1", 780).attr("y2", 780).attr("stroke", "#fff").attr("stroke-width", 6); ruler.append("text").attr("x", 500).attr("y", 830).attr("text-anchor", "middle").attr("fill", "#fff").attr("font-size", 44).attr("font-weight", 800).text("ഒരേ വലുപ്പം");
    const tube = s.append("rect").attr("x", 330).attr("y", 80).attr("width", 340).attr("height", 200).attr("rx", 100).attr("fill", "none").attr("stroke", "#fff").attr("stroke-width", 10).attr("opacity", 0);
    return (lt, f, d, S) => { const ho = S("horizon", 0.05), ov = S("overhead", 0.1), tu = S("tube", 0.08);
      moonH.attr("opacity", 1).attr("cy", lerp(620, 620 - 440 * ov * 0, 0)); moonO.attr("opacity", ov); ruler.attr("opacity", ov); tube.attr("opacity", tu); };
  };

  // ---- ring of fire: when the Moon is farther away it looks smaller and cannot cover the whole Sun ----   at: align, near, far, ring
  MODES.ringeclipse = (s, k, a) => {
    s.append("rect").attr("x", -1400).attr("y", -400).attr("width", 3800).attr("height", 1500).attr("fill", "#0a1030");
    s.append("circle").attr("cx", 120).attr("cy", 500).attr("r", 150).attr("fill", "#ffd23f"); s.append("circle").attr("cx", 120).attr("cy", 500).attr("r", 300).attr("fill", k.rg("sg", [[0, "#ffd23f", 0.4], [1, "#ffd23f", 0]]));
    s.append("circle").attr("cx", 880).attr("cy", 500).attr("r", 50).attr("fill", "#3aa0e8"); const moon = s.append("circle").attr("r", 28).attr("fill", "#cfccc2").attr("stroke", "#fff").attr("stroke-width", 3), ln = s.append("path").attr("fill", "rgba(255,226,120,0.18)").attr("stroke", "none"), view = s.append("g").attr("transform", "translate(500,200)").attr("opacity", 0); view.append("circle").attr("r", 110).attr("fill", "#ffd23f"); const disc = view.append("circle").attr("r", 80).attr("fill", "#0a1030").attr("stroke", "#0a1030");
    const lab = s.append("text").attr("x", 500).attr("y", 760).attr("text-anchor", "middle").attr("font-size", 52).attr("font-weight", 800).attr("fill", "#fff6e2").attr("opacity", 0);
    return (lt, f, d, S) => { const al = S("align", 0.08), ne = S("near", 0.05), fa = S("far", 0.1), ri = S("ring", 0.05), x = lerp(500, 760 - 130 * ne * (1 - fa), fa * 0 + 1) * 0 + (ne > 0 && fa === 0 ? 760 : fa > 0 ? 500 : 640);
      moon.attr("cx", al * 0 + (fa > 0 ? 440 : 640)).attr("cy", 500).attr("r", fa > 0 ? 36 : 56).attr("opacity", al); ln.attr("d", `M 120 350 L ${fa > 0 ? 440 : 640} 460 L 880 470 L 880 530 L ${fa > 0 ? 440 : 640} 540 L 120 650 Z`).attr("opacity", al);
      view.attr("opacity", Math.max(ne, fa)); disc.attr("r", fa > 0 ? 82 : 118).attr("fill", "#0a1030"); view.select("circle").attr("r", 110); lab.attr("opacity", Math.max(ne, fa)).text(fa > 0 ? "വലയം (ring)" : "പൂർണ്ണ ഗ്രഹണം"); };
  };

  // ---- the space station: a fast orbit that is really constant falling around the Earth; we see it by reflected sunlight ----   at: orbit, speed, reflect
  MODES.iss = (s, k, a) => {
    s.append("rect").attr("x", -1400).attr("y", -400).attr("width", 3800).attr("height", 1500).attr("fill", "#050b1f"); for (let i = 0; i < 80; i++) s.append("circle").attr("cx", -800 + rnd(i) * 2400).attr("cy", -300 + rnd(i + 4) * 1100).attr("r", 1.6 + rnd(i + 2) * 2).attr("fill", "#fff").attr("opacity", 0.6);
    s.append("circle").attr("cx", 500).attr("cy", 1300).attr("r", 760).attr("fill", k.lg("e", [[0, "#3aa0e8"], [1, "#1a5fa8"]])); s.append("circle").attr("cx", 500).attr("cy", 1300).attr("r", 740).attr("fill", "#4f9a4a").attr("opacity", 0.35);
    const orb = s.append("ellipse").attr("cx", 500).attr("cy", 1300).attr("rx", 880).attr("ry", 880).attr("fill", "none").attr("stroke", "#ffd23f").attr("stroke-width", 4).attr("stroke-dasharray", "12 12").attr("opacity", 0), sat = M.chayaIcon(s, "satellite", 500, 420, 100).attr("opacity", 0), person = M.chayaIcon(s, "person", 140, 560, 120), beam = s.append("path").attr("fill", "rgba(255,246,200,0.25)").attr("opacity", 0), sp = s.append("text").attr("x", 500).attr("y", 120).attr("text-anchor", "middle").attr("font-size", 64).attr("font-weight", 800).attr("fill", "#ffd23f").attr("opacity", 0), sunI = M.chayaIcon(s, "sun", 1250, 120, 160);
    return (lt, f, d, S) => { const or = S("orbit", 0.05), sp2 = S("speed", 0.1), re = S("reflect", 0.1), th = -Math.PI / 2 + (lt * 0.5);
      orb.attr("opacity", or); const x = 500 + 880 * Math.cos(th), y = 1300 + 880 * Math.sin(th); sat.attr("opacity", or).attr("transform", `translate(${x},${y}) scale(1.1)`); sp.attr("opacity", sp2).text("≈ 28,000 km/h");
      beam.attr("d", `M 1200 130 L ${x} ${y} L ${x + 20} ${y + 40} Z`).attr("opacity", re); person.attr("transform", "translate(140,560) scale(1.3)"); sunI.attr("transform", "translate(1250,120) scale(1.6)"); };
  };

  // ---- one face of the Moon: it spins once per orbit, so the same side always faces Earth ----   at: orbit, spin, lock
  MODES.moonface = (s, k, a) => {
    s.append("rect").attr("x", -1400).attr("y", -400).attr("width", 3800).attr("height", 1500).attr("fill", "#050b1f"); for (let i = 0; i < 60; i++) s.append("circle").attr("cx", -600 + rnd(i) * 2200).attr("cy", -300 + rnd(i + 4) * 1100).attr("r", 1.6 + rnd(i + 2) * 2).attr("fill", "#fff").attr("opacity", 0.6);
    s.append("circle").attr("cx", 500).attr("cy", 560).attr("r", 120).attr("fill", k.lg("e", [[0, "#3aa0e8"], [1, "#1a5fa8"]])); s.append("ellipse").attr("cx", 480).attr("cy", 540).attr("rx", 50).attr("ry", 34).attr("fill", "#4f9a4a"); s.append("ellipse").attr("cx", 500).attr("cy", 560).attr("rx", 360).attr("ry", 360).attr("fill", "none").attr("stroke", "#ffd23f").attr("stroke-width", 4).attr("stroke-dasharray", "12 12");
    const moon = s.append("g"); moon.append("circle").attr("r", 60).attr("fill", "#d9d6cc"); moon.append("circle").attr("cx", 14).attr("cy", -10).attr("r", 18).attr("fill", "#9b988e"); moon.append("circle").attr("cx", 26).attr("cy", 20).attr("r", 10).attr("fill", "#9b988e"); const face = moon.append("path").attr("d", "M 0 0 L 90 0").attr("stroke", "#c8442f").attr("stroke-width", 8).attr("stroke-linecap", "round"), lab = s.append("text").attr("x", 500).attr("y", 1010).attr("text-anchor", "middle").attr("font-size", 56).attr("font-weight", 800).attr("fill", "#fff6e2").attr("opacity", 0);
    return (lt, f, d, S) => { const or = S("orbit", 0.05), sp = S("spin", 0.1), lo = S("lock", 0.1), th = lt * 0.6, x = 500 + 360 * Math.cos(th), y = 560 + 360 * Math.sin(th);
      moon.attr("opacity", 1).attr("transform", `translate(${x},${y}) rotate(${(th * 180) / Math.PI + 180 + (lo > 0 ? 0 : (1 - sp) * lt * 80)})`); lab.attr("opacity", lo).text("ഒരു ചുറ്റ് = ഒരു കറക്കം"); };
  };

  // ---- fever: germs, immune signals, the brain's thermostat set higher, shivering, then lowered and sweating ----   at: germ, signal, raise, shiver, hot, lower
  MODES.thermostat = (s, k, a) => {
    const gg = s.append("g").attr("transform", "translate(320,520)"); gg.append("path").attr("d", "M -200 0 A 200 200 0 0 1 200 0").attr("fill", "none").attr("stroke", "#c9a77a").attr("stroke-width", 36).attr("stroke-linecap", "round"); gg.append("path").attr("d", "M 60 -190 A 200 200 0 0 1 200 0").attr("fill", "none").attr("stroke", "#e23b2e").attr("stroke-width", 36).attr("stroke-linecap", "round").attr("opacity", 0.5);
    const needle = gg.append("g"); needle.append("path").attr("d", "M -10 0 L 0 -170 L 10 0 Z").attr("fill", "#2a1a10"); gg.append("circle").attr("r", 20).attr("fill", "#2a1a10"); gg.append("text").attr("y", 80).attr("text-anchor", "middle").attr("font-size", 40).attr("font-weight", 800).attr("fill", "#4a2a17").text("തെർമോസ്റ്റാറ്റ്");
    const body = s.append("g").attr("transform", "translate(760,520)"), person = M.chayaIcon(body, "person", 0, 0, 260), th = M.chayaIcon(s, "thermo", 960, 480, 220), val = s.append("text").attr("x", 760).attr("y", 780).attr("text-anchor", "middle").attr("font-size", 70).attr("font-weight", 800).attr("fill", "#2a1a10");
    const germs = dots(s, 12, "#7a3fb0", 12, 2), sig = dots(s, 8, "#2d6fa0", 9, 5), drops = dots(s, 8, "#4fb8e8", 9, 7);
    return (lt, f, d, S) => { const ge = S("germ", 0.05), si = S("signal", 0.08), ra = S("raise", 0.12), sh = S("shiver", 0.05), ho = S("hot", 0.05), lo = S("lower", 0.12), set = 37 + 2 * ra - 2 * lo, temp = lerp(37, 39, clamp(ra * 1.1 - lo * 1.1));
      needle.attr("transform", `rotate(${lerp(-90, 40, (set - 36) / 4) - 0})`); val.text(temp.toFixed(1) + " °C");
      germs.forEach((q, i) => q.attr("cx", 620 + rnd(i) * 280 + Math.sin(lt * 2 + i) * 20).attr("cy", 300 + rnd(i + 3) * 340 + Math.cos(lt * 1.6 + i) * 20).attr("opacity", ge * (1 - lo * 0.8)));
      sig.forEach((q, i) => { const u = (lt * 0.5 + i / 8) % 1; q.attr("cx", lerp(760, 320, u)).attr("cy", lerp(380, 400, u) - Math.sin(u * Math.PI) * 60).attr("opacity", si * (1 - lo) * 0.9); });
      body.attr("transform", `translate(${760 + sh * (1 - ho) * (1 - lo) * 8 * Math.sin(lt * 40)},520)`); th.attr("transform", "translate(960,480) scale(2.2)");
      drops.forEach((q, i) => { const u = (lt * 0.5 + rnd(i)) % 1; q.attr("cx", 700 + (i % 4) * 40).attr("cy", 320 + u * 120).attr("opacity", (ho * (1 - lo) * 0 + lo) * (1 - u)); }); };
  };

  // ---- hiccups: the diaphragm jerks down and the vocal cords snap shut ----   at: breath, spasm, close
  MODES.hiccup = (s, k, a) => {
    s.append("path").attr("d", "M 300 260 Q 500 200 700 260 L 760 880 L 240 880 Z").attr("fill", "#f3dcc0").attr("stroke", "#c9a77a").attr("stroke-width", 8); const lungs = [380, 620].map((x) => s.append("ellipse").attr("cx", x).attr("cy", 480).attr("rx", 90).attr("ry", 150).attr("fill", "#e89a9a").attr("stroke", "#a85a5a").attr("stroke-width", 6));
    const dia = s.append("path").attr("fill", "#c8442f").attr("stroke", "#7b2a1c").attr("stroke-width", 8), cords = [-1, 1].map((sg) => s.append("path").attr("fill", "#c8442f").datum(sg)), hic = s.append("text").attr("x", 500).attr("y", 190).attr("text-anchor", "middle").attr("font-size", 110).attr("font-weight", 800).attr("fill", "#c8442f").attr("opacity", 0).text("ഹിക്!");
    return (lt, f, d, S) => { const br = S("breath", 0.05), sp = S("spasm", 0.1), cl = S("close", 0.08), pulse = sp * Math.max(0, Math.sin(lt * 5)) ** 6, y = 640 + 40 * Math.sin(lt * 1.4) * (1 - sp) + 90 * pulse;
      dia.attr("d", `M 270 ${y} Q 500 ${y - 90 + 60 * pulse} 730 ${y} L 730 ${y + 30} Q 500 ${y - 50} 270 ${y + 30} Z`); lungs.forEach((q) => q.attr("ry", 150 + 14 * Math.sin(lt * 1.4) * (1 - sp) + 30 * pulse).attr("opacity", br));
      cords.forEach((q) => { const sg = q.datum(), gap = 26 * (1 - cl * pulse); q.attr("d", `M ${500 + sg * 80} 270 L ${500 + sg * gap} 290 L ${500 + sg * 80} 310 Z`); }); hic.attr("opacity", cl * pulse); };
  };

  // ---- wrinkled fingers: blood vessels narrow, the skin pulls in and forms grooves like tyre treads ----   at: water, narrow, wrinkle, grip
  MODES.pruning = (s, k, a) => {
    const top = s.append("path").attr("fill", "#e6b890").attr("stroke", "#a8774a").attr("stroke-width", 6), sub = s.append("rect").attr("x", 160).attr("y", 600).attr("width", 680).attr("height", 260).attr("fill", "#d98a8a").attr("opacity", 0.9), vessels = [680, 760, 840].map((y) => s.append("path").attr("fill", "none").attr("stroke", "#c8221f").attr("stroke-linecap", "round").datum(y)), drops = dots(s, 14, "#4fb8e8", 12, 3), ball = s.append("circle").attr("cx", 500).attr("cy", 380).attr("r", 70).attr("fill", "#4fb8e8").attr("opacity", 0), rain = s.append("circle").attr("cx", 500).attr("cy", 380).attr("r", 70).attr("fill", "none").attr("stroke", "#2f7d4f").attr("stroke-width", 8).attr("opacity", 0);
    return (lt, f, d, S) => { const wa = S("water", 0.05), na = S("narrow", 0.12), wr = S("wrinkle", 0.15), gr = S("grip", 0.08), amp = 40 * wr, pts = Array.from({ length: 35 }, (_, i) => [160 + i * 20, 600 - 20 - amp * (0.5 + 0.5 * Math.sin(i * 0.9)) * 0 - amp * Math.abs(Math.sin(i * 0.9))]);
      top.attr("d", "M 160 700 L " + pts.map((q) => q.join(" ")).join(" L ") + " L 840 700 Z"); vessels.forEach((q) => q.attr("d", `M 200 ${q.datum()} L 800 ${q.datum()}`).attr("stroke-width", 32 - 22 * na));
      drops.forEach((q, i) => { const u = (lt * 0.5 + rnd(i)) % 1; q.attr("cx", 180 + rnd(i + 2) * 640).attr("cy", 300 + u * 280).attr("opacity", wa * (1 - u)); }); ball.attr("opacity", gr); rain.attr("opacity", gr * (0.6 + 0.4 * Math.sin(lt * 5))); };
  };

  // ---- goosebumps: a tiny muscle pulls each hair upright when the nerves fire ----   at: cold, nerve, stand
  MODES.goosebumps = (s, k, a) => {
    s.append("rect").attr("x", 160).attr("y", 600).attr("width", 680).attr("height", 300).attr("fill", "#f0c4a0"); s.append("rect").attr("x", 160).attr("y", 760).attr("width", 680).attr("height", 160).attr("fill", "#e8a0a0");
    const hairs = [300, 500, 700].map((x) => { const g2 = s.append("g").datum(x), hair = g2.append("path").attr("fill", "none").attr("stroke", "#2a1a10").attr("stroke-width", 8).attr("stroke-linecap", "round"), mus = g2.append("path").attr("fill", "none").attr("stroke", "#c8442f").attr("stroke-width", 12).attr("stroke-linecap", "round"); return { x, hair, mus }; });
    const snow = s.append("text").attr("x", 500).attr("y", 260).attr("text-anchor", "middle").attr("font-size", 150).attr("fill", "#7fd0f8").attr("opacity", 0).text("❄"), pulse = dots(s, 6, "#ffd23f", 10, 4);
    return (lt, f, d, S) => { const co = S("cold", 0.05), ne = S("nerve", 0.08), st = S("stand", 0.1);
      snow.attr("opacity", co).attr("transform", `rotate(${lt * 40} 500 210)`);
      hairs.forEach(({ x, hair, mus }) => { const ang = lerp(-62, 0, st) * (x > 500 ? -1 : 1) * 1, tipx = x + Math.sin((ang * Math.PI) / 180) * 150, tipy = 600 - Math.cos((ang * Math.PI) / 180) * 150; hair.attr("d", `M ${x} 740 L ${x} 600 Q ${(x + tipx) / 2} ${600 - 60} ${tipx} ${tipy}`); mus.attr("d", `M ${x} 740 L ${x + lerp(-120, -60, st)} ${lerp(660, 690, st)}`); });
      pulse.forEach((q, i) => { const u = (lt * 0.6 + i / 6) % 1; q.attr("cx", 120 + u * 640).attr("cy", 860).attr("opacity", ne * (1 - st * 0.6) * (1 - Math.abs(u - 0.5) * 1.4)); }); };
  };

  // ---- yawning: tired or bored, the mouth opens wide, and a nearby friend yawns too ----   at: yawn, tired, copy
  MODES.yawn = (s, k, a) => {
    const mk = (x) => { const g2 = s.append("g").attr("transform", `translate(${x},560)`); g2.append("circle").attr("r", 150).attr("fill", "#e6b890").attr("stroke", "#a8774a").attr("stroke-width", 8); g2.append("circle").attr("cx", -50).attr("cy", -40).attr("r", 14).attr("fill", "#2a1a10"); g2.append("circle").attr("cx", 50).attr("cy", -40).attr("r", 14).attr("fill", "#2a1a10"); const mouth = g2.append("ellipse").attr("cy", 60).attr("fill", "#7b2a1c").attr("rx", 40).attr("ry", 12); return mouth; };
    const m1 = mk(300), m2 = mk(700), z = s.append("text").attr("x", 300).attr("y", 330).attr("text-anchor", "middle").attr("font-size", 100).attr("font-weight", 800).attr("fill", "#4a90d8").attr("opacity", 0).text("Zzz");
    return (lt, f, d, S) => { const ya = S("yawn", 0.05), ti = S("tired", 0.1), co = S("copy", 0.1), w = (ph) => Math.max(0, Math.sin(lt * 1.6 + ph)) ** 2;
      m1.attr("rx", 40 - 10 * ya * w(0)).attr("ry", 12 + 70 * ya * w(0)); m2.attr("rx", 40 - 10 * co * w(0.8)).attr("ry", 12 + 70 * co * w(0.8)); z.attr("opacity", ti * 0.8); };
  };

  // ---- soap vs a virus: the soap molecules pull apart the fatty coat and wash the pieces away ----   at: virus, soap, break, wash
  MODES.soap = (s, k, a) => {
    const v = s.append("g").attr("transform", "translate(500,560)"); v.append("circle").attr("r", 150).attr("fill", "#b45ab0").attr("stroke", "#f6c8f0").attr("stroke-width", 22); for (let i = 0; i < 14; i++) v.append("rect").attr("x", -6).attr("y", -190).attr("width", 12).attr("height", 40).attr("rx", 6).attr("fill", "#e23b2e").attr("transform", `rotate(${i * 25.7})`);
    const mols = Array.from({ length: 26 }, (_, i) => { const g2 = s.append("g").datum(i); g2.append("circle").attr("r", 12).attr("fill", "#4fb8e8"); g2.append("path").attr("d", "M 0 12 L 0 38").attr("stroke", "#ffd23f").attr("stroke-width", 6).attr("stroke-linecap", "round"); return g2; }), bits = dots(s, 18, "#b45ab0", 12, 8), wat = Array.from({ length: 6 }, (_, i) => s.append("path").attr("fill", "none").attr("stroke", "#7fb8e8").attr("stroke-width", 9).attr("stroke-linecap", "round").attr("opacity", 0).datum(i));
    return (lt, f, d, S) => { const vi = S("virus", 0.05), so = S("soap", 0.1), br = S("break", 0.12), wa = S("wash", 0.1);
      v.attr("opacity", vi * (1 - br)).attr("transform", `translate(500,560) scale(${1 - 0.3 * br})`); mols.forEach((g2) => { const i = g2.datum(), an = (i / 26) * Math.PI * 2, r = lerp(520 + 100 * Math.sin(lt + i), 190, so) + br * 160; g2.attr("transform", `translate(${500 + Math.cos(an) * r},${560 + Math.sin(an) * r}) rotate(${(an * 180) / Math.PI - 90})`).attr("opacity", so); });
      bits.forEach((q, i) => { const an = rnd(i) * Math.PI * 2, r = 60 + br * (120 + rnd(i + 3) * 160) + wa * 300; q.attr("cx", 500 + Math.cos(an) * r + wa * 200).attr("cy", 560 + Math.sin(an) * r + wa * 120).attr("opacity", br * (1 - wa)); });
      wat.forEach((q, i) => { const u = (lt * 0.8 + i / 6) % 1; q.attr("d", `M ${120 + u * 760} ${300 + i * 90} l 70 20`).attr("opacity", wa * (1 - Math.abs(u - 0.5) * 1.6)); }); };
  };

  // ---- the heart: it beats about 72 times a minute, so around 100,000 times a day ----   at: beat, count, day
  MODES.heart = (s, k, a) => {
    const hrt = s.append("path").attr("d", "M 0 120 C -260 -60 -140 -220 0 -90 C 140 -220 260 -60 0 120 Z").attr("fill", "#d8323a").attr("stroke", "#7b1a1f").attr("stroke-width", 10), cnt = s.append("text").attr("x", 500).attr("y", 880).attr("text-anchor", "middle").attr("font-size", 90).attr("font-weight", 800).attr("fill", "#2a1a10").attr("opacity", 0), lab = s.append("text").attr("x", 500).attr("y", 960).attr("text-anchor", "middle").attr("font-size", 44).attr("font-weight", 700).attr("fill", "#7b4a2b").attr("opacity", 0), pulse = s.append("path").attr("fill", "none").attr("stroke", "#d8323a").attr("stroke-width", 8).attr("stroke-linecap", "round").attr("opacity", 0);
    return (lt, f, d, S) => { const be = S("beat", 0.05), co = S("count", 0.1), da = S("day", 0.15), ph = (lt * 1.2) % 1, sc = 1 + 0.14 * Math.exp(-ph * 6) * Math.sin(ph * 12 + 1.6) * 0 + 0.12 * Math.max(0, Math.sin(ph * Math.PI * 2)) ** 3;
      hrt.attr("transform", `translate(500,520) scale(${sc})`).attr("opacity", 1);
      const n = Math.floor(co * 72 + da * (100000 - 72)); cnt.attr("opacity", co).text(n.toLocaleString("en-US")); lab.attr("opacity", co).text(da > 0.1 ? "ഒരു ദിവസത്തെ മിടിപ്പുകൾ" : "ഒരു മിനിറ്റിലെ മിടിപ്പുകൾ");
      const pts = Array.from({ length: 41 }, (_, i) => { const x = 120 + i * 19, u = ((x - 120) / 760 - lt * 0.2 + 1) % 1; return [x, 190 - (u > 0.45 && u < 0.5 ? 130 * Math.sin((u - 0.45) * 63) : u > 0.5 && u < 0.55 ? -40 : 0)]; }); pulse.attr("d", "M " + pts.map((q) => q.join(" ")).join(" L ")).attr("opacity", be); };
  };

  // ---- a pepper berry: green, ripe red, dried black, or peeled white ----   at: green, red, black, white
  MODES.pepperberry = (s, k, a) => {
    s.append("path").attr("d", "M 500 120 Q 520 300 500 420").attr("stroke", "#4a7a2a").attr("stroke-width", 14).attr("fill", "none"); const bunch = Array.from({ length: 14 }, (_, i) => { const ang = (i / 14) * Math.PI * 2, r = 50 + (i % 3) * 30, x = 500 + Math.cos(ang) * r * 0.6, y = 520 + i * 18 + (i % 2) * 20; return { c: s.append("circle").attr("cx", x).attr("cy", y).attr("r", 34).attr("stroke", "#3a2a1d").attr("stroke-width", 4), x, y }; });
    s.append("ellipse").attr("cx", 500).attr("cy", 380).attr("rx", 140).attr("ry", 46).attr("fill", "#3a8a3a").attr("transform", "rotate(-12 500 380)"); const lab = s.append("text").attr("x", 500).attr("y", 940).attr("text-anchor", "middle").attr("font-size", 70).attr("font-weight", 800).attr("fill", "#2a1a10");
    return (lt, f, d, S) => { const gr = S("green", 0.05), re = S("red", 0.1), bl = S("black", 0.12), wh = S("white", 0.12);
      const col = d3.interpolateRgb(d3.interpolateRgb(d3.interpolateRgb("#4aa83a", "#d8323a")(re), "#2a1a10")(bl), "#f3ead0")(wh * (re > 0.5 ? 1 : 1));
      bunch.forEach(({ c }) => c.attr("fill", col).attr("opacity", gr).attr("r", 34 - 8 * bl * (1 - wh) + 0 * wh)); lab.text(wh > 0.5 ? "വെള്ള കുരുമുളക്" : bl > 0.5 ? "കറുത്ത കുരുമുളക്" : re > 0.5 ? "പഴുത്തത്" : "പച്ച മണികൾ"); };
  };

  // ---- ships and the monsoon wind: Roman ships sail to Muziris on the monsoon and come back loaded with pepper ----   at: wind, sail, trade
  MODES.muziris = (s, k, a) => {
    s.append("rect").attr("x", -1400).attr("y", 560).attr("width", 3800).attr("height", 600).attr("fill", k.lg("sea", [[0, "#2a8fc0"], [1, "#146a95"]])); s.append("rect").attr("x", -400).attr("y", 520).attr("width", 300).attr("height", 120).attr("rx", 20).attr("fill", "#e6cf98"); s.append("rect").attr("x", 1100).attr("y", 520).attr("width", 300).attr("height", 120).attr("rx", 20).attr("fill", "#5d9a3a");
    s.append("text").attr("x", -250).attr("y", 500).attr("text-anchor", "middle").attr("font-size", 52).attr("font-weight", 800).attr("fill", "#4a2a17").text("റോം"); s.append("text").attr("x", 1250).attr("y", 500).attr("text-anchor", "middle").attr("font-size", 52).attr("font-weight", 800).attr("fill", "#4a2a17").text("മുസിരിസ്");
    const ship = M.chayaIcon(s, "boat", 0, 540, 200), winds = Array.from({ length: 8 }, (_, i) => s.append("path").attr("fill", "none").attr("stroke", "#fff").attr("stroke-width", 8).attr("stroke-linecap", "round").attr("opacity", 0).datum(i)), coins = dots(s, 6, "#ffd23f", 16, 4), sacks = Array.from({ length: 4 }, () => s.append("ellipse").attr("rx", 24).attr("ry", 20).attr("fill", "#8a5a36").attr("opacity", 0));
    return (lt, f, d, S) => { const wi = S("wind", 0.05), sa = S("sail", 0.25), tr = S("trade", 0.1), x = lerp(-200, 1120, E.inOut(sa));
      winds.forEach((q) => { const i = q.datum(), u = (lt * 0.5 + i / 8) % 1; q.attr("d", `M ${-200 + u * 1500} ${300 + (i % 4) * 50} l 100 0`).attr("opacity", wi * (1 - Math.abs(u - 0.5) * 2)); }); ship.attr("transform", `translate(${x},${540 + 8 * Math.sin(lt * 3)}) scale(2)`);
      coins.forEach((q, i) => q.attr("cx", 1100 + (i % 3) * 36).attr("cy", 640 - Math.floor(i / 3) * 30).attr("opacity", tr * (x > 1000 ? 1 : 0))); sacks.forEach((q, i) => q.attr("cx", 1000 - tr * 1100 + i * 40 - 0).attr("cy", 600).attr("opacity", tr * 0.9)); };
  };

  // ---- the heat receptor: capsaicin or piperine opens the tongue's heat channel and the brain feels burning; water cannot wash it, milk's casein can ----   at: bind, signal, water, milk
  MODES.receptor = (s, k, a) => {
    s.append("rect").attr("x", 160).attr("y", 600).attr("width", 680).attr("height", 40).attr("fill", "#d98a8a"); s.append("rect").attr("x", 160).attr("y", 640).attr("width", 680).attr("height", 260).attr("fill", "#e8a0a0").attr("opacity", 0.8);
    const gate = s.append("g").attr("transform", "translate(500,620)"); gate.append("rect").attr("x", -90).attr("y", -40).attr("width", 50).attr("height", 80).attr("fill", "#8a5ab8"); gate.append("rect").attr("x", 40).attr("y", -40).attr("width", 50).attr("height", 80).attr("fill", "#8a5ab8"); const lid = gate.append("rect").attr("x", -40).attr("y", -20).attr("width", 80).attr("height", 40).attr("fill", "#4a2a6a");
    const mol = dots(s, 8, "#e8613a", 18, 1), ow = dots(s, 14, "#4fb8e8", 10, 3), casein = dots(s, 6, "#fff6e2", 26, 5), sig = s.append("path").attr("fill", "none").attr("stroke", "#ffd23f").attr("stroke-width", 12).attr("stroke-linecap", "round").attr("opacity", 0), hot = s.append("text").attr("x", 500).attr("y", 180).attr("text-anchor", "middle").attr("font-size", 110).attr("font-weight", 800).attr("fill", "#c8442f").attr("opacity", 0).text("ഹോ! 🔥");
    return (lt, f, d, S) => { const bi = S("bind", 0.06), si = S("signal", 0.06), wa = S("water", 0.08), mi = S("milk", 0.1);
      mol.forEach((q, i) => { const dock = bi * (1 - mi), tx = 440 + (i % 4) * 40, ty = 560; q.attr("cx", lerp(150 + rnd(i) * 700, tx, dock) + Math.sin(lt * 2 + i) * 12 * (1 - dock) + mi * (rnd(i) - 0.5) * 120).attr("cy", lerp(300 + rnd(i + 3) * 200, ty, dock) - mi * 220 * rnd(i + 2)).attr("opacity", bi); });
      lid.attr("y", lerp(-20, -90, si * (1 - mi))); sig.attr("d", `M 500 590 L 500 ${590 - 380 * si}`).attr("opacity", si * (1 - mi)); hot.attr("opacity", si * (1 - mi) * (0.6 + 0.4 * Math.sin(lt * 8)));
      ow.forEach((q, i) => { const u = (lt * 0.6 + rnd(i)) % 1; q.attr("cx", 120 + u * 760).attr("cy", 520 + (rnd(i + 2) - 0.5) * 140).attr("opacity", wa * (1 - mi) * 0.9); }); casein.forEach((q, i) => q.attr("cx", 300 + rnd(i) * 400 + Math.sin(lt + i) * 20).attr("cy", 480 + rnd(i + 3) * 80 - mi * 80).attr("opacity", mi * 0.9)); };
  };

  // ---- turmeric and lime: curcumin is yellow in acid and red-brown in alkali ----   at: bowl, lime, acid
  MODES.turmeric = (s, k, a) => {
    const bowl = s.append("path").attr("d", "M 220 560 L 780 560 Q 760 840 500 880 Q 240 840 220 560 Z").attr("fill", "#f3ead0").attr("stroke", "#c9a77a").attr("stroke-width", 10), top = s.append("ellipse").attr("cx", 500).attr("cy", 560).attr("rx", 280).attr("ry", 60).attr("fill", "#f0b81f"), drop = s.append("circle").attr("r", 28).attr("fill", "#fff").attr("stroke", "#c9c2a8").attr("stroke-width", 4), lemon = s.append("circle").attr("r", 28).attr("fill", "#f3e04a").attr("stroke", "#a89020").attr("stroke-width", 4), lab = s.append("text").attr("x", 500).attr("y", 960).attr("text-anchor", "middle").attr("font-size", 62).attr("font-weight", 800).attr("fill", "#2a1a10");
    return (lt, f, d, S) => { const bo = S("bowl", 0.05), li = S("lime", 0.12), ac = S("acid", 0.12), red = li * (1 - ac);
      top.attr("fill", d3.interpolateRgb("#f0b81f", "#c8441f")(red)).attr("rx", 280 - 60 * 0); const y1 = lerp(200, 540, E.in ? 0 : 0) || 0; drop.attr("cx", 500).attr("cy", lerp(200, 540, clamp(li * 1.4))).attr("opacity", li > 0 && li < 1 && ac === 0 ? 1 : 0); lemon.attr("cx", 600).attr("cy", lerp(200, 540, clamp(ac * 1.4))).attr("opacity", ac > 0 && ac < 1 ? 1 : 0);
      lab.text(ac > 0.5 ? "അമ്ലം: വീണ്ടും മഞ്ഞ" : li > 0.5 ? "ക്ഷാരം: ചുവപ്പ്" : "കുർക്കുമിൻ: മഞ്ഞ"); };
  };

  // ---- puttu: steam from the pot climbs through the tube of flour and coconut and cooks it ----   at: heat, steam, layers, cooked
  MODES.puttu = (s, k, a) => {
    const pot = s.append("g"); pot.append("path").attr("d", "M 300 740 L 700 740 L 680 900 L 320 900 Z").attr("fill", "#aab3ba").attr("stroke", "#5e6b78").attr("stroke-width", 8); const w = pot.append("rect").attr("x", 316).attr("y", 840).attr("width", 368).attr("height", 52).attr("fill", "#4fb8e8");
    s.append("rect").attr("x", 430).attr("y", 380).attr("width", 140).attr("height", 360).attr("rx", 14).attr("fill", "#d9dfe4").attr("fill-opacity", 0.5).attr("stroke", "#5e6b78").attr("stroke-width", 8); const lay = [0, 1, 2, 3, 4, 5, 6].map((i) => s.append("rect").attr("x", 438).attr("y", 396 + i * 48).attr("width", 124).attr("height", 44).attr("fill", i % 2 ? "#fffaf0" : "#f0e0b8").attr("opacity", 0)), steam = dots(s, 24, "#fff", 11, 2), flame = [360, 440, 520, 600, 660].map((x) => s.append("path").attr("d", `M ${x} 960 Q ${x + 20} 920 ${x} 880 Q ${x - 20} 920 ${x} 960 Z`).attr("fill", "#ff9a2e").attr("opacity", 0));
    return (lt, f, d, S) => { const he = S("heat", 0.05), st = S("steam", 0.1), la = S("layers", 0.1), co = S("cooked", 0.15);
      flame.forEach((q, i) => q.attr("opacity", he).attr("transform", `scale(1,${0.9 + 0.15 * Math.sin(lt * 9 + i)})`)); steam.forEach((q, i) => { const u = (lt * 0.6 + rnd(i)) % 1; q.attr("cx", 470 + rnd(i + 4) * 60).attr("cy", 840 - u * 460).attr("opacity", st * (1 - u) * 0.85); });
      lay.forEach((q, i) => q.attr("opacity", la).attr("fill", d3.interpolateRgb(i % 2 ? "#fffaf0" : "#f0e0b8", i % 2 ? "#ffffff" : "#e8c97a")(co))); };
  };

  // ---- a pappadam in hot oil: trapped water turns to steam and puffs the dough, then the protein sets ----   at: oil, steam, puff, set
  MODES.pappadam = (s, k, a) => {
    s.append("rect").attr("x", 150).attr("y", 640).attr("width", 700).attr("height", 260).attr("rx", 24).attr("fill", "#e8a33d").attr("opacity", 0.85); const bub = dots(s, 24, "#fff6c8", 10, 3), pap = s.append("path").attr("fill", "#f3dca0").attr("stroke", "#a8774a").attr("stroke-width", 6), m = dots(s, 16, "#4fb8e8", 7, 6), lab = s.append("text").attr("x", 500).attr("y", 420).attr("text-anchor", "middle").attr("font-size", 60).attr("font-weight", 800).attr("fill", "#2a1a10");
    return (lt, f, d, S) => { const oi = S("oil", 0.05), st = S("steam", 0.1), pu = S("puff", 0.15), se = S("set", 0.1), h = 14 + 90 * pu, y = 600;
      pap.attr("d", `M 250 ${y} Q 500 ${y - h * 2} 750 ${y} Q 500 ${y + 24 - h * 0.2} 250 ${y} Z`).attr("fill", d3.interpolateRgb("#f3dca0", "#d8a24a")(se)); m.forEach((q, i) => q.attr("cx", 320 + rnd(i) * 360).attr("cy", y - 6 - rnd(i + 3) * h * 0.8).attr("opacity", (1 - st) * 0.9).attr("r", 7)); bub.forEach((q, i) => { const u = (lt * 0.7 + rnd(i)) % 1; q.attr("cx", 200 + rnd(i + 4) * 600).attr("cy", 860 - u * 240).attr("opacity", oi * (1 - u) * 0.9); });
      lab.text(pu > 0.4 ? "ആവി വീർപ്പിക്കുന്നു" : st > 0.3 ? "ജലം ആവിയാകുന്നു" : "ചൂടെണ്ണ"); };
  };

  // ---- a cardamom pod: seeds full of aroma oil that evaporates; crushing releases more ----   at: pod, oil, aroma, crush
  MODES.cardamom = (s, k, a) => {
    const pod = s.append("g").attr("transform", "translate(500,600)"); pod.append("path").attr("d", "M -260 0 Q 0 -190 260 0 Q 0 190 -260 0 Z").attr("fill", "#9acb6a").attr("stroke", "#4a7a2a").attr("stroke-width", 10); const seeds = Array.from({ length: 14 }, (_, i) => pod.append("circle").attr("cx", -190 + i * 29).attr("cy", (i % 2 ? 24 : -24)).attr("r", 18).attr("fill", "#3a2a1d").attr("opacity", 0));
    const oil = dots(s, 14, "#ffd23f", 7, 2), aroma = Array.from({ length: 8 }, (_, i) => s.append("path").attr("fill", "none").attr("stroke", "#c9e85a").attr("stroke-width", 8).attr("stroke-linecap", "round").attr("opacity", 0).datum(i)), bits = dots(s, 16, "#6a8a3a", 12, 5);
    return (lt, f, d, S) => { const po = S("pod", 0.05), oi = S("oil", 0.1), ar = S("aroma", 0.1), cr = S("crush", 0.12);
      pod.attr("opacity", po * (1 - cr)).attr("transform", `translate(500,${600}) scale(${1 - 0.3 * cr})`); seeds.forEach((q) => q.attr("opacity", oi)); oil.forEach((q, i) => q.attr("cx", 330 + rnd(i) * 340).attr("cy", 580 + (rnd(i + 3) - 0.5) * 100).attr("opacity", oi * 0.85));
      aroma.forEach((q, i) => { const u = (lt * (0.5 + 0.5 * cr) + i / 8) % 1, x = 320 + i * 50; q.attr("d", `M ${x} ${520 - u * 260} q 16 -22 0 -44 t 0 -44`).attr("opacity", ar * (1 - u) * (0.7 + 0.5 * cr)); }); bits.forEach((q, i) => q.attr("cx", 330 + rnd(i) * 340).attr("cy", 620 + (rnd(i + 2) - 0.5) * 80).attr("opacity", cr * 0.9)); };
  };

  // ---- pickle: salt draws water out of the fruit and out of bacteria, so they cannot grow ----   at: salt, water, bacteria, oil
  MODES.pickle = (s, k, a) => {
    s.append("path").attr("d", "M 320 380 L 680 380 L 700 880 Q 700 900 680 900 L 320 900 Q 300 900 300 880 Z").attr("fill", "#d9eef7").attr("fill-opacity", 0.4).attr("stroke", "#8fb0b8").attr("stroke-width", 10); s.append("rect").attr("x", 300).attr("y", 340).attr("width", 400).attr("height", 40).attr("rx", 10).attr("fill", "#c8442f");
    const frs = Array.from({ length: 6 }, (_, i) => s.append("circle").attr("cx", 380 + (i % 3) * 120).attr("cy", 560 + Math.floor(i / 3) * 140).attr("r", 54).attr("fill", "#8fc04a").attr("stroke", "#4a7a2a").attr("stroke-width", 5)), salts = dots(s, 20, "#fff", 8, 3), water = dots(s, 22, "#4fb8e8", 8, 5), bact = Array.from({ length: 6 }, (_, i) => s.append("ellipse").attr("rx", 24).attr("ry", 12).attr("fill", "#d05a5a").attr("opacity", 0).datum(i)), oil = s.append("rect").attr("x", 304).attr("y", 400).attr("width", 392).attr("height", 40).attr("fill", "#e8a33d").attr("opacity", 0);
    return (lt, f, d, S) => { const sa = S("salt", 0.05), wa = S("water", 0.1), ba = S("bacteria", 0.12), oi = S("oil", 0.1);
      salts.forEach((q, i) => q.attr("cx", 340 + rnd(i) * 320).attr("cy", 470 + rnd(i + 3) * 380).attr("opacity", sa * 0.9)); water.forEach((q, i) => { const u = (lt * 0.4 + rnd(i)) % 1; q.attr("cx", 360 + rnd(i + 2) * 280).attr("cy", 700 - u * 280).attr("opacity", wa * (1 - u)); });
      bact.forEach((q) => { const i = q.datum(); q.attr("cx", 360 + (i % 3) * 140 + Math.sin(lt + i) * 10).attr("cy", 480 + Math.floor(i / 3) * 360).attr("rx", 24 - 14 * ba).attr("ry", 12 - 5 * ba).attr("opacity", sa > 0 ? 1 : 0).attr("fill", d3.interpolateRgb("#d05a5a", "#7a5a5a")(ba)); }); oil.attr("opacity", oi); };
  };

  // ---- the Western Ghats in profile: monsoon wind from the sea, rain on the slope, life in bands of height, a long isolated range with a gap ----   at: wind, rain, bands, isolation, gap
  MODES.ghats = (s, k, a) => {
    s.append("rect").attr("x", -1400).attr("y", -400).attr("width", 3800).attr("height", 1100).attr("fill", k.lg("sky", [[0, "#9fb6c4"], [1, "#e3ebee"]])); s.append("rect").attr("x", -1400).attr("y", 700).attr("width", 1500).attr("height", 500).attr("fill", k.lg("sea", [[0, "#2a8fc0"], [1, "#146a95"]]));
    const ridge = "M 100 760 L 420 560 L 560 300 L 700 520 L 940 700 L 1500 760 L 1500 1100 L 100 1100 Z"; s.append("path").attr("d", ridge).attr("fill", "#7a8f5a"); const bands = [["#2f6a3a", 700, 760], ["#4f8a3a", 520, 700], ["#b8c070", 320, 520]].map(([col, y0, y1]) => s.append("path").attr("d", ridge).attr("fill", col).attr("opacity", 0).attr("clip-path", "none").datum([y0, y1, col]));
    const cut = s.append("clipPath").attr("id", id0(k) + "ghc"); cut.append("path").attr("d", ridge);
    const bandR = [[700, 80, "#2f6a3a"], [520, 180, "#4f8a3a"], [300, 220, "#c8d070"]].map(([y, h, col]) => s.append("rect").attr("x", 100).attr("y", y).attr("width", 1400).attr("height", h).attr("fill", col).attr("opacity", 0).attr("clip-path", `url(#${id0(k)}ghc)`));
    const icons = [M.chayaIcon(s, "elephant", 520, 690, 100), M.chayaIcon(s, "bird", 600, 520, 90), M.chayaIcon(s, "leaf", 560, 370, 90)].map((g2) => g2.attr("opacity", 0));
    const gapL = s.append("g").attr("opacity", 0); gapL.append("rect").attr("x", 1040).attr("y", 600).attr("width", 120).attr("height", 200).attr("fill", "#e3ebee"); gapL.append("path").attr("d", "M 1100 560 L 1100 820").attr("stroke", "#c8442f").attr("stroke-width", 8).attr("stroke-dasharray", "12 10"); const cl = [M.chayaIcon(s, "cloudDark", 200, 420, 260), M.chayaIcon(s, "cloudDark", 380, 360, 220)], rain = dots(s, 40, "#4aa3d8", 6, 3), winds = Array.from({ length: 6 }, (_, i) => s.append("path").attr("fill", "none").attr("stroke", "#fff").attr("stroke-width", 9).attr("stroke-linecap", "round").attr("opacity", 0).datum(i));
    return (lt, f, d, S) => { const wi = S("wind", 0.04), ra = S("rain", 0.06), ba = S("bands", 0.1), is = S("isolation", 0.06), ga = S("gap", 0.06);
      winds.forEach((q) => { const i = q.datum(), u = (lt * 0.5 + i / 6) % 1; q.attr("d", `M ${-300 + u * 700} ${380 + i * 50} l 110 0`).attr("opacity", wi * (1 - Math.abs(u - 0.5) * 2)); }); cl.forEach((c2, i) => c2.attr("opacity", ra).attr("transform", `translate(${[200, 380][i] + 8 * Math.sin(lt + i)},${[420, 360][i]}) scale(${[2.6, 2.2][i]})`));
      rain.forEach((q, i) => { const u = (lt * 0.8 + rnd(i)) % 1; q.attr("cx", 180 + rnd(i + 2) * 380 - u * 30).attr("cy", 440 + u * 260).attr("opacity", ra * (1 - u)); }); bandR.forEach((q, i) => q.attr("opacity", clamp(ba * 3 - i) * 0.85)); icons.forEach((g2, i) => g2.attr("opacity", clamp(ba * 3 - i - 0.5)).attr("transform", `translate(${[520, 600, 560][i]},${[690, 520, 370][i]}) scale(1.1)`));
      gapL.attr("opacity", ga); }; function id0(k2) { return "g" + Math.abs(Math.floor(rnd(1) * 9999)); }
  };

  // ---- neelakurinji: a whole hillside flowers in the same year, sets seed, and waits twelve years ----   at: grow, bloom, seed, timeline
  MODES.neelakurinji = (s, k, a) => {
    s.append("path").attr("d", "M -400 760 Q 200 460 500 520 Q 800 580 1400 400 L 1400 1100 L -400 1100 Z").attr("fill", "#6a9a4a"); const pl = Array.from({ length: 70 }, (_, i) => { const x = -200 + rnd(i) * 1300, y = 560 + rnd(i + 3) * 360 + Math.sin(x * 0.004) * 30; return s.append("circle").attr("cx", x).attr("cy", y - 0).attr("r", 12 + rnd(i + 5) * 10).attr("fill", "#4a8a3a").datum(i); });
    const tl = s.append("g").attr("opacity", 0).attr("transform", "translate(150,960)"); tl.append("line").attr("x1", 0).attr("x2", 700).attr("stroke", "#4a2a17").attr("stroke-width", 8); for (let i = 0; i <= 12; i++) tl.append("circle").attr("cx", i * 58).attr("r", i === 0 || i === 12 ? 18 : 8).attr("fill", i === 0 || i === 12 ? "#6a4ab8" : "#4a2a17"); tl.append("text").attr("x", 350).attr("y", -30).attr("text-anchor", "middle").attr("font-size", 56).attr("font-weight", 800).attr("fill", "#4a2a17").text("12 വർഷം");
    const seeds = dots(s, 30, "#3a2a1d", 5, 3);
    return (lt, f, d, S) => { const gr = S("grow", 0.05), bl = S("bloom", 0.1), se = S("seed", 0.1), ti = S("timeline", 0.08);
      pl.forEach((q) => q.attr("fill", d3.interpolateRgb("#4a8a3a", "#7a5ad8")(bl * (1 - se * 0.7))).attr("opacity", gr).attr("r", 12 + q.datum() % 10 * 0.8 + 4 * bl * Math.sin(lt * 2 + q.datum()))); seeds.forEach((q, i) => { const u = (lt * 0.4 + rnd(i)) % 1; q.attr("cx", -100 + rnd(i + 3) * 1100).attr("cy", 620 + u * 280).attr("opacity", se * (1 - u)); }); tl.attr("opacity", ti); };
  };

  // ---- a kingfisher's beak: its shape parts the water without a splash, the same shape quietens a train in a tunnel ----   at: dive, beak, train
  MODES.kingfisher = (s, k, a) => {
    s.append("rect").attr("x", -1400).attr("y", 560).attr("width", 3800).attr("height", 500).attr("fill", k.lg("w", [[0, "#2a8fc0"], [1, "#146a95"]])); const bird = s.append("g"); bird.append("ellipse").attr("rx", 70).attr("ry", 40).attr("fill", "#2d8fd0"); bird.append("circle").attr("cx", 60).attr("cy", 10).attr("r", 28).attr("fill", "#e8832e"); bird.append("path").attr("d", "M 80 10 L 230 24 L 80 34 Z").attr("fill", "#2a1a10");
    const rings = [0, 1, 2].map((i) => s.append("ellipse").attr("cx", 260).attr("cy", 566).attr("fill", "none").attr("stroke", "#e9f8ff").attr("stroke-width", 5).attr("opacity", 0).datum(i)), splash = dots(s, 14, "#fff", 12, 2), tr = s.append("g").attr("opacity", 0).attr("transform", "translate(700,380)"); tr.append("path").attr("d", "M -300 40 L 40 40 Q 200 40 300 -20 Q 200 -80 40 -80 L -300 -80 Z").attr("fill", "#e8eef2").attr("stroke", "#5e6b78").attr("stroke-width", 8); tr.append("rect").attr("x", -280).attr("y", -60).attr("width", 220).attr("height", 40).attr("fill", "#8fc4e3");
    const beak = s.append("path").attr("d", "M 700 600 L 960 640 L 700 680 Z").attr("fill", "#2a1a10").attr("opacity", 0);
    return (lt, f, d, S) => { const di = S("dive", 0.1), be = S("beak", 0.08), trn = S("train", 0.1), y = lerp(150, 650, E.in ? E.out(di) : di);
      bird.attr("transform", `translate(${lerp(120, 330, di)},${y}) rotate(${lerp(10, 75, di)})`).attr("opacity", 1); rings.forEach((q) => { const u = (lt * 0.5 + q.datum() / 3) % 1; q.attr("rx", 20 + u * 100).attr("ry", 6 + u * 24).attr("opacity", di > 0.9 ? 0.6 * (1 - u) : 0); });
      splash.forEach((q, i) => q.attr("cx", 330 + (rnd(i) - 0.5) * 80).attr("cy", 560 - ((lt * 80 + i * 20) % 120)).attr("opacity", 0)); beak.attr("opacity", be); tr.attr("opacity", trn); };
  };

  // ---- the bee waggle dance: the angle to the vertical is the angle to the Sun, the length of the waggle is the distance ----   at: dance, angle, distance
  MODES.beedance = (s, k, a) => {
    s.append("rect").attr("x", 120).attr("y", 280).attr("width", 380).attr("height", 600).attr("rx", 20).attr("fill", "#e8a33d").attr("opacity", 0.55); for (let r = 0; r < 4; r++) for (let c = 0; c < 3; c++) s.append("path").attr("d", d3.range(6).map((i) => `${i ? "L" : "M"} ${200 + c * 100 + (r % 2) * 50 + 40 * Math.cos(Math.PI / 6 + i * Math.PI / 3)} ${380 + r * 100 + 40 * Math.sin(Math.PI / 6 + i * Math.PI / 3)}`).join(" ") + " Z").attr("fill", "none").attr("stroke", "#a8774a").attr("stroke-width", 4);
    const sun = M.chayaIcon(s, "sun", 760, 240, 180), flowers = [M.chayaIcon(s, "leaf", 940, 780, 120), M.chayaIcon(s, "leaf", 1010, 790, 100)], dir = s.append("line").attr("stroke", "#ffd23f").attr("stroke-width", 6).attr("stroke-dasharray", "12 10").attr("opacity", 0), bee = s.append("g"); bee.append("ellipse").attr("rx", 20).attr("ry", 13).attr("fill", "#f6b945").attr("stroke", "#2a1a10").attr("stroke-width", 3); bee.append("rect").attr("x", -5).attr("y", -13).attr("width", 6).attr("height", 26).attr("fill", "#2a1a10");
    const path = s.append("path").attr("fill", "none").attr("stroke", "#c8442f").attr("stroke-width", 6).attr("stroke-dasharray", "6 8").attr("opacity", 0), vert = s.append("line").attr("x1", 310).attr("x2", 310).attr("y1", 300).attr("y2", 860).attr("stroke", "#fff").attr("stroke-width", 4).attr("stroke-dasharray", "8 10").attr("opacity", 0), arc = s.append("path").attr("fill", "none").attr("stroke", "#c8442f").attr("stroke-width", 8).attr("opacity", 0);
    return (lt, f, d, S) => { const da = S("dance", 0.05), an = S("angle", 0.1), di = S("distance", 0.1), th = (35 * Math.PI) / 180, len = lerp(120, 200, di);
      const u = (lt * 0.7) % 1, seg = u < 0.5 ? u * 2 : 1, ret = u < 0.5 ? 0 : u * 2 - 1, wx = 310 + Math.sin(th) * len * (u < 0.5 ? seg : 1 - ret) + (u < 0.5 ? Math.sin(lt * 40) * 6 : (ret - 0.5) * 0), wy = 580 - Math.cos(th) * len * (u < 0.5 ? seg : 1 - ret);
      bee.attr("opacity", da).attr("transform", `translate(${wx},${wy}) rotate(${(th * 180) / Math.PI})`); path.attr("d", `M 310 580 L ${310 + Math.sin(th) * len} ${580 - Math.cos(th) * len}`).attr("opacity", da * 0.9); vert.attr("opacity", an); arc.attr("d", `M 310 ${580 - 90} A 90 90 0 0 1 ${310 + Math.sin(th) * 90} ${580 - Math.cos(th) * 90}`).attr("opacity", an);
      dir.attr("x1", 760).attr("y1", 280).attr("x2", 940).attr("y2", 740).attr("opacity", an); sun.attr("transform", "translate(760,240) scale(1.8)"); flowers.forEach((q, i) => q.attr("transform", `translate(${[940, 1010][i]},${[780, 790][i]}) scale(1.2)`).attr("opacity", di)); };
  };

  // ---- a bat: it shouts, the echo returns from a moth, and the delay says how far ----   at: call, echo, catch
  MODES.bat = (s, k, a) => {
    for (let i = 0; i < 40; i++) s.append("circle").attr("cx", -300 + rnd(i) * 1700).attr("cy", -100 + rnd(i + 5) * 900).attr("r", 2).attr("fill", "#fff").attr("opacity", 0.5);
    const bt = M.chayaIcon(s, "bird", 220, 520, 160), moth = s.append("g"); moth.append("ellipse").attr("rx", 18).attr("ry", 10).attr("fill", "#d9c8a0"); moth.append("path").attr("d", "M 0 0 Q -34 -34 -44 0 Q -34 34 0 0 Z M 0 0 Q 34 -34 44 0 Q 34 34 0 0 Z").attr("fill", "#e8d8b0").attr("opacity", 0.8);
    const out = [0, 1, 2].map((i) => s.append("path").attr("fill", "none").attr("stroke", "#ffd23f").attr("stroke-width", 7).attr("opacity", 0).datum(i)), back = [0, 1, 2].map((i) => s.append("path").attr("fill", "none").attr("stroke", "#9fd8f5").attr("stroke-width", 7).attr("opacity", 0).datum(i)), lab = s.append("text").attr("x", 520).attr("y", 760).attr("text-anchor", "middle").attr("font-size", 60).attr("font-weight", 800).attr("fill", "#fff6e2").attr("opacity", 0).text("സമയം = ദൂരം");
    return (lt, f, d, S) => { const ca = S("call", 0.05), ec = S("echo", 0.1), ct = S("catch", 0.1), mx = lerp(780, 600, ct), bx = lerp(220, 480, ct);
      bt.attr("transform", `translate(${bx},520) scale(2.2)`).attr("opacity", 1); moth.attr("transform", `translate(${mx},${480 + 20 * Math.sin(lt * 5)})`).attr("opacity", ct > 0.95 ? 0 : 1);
      out.forEach((q) => { const u = (lt * 0.5 + q.datum() / 3) % 1, r = 40 + u * (mx - bx - 40); q.attr("d", `M ${bx + r} ${520 - r * 0.5} Q ${bx + r + 40} 520 ${bx + r} ${520 + r * 0.5}`).attr("opacity", ca * (1 - u) * (1 - ct * 0.4)); });
      back.forEach((q) => { const u = (lt * 0.5 + q.datum() / 3) % 1, x = mx - u * (mx - bx - 30); q.attr("d", `M ${x} ${480 - 40} Q ${x - 30} 480 ${x} ${480 + 40}`).attr("opacity", ec * (1 - u)); }); lab.attr("opacity", ec); };
  };

  // ---- a mangrove: salt filtered at the roots or pushed out through the leaves, breathing roots, waves broken, fish nursery ----   at: salt, leaf, breath, wave, fish
  MODES.mangrove = (s, k, a) => {
    s.append("rect").attr("x", -1400).attr("y", 600).attr("width", 3800).attr("height", 500).attr("fill", k.lg("w", [[0, "#3a90b8"], [1, "#1a5a7a"]])).attr("opacity", 0.9); s.append("rect").attr("x", -1400).attr("y", 900).attr("width", 3800).attr("height", 300).attr("fill", "#6a4a2c");
    const tree = s.append("g"); tree.append("path").attr("d", "M 480 420 L 520 420 L 540 640 L 460 640 Z").attr("fill", "#6a4a2c"); for (const dx of [-90, -40, 40, 90]) tree.append("path").attr("d", `M ${500 + dx * 0.2} 600 Q ${500 + dx * 1.2} 700 ${500 + dx * 1.4} 910`).attr("fill", "none").attr("stroke", "#6a4a2c").attr("stroke-width", 12); tree.append("circle").attr("cx", 500).attr("cy", 340).attr("r", 150).attr("fill", "#2f7d4f"); tree.append("circle").attr("cx", 400).attr("cy", 400).attr("r", 100).attr("fill", "#3a915d"); tree.append("circle").attr("cx", 610).attr("cy", 410).attr("r", 100).attr("fill", "#277043");
    const pn = [200, 260, 760, 820, 880].map((x) => s.append("path").attr("d", `M ${x} 920 L ${x} 600`).attr("stroke", "#8a5a36").attr("stroke-width", 12).attr("stroke-linecap", "round").attr("opacity", 0)), salt = dots(s, 20, "#fff", 8, 2), crys = dots(s, 12, "#fff", 6, 4), fish = Array.from({ length: 6 }, (_, i) => s.append("path").attr("d", "M -14 0 Q 0 -10 14 0 Q 0 10 -14 0 M 14 0 L 24 -8 L 24 8 Z").attr("fill", "#f6b945").attr("opacity", 0).datum(i)), wv = s.append("path").attr("fill", "none").attr("stroke", "#e9f8ff").attr("stroke-width", 7);
    return (lt, f, d, S) => { const sl = S("salt", 0.05), le = S("leaf", 0.08), br = S("breath", 0.06), wa = S("wave", 0.06), fi = S("fish", 0.06);
      salt.forEach((q, i) => { const u = (lt * 0.4 + rnd(i)) % 1; q.attr("cx", 300 + rnd(i + 2) * 400).attr("cy", 880 - Math.min(u, 0.35 + 0.0) * 600 * (u < 0.35 ? 1 : 0)).attr("opacity", sl * (u < 0.35 ? 1 : 0)); });
      crys.forEach((q, i) => q.attr("cx", 380 + rnd(i) * 240).attr("cy", 300 + rnd(i + 3) * 160).attr("opacity", le)); pn.forEach((q) => q.attr("opacity", br)); fish.forEach((q) => { const i = q.datum(); q.attr("transform", `translate(${360 + i * 60 + 30 * Math.sin(lt + i)},${760 + (i % 2) * 50})`).attr("opacity", fi); });
      wv.attr("d", "M -300 " + [0, 1].map(() => "").join("") + Array.from({ length: 50 }, (_, i) => { const x = -300 + i * 30, damp = wa > 0 ? Math.exp(-Math.pow((x - 500) / 300, 2)) : 0; return `L ${x} ${600 - 26 * (1 - 0.85 * damp * wa) * Math.sin(x * 0.04 - lt * 3)}`; }).join(" ").slice(1)); };
  };

  // ---- peacock colour: thin layers in the feather reflect some colours and the colour changes with the angle ----   at: layers, light, tilt
  MODES.peacock = (s, k, a) => {
    const st = s.append("g").attr("transform", "translate(500,620)"), layers = Array.from({ length: 9 }, (_, i) => st.append("rect").attr("x", -200).attr("y", -140 + i * 34).attr("width", 400).attr("height", 18).attr("rx", 6).attr("fill", i % 2 ? "#2a1a10" : "#7ad8c8").attr("opacity", 0)), rays = Array.from({ length: 7 }, (_, i) => s.append("path").attr("fill", "none").attr("stroke-width", 9).attr("stroke-linecap", "round").attr("opacity", 0).datum(i)), cols = ["#e23b2e", "#f08a24", "#f6d12a", "#3aa84a", "#2d8fd0", "#3b4fb8", "#7a3fb0"], sw = s.append("circle").attr("cx", 900).attr("cy", 380).attr("r", 70).attr("stroke", "#fff").attr("stroke-width", 6).attr("opacity", 0);
    return (lt, f, d, S) => { const la = S("layers", 0.06), li = S("light", 0.08), ti = S("tilt", 0.2), ang = 28 * Math.sin(ti * Math.PI) * (ti > 0 ? 1 : 0) + 0;
      st.attr("transform", `translate(500,620) rotate(${ang})`); layers.forEach((q) => q.attr("opacity", la));
      rays.forEach((q) => { const i = q.datum(), c = (i + ti * 4 + lt * 0.0) % 7, col = cols[Math.floor(c)]; q.attr("d", `M ${100 + i * 40} 180 L ${220 + i * 30} 520 L ${360 + i * 50 + ang * 4} 180`).attr("stroke", i === Math.floor(c) ? col : "#fff").attr("opacity", li * (i === 3 ? 1 : 0.35)); });
      sw.attr("fill", cols[Math.floor(clamp(0.25 + ti * 0.7) * 6.99)]).attr("opacity", li); };
  };

  // ---- a QR code: three corner markers, data, and extra error-correcting data so a torn corner still scans ----   at: grid, markers, tear, scan
  MODES.qr = (s, k, a) => {
    const N = 15, U = 40, X0 = 300, Y0 = 380, cells = []; s.append("rect").attr("x", X0 - 30).attr("y", Y0 - 30).attr("width", N * U + 60).attr("height", N * U + 60).attr("rx", 16).attr("fill", "#fff").attr("stroke", "#c9a77a").attr("stroke-width", 6);
    const fin = (x, y) => [0, 1, 2].map((i) => i); for (let r = 0; r < N; r++) for (let c = 0; c < N; c++) { const inF = (r < 7 && c < 7) || (r < 7 && c > 7) || (r > 7 && c < 7), edge = inF && (((r % 7 === 0 || r % 7 === 6) || (c % 7 === 0 || c % 7 === 6)) || ((r % 7 >= 2 && r % 7 <= 4) && (c % 7 >= 2 && c % 7 <= 4))), on = inF ? edge : rnd(r * 31 + c) > 0.5; const q = s.append("rect").attr("x", X0 + c * U).attr("y", Y0 + r * U).attr("width", U - 2).attr("height", U - 2).attr("fill", on ? "#2a1a10" : "#fff").attr("opacity", 0).datum({ r, c, inF }); cells.push(q); }
    const scan = s.append("rect").attr("x", X0 - 20).attr("width", N * U + 40).attr("height", 14).attr("fill", "#e23b2e").attr("opacity", 0), ok = s.append("text").attr("x", 600).attr("y", 330).attr("text-anchor", "middle").attr("font-size", 80).attr("font-weight", 800).attr("fill", "#2f7d4f").attr("opacity", 0).text("✓ സ്കാൻ ആയി");
    return (lt, f, d, S) => { const gr = S("grid", 0.05), ma = S("markers", 0.08), te = S("tear", 0.08), sc = S("scan", 0.1);
      cells.forEach((q) => { const { r, c, inF } = q.datum(), torn = te > 0 && r > 9 && c > 8; q.attr("opacity", (inF ? ma : gr) * (torn ? 1 - te : 1)).attr("stroke", inF && ma > 0 && ma < 1 ? "#ffd23f" : "none"); });
      scan.attr("y", Y0 + ((lt * 0.5) % 1) * N * U).attr("opacity", sc * 0.8); ok.attr("opacity", sc * (Math.sin(lt * 3) > -0.3 ? 1 : 0.6)); };
  };

  // ---- a hot phone: the chip and the battery turn some electricity into heat that has little room to escape ----   at: chip, battery, heat, sun
  MODES.phoneheat = (s, k, a) => {
    const ph = s.append("g").attr("transform", "translate(500,600)"); ph.append("rect").attr("x", -170).attr("y", -330).attr("width", 340).attr("height", 660).attr("rx", 40).attr("fill", "#2a2f35").attr("stroke", "#8d99a6").attr("stroke-width", 8); const chip = ph.append("rect").attr("x", -80).attr("y", -230).attr("width", 160).attr("height", 120).attr("rx", 14).attr("fill", "#8d99a6"), bat = ph.append("rect").attr("x", -110).attr("y", -50).attr("width", 220).attr("height", 300).attr("rx", 20).attr("fill", "#4a8a5a");
    for (let i = 0; i < 4; i++) ph.append("line").attr("x1", -80).attr("x2", -110).attr("y1", -220 + i * 30).attr("y2", -220 + i * 30).attr("stroke", "#c9cfd4").attr("stroke-width", 6); const heat = Array.from({ length: 7 }, (_, i) => s.append("path").attr("fill", "none").attr("stroke", "#ff7a3c").attr("stroke-width", 9).attr("stroke-linecap", "round").attr("opacity", 0).datum(i)), th = M.chayaIcon(s, "thermo", 900, 560, 180).attr("opacity", 0), sun = M.chayaIcon(s, "sun", 880, 180, 180).attr("opacity", 0);
    return (lt, f, d, S) => { const ch = S("chip", 0.05), ba = S("battery", 0.08), he = S("heat", 0.08), su = S("sun", 0.08); chip.attr("fill", d3.interpolateRgb("#8d99a6", "#ff6a2e")(ch * (0.7 + 0.3 * Math.sin(lt * 4)))); bat.attr("fill", d3.interpolateRgb("#4a8a5a", "#e8a33d")(ba));
      heat.forEach((q) => { const i = q.datum(), u = (lt * 0.6 + i / 7) % 1, x = 340 + i * 54; q.attr("d", `M ${x} ${260 - u * 220} q 14 -20 0 -40 t 0 -40`).attr("opacity", he * (1 - u)); }); th.attr("opacity", he).attr("transform", "translate(900,560) scale(1.8)"); sun.attr("opacity", su).attr("transform", "translate(880,180) scale(1.8)"); };
  };

  // ---- an induction cooker: a coil makes a changing magnetic field, which drives currents in the pan itself ----   at: coil, field, eddy, heat
  MODES.induction = (s, k, a) => {
    s.append("rect").attr("x", 160).attr("y", 760).attr("width", 680).attr("height", 40).attr("rx", 10).attr("fill", "#2a2f35"); const coil = s.append("path").attr("fill", "none").attr("stroke", "#e8a33d").attr("stroke-width", 12).attr("stroke-linecap", "round").attr("d", "M 260 860 " + Array.from({ length: 12 }, (_, i) => `q 20 -50 40 0`).join(" ")), pan = s.append("rect").attr("x", 200).attr("y", 640).attr("width", 600).attr("height", 100).attr("rx", 16).attr("fill", "#5e6b78").attr("stroke", "#2a2f35").attr("stroke-width", 8);
    const field = Array.from({ length: 5 }, (_, i) => s.append("path").attr("fill", "none").attr("stroke", "#7fb8e8").attr("stroke-width", 7).attr("stroke-dasharray", "10 8").attr("opacity", 0).datum(i)), eddy = Array.from({ length: 4 }, (_, i) => s.append("ellipse").attr("cx", 280 + i * 150).attr("cy", 690).attr("rx", 50).attr("ry", 22).attr("fill", "none").attr("stroke", "#ffd23f").attr("stroke-width", 7).attr("opacity", 0)), heat = Array.from({ length: 5 }, (_, i) => s.append("path").attr("fill", "none").attr("stroke", "#ff7a3c").attr("stroke-width", 9).attr("stroke-linecap", "round").attr("opacity", 0).datum(i));
    return (lt, f, d, S) => { const co = S("coil", 0.05), fi = S("field", 0.08), ed = S("eddy", 0.08), he = S("heat", 0.1);
      coil.attr("opacity", co).attr("stroke", d3.interpolateRgb("#e8a33d", "#ffd23f")(0.5 + 0.5 * Math.sin(lt * 10))); field.forEach((q) => { const i = q.datum(), x = 260 + i * 120; q.attr("d", `M ${x} 840 Q ${x + 60} ${700 - 30 * Math.sin(lt * 8)} ${x + 120} 840`).attr("opacity", fi * 0.9).attr("stroke-dashoffset", -lt * 60); });
      eddy.forEach((q, i) => q.attr("opacity", ed).attr("rx", 50 + 8 * Math.sin(lt * 9 + i))); pan.attr("fill", d3.interpolateRgb("#5e6b78", "#d8452f")(he)); heat.forEach((q) => { const i = q.datum(), u = (lt * 0.6 + i / 5) % 1; q.attr("d", `M ${290 + i * 110} ${620 - u * 170} q 14 -20 0 -40`).attr("opacity", he * (1 - u)); }); };
  };

  // ---- GPS: distances to several satellites, each a circle, meet at your position ----   at: sat, circles, fix
  MODES.gps = (s, k, a) => {
    s.append("circle").attr("cx", 500).attr("cy", 1250).attr("r", 560).attr("fill", k.lg("e", [[0, "#3aa0e8"], [1, "#1a5fa8"]])); const sats = [[220, 260], [420, 160], [640, 180], [820, 300]].map(([x, y]) => M.chayaIcon(s, "satellite", x, y, 90).attr("opacity", 0)), circ = sats.map(() => s.append("circle").attr("fill", "none").attr("stroke", "#ffd23f").attr("stroke-width", 6).attr("opacity", 0)), me = M.chayaIcon(s, "person", 540, 700, 110), pin = s.append("circle").attr("cx", 540).attr("cy", 700).attr("r", 24).attr("fill", "none").attr("stroke", "#c8442f").attr("stroke-width", 8).attr("opacity", 0);
    const P = [[220, 260], [420, 160], [640, 180], [820, 300]];
    return (lt, f, d, S) => { const sa = S("sat", 0.05), ci = S("circles", 0.15), fx = S("fix", 0.08);
      sats.forEach((q, i) => q.attr("opacity", sa).attr("transform", `translate(${P[i][0]},${P[i][1]}) scale(1)`)); circ.forEach((q, i) => { const r = Math.hypot(540 - P[i][0], 700 - P[i][1]); q.attr("cx", P[i][0]).attr("cy", P[i][1]).attr("r", r * ci).attr("opacity", ci > 0 ? 0.8 * (1 - 0.4 * fx) : 0); }); pin.attr("opacity", fx).attr("r", 24 + 10 * Math.sin(lt * 6)); me.attr("transform", "translate(540,700) scale(1.2)"); };
  };

  // ---- a capacitive touchscreen: a conductive fingertip disturbs the electric field; a normal glove does not ----   at: field, finger, glove
  MODES.touchscreen = (s, k, a) => {
    s.append("rect").attr("x", 160).attr("y", 740).attr("width", 680).attr("height", 40).attr("rx", 8).attr("fill", "#bfe3f6").attr("stroke", "#5e6b78").attr("stroke-width", 6); s.append("rect").attr("x", 160).attr("y", 780).attr("width", 680).attr("height", 90).attr("fill", "#2a2f35"); for (let i = 0; i < 9; i++) s.append("rect").attr("x", 180 + i * 74).attr("y", 790).attr("width", 50).attr("height", 14).attr("fill", "#8d99a6");
    const fl = Array.from({ length: 7 }, (_, i) => s.append("path").attr("fill", "none").attr("stroke", "#7fb8e8").attr("stroke-width", 6).attr("stroke-dasharray", "8 8").attr("opacity", 0).datum(i)), fing = s.append("g"); fing.append("rect").attr("x", -40).attr("y", -260).attr("width", 80).attr("height", 260).attr("rx", 40).attr("fill", "#e6b890"); const glove = s.append("rect").attr("x", -56).attr("y", -190).attr("width", 112).attr("height", 200).attr("rx", 56).attr("fill", "#4a90d8").attr("opacity", 0), glv = fing, cross = s.append("text").attr("x", 500).attr("y", 380).attr("text-anchor", "middle").attr("font-size", 120).attr("fill", "#c8442f").attr("opacity", 0).text("✕");
    return (lt, f, d, S) => { const fi = S("field", 0.05), fg = S("finger", 0.1), gl = S("glove", 0.1), y = lerp(430, 726, E.out(fg)) - (gl > 0 ? 0 : 0);
      fing.attr("transform", `translate(500,${y})`).attr("opacity", fg > 0 ? 1 : 0); glove.attr("opacity", gl).attr("transform", `translate(500,${y})`);
      fl.forEach((q) => { const i = q.datum(), x = 220 + i * 90, pull = fg * (1 - gl) * Math.max(0, 1 - Math.abs(x - 500) / 240); q.attr("d", `M ${x} 740 Q ${x + (500 - x) * 0.3 * pull} ${640 - 120 * pull} ${x + (i < 3 ? 40 : -40) * 0 + 50} 740`).attr("opacity", fi).attr("stroke", pull > 0.3 ? "#ffd23f" : "#7fb8e8").attr("stroke-dashoffset", -lt * 40); }); cross.attr("opacity", gl); };
  };

  // ---- a microwave oven: water molecules twist to the wave and the friction heats the food; metal throws sparks ----   at: wave, spin, heat, metal
  MODES.microwave = (s, k, a) => {
    s.append("rect").attr("x", 160).attr("y", 380).attr("width", 680).attr("height", 480).attr("rx", 26).attr("fill", "#2a2f35").attr("stroke", "#8d99a6").attr("stroke-width", 10); s.append("rect").attr("x", 200).attr("y", 420).attr("width", 600).attr("height", 400).attr("rx", 12).attr("fill", "#1a1f24"); const food = s.append("rect").attr("x", 360).attr("y", 680).attr("width", 280).attr("height", 100).attr("rx", 24).attr("fill", "#e8a33d");
    const mols = Array.from({ length: 10 }, (_, i) => { const g2 = s.append("g").datum(i); g2.append("circle").attr("r", 14).attr("fill", "#e23b2e"); g2.append("circle").attr("cx", -16).attr("cy", 14).attr("r", 8).attr("fill", "#fff"); g2.append("circle").attr("cx", 16).attr("cy", 14).attr("r", 8).attr("fill", "#fff"); return g2; }), waves = [0, 1, 2].map((i) => s.append("path").attr("fill", "none").attr("stroke", "#7fb8e8").attr("stroke-width", 7).attr("opacity", 0).datum(i)), fork = s.append("text").attr("x", 700).attr("y", 760).attr("font-size", 100).attr("opacity", 0).text("🍴"), spark = dots(s, 10, "#ffd23f", 8, 2), heat = Array.from({ length: 4 }, (_, i) => s.append("path").attr("fill", "none").attr("stroke", "#ff7a3c").attr("stroke-width", 8).attr("stroke-linecap", "round").attr("opacity", 0).datum(i));
    return (lt, f, d, S) => { const wa = S("wave", 0.05), sp = S("spin", 0.08), he = S("heat", 0.08), me = S("metal", 0.08);
      waves.forEach((q) => { const u = (lt * 0.7 + q.datum() / 3) % 1; q.attr("d", `M 220 ${480 + u * 160} q 40 -40 80 0 t 80 0 t 80 0 t 80 0 t 80 0 t 80 0`).attr("opacity", wa * (1 - u) * 0.9); });
      mols.forEach((g2) => { const i = g2.datum(); g2.attr("transform", `translate(${380 + (i % 5) * 60},${700 + Math.floor(i / 5) * 50}) rotate(${sp * lt * 400 + i * 40})`).attr("opacity", sp); }); food.attr("fill", d3.interpolateRgb("#e8a33d", "#e86a2a")(he)); heat.forEach((q) => { const i = q.datum(), u = (lt * 0.6 + i / 4) % 1; q.attr("d", `M ${400 + i * 70} ${660 - u * 100} q 12 -16 0 -32`).attr("opacity", he * (1 - u)); });
      fork.attr("opacity", me); spark.forEach((q, i) => { const u = (lt * 2 + rnd(i)) % 1; q.attr("cx", 700 + (rnd(i + 2) - 0.5) * 80 * u).attr("cy", 740 - u * 100).attr("opacity", me * (1 - u)); }); };
  };

  // ---- laterite: soft when cut from the ground, it hardens as the water leaves and the iron oxides set ----   at: cut, air, harden
  MODES.laterite = (s, k, a) => {
    s.append("rect").attr("x", -400).attr("y", 600).attr("width", 1800).attr("height", 500).attr("fill", k.lg("g", [[0, "#9a6f45"], [1, "#5a3e24"]])); const blk = s.append("rect").attr("width", 300).attr("height", 200).attr("rx", 10).attr("stroke", "#4a2a17").attr("stroke-width", 8), dr = dots(s, 14, "#4fb8e8", 9, 3), air = Array.from({ length: 5 }, (_, i) => s.append("path").attr("fill", "none").attr("stroke", "#fff").attr("stroke-width", 8).attr("stroke-linecap", "round").attr("opacity", 0).datum(i)), lab = s.append("text").attr("x", 500).attr("y", 340).attr("text-anchor", "middle").attr("font-size", 70).attr("font-weight", 800).attr("fill", "#2a1a10");
    return (lt, f, d, S) => { const cu = S("cut", 0.08), ai = S("air", 0.1), ha = S("harden", 0.2), y = lerp(640, 440, E.out(cu)) + 0, x = lerp(480, 350, E.out(cu));
      blk.attr("x", 350).attr("y", cu > 0 ? y : 640).attr("fill", d3.interpolateRgb("#c86a4a", "#7a3a22")(ha)).attr("opacity", 1); lab.text(ha > 0.6 ? "കല്ലുപോലെ കട്ടി" : cu > 0.5 ? "വെട്ടുമ്പോൾ മൃദുവായ" : "");
      air.forEach((q) => { const i = q.datum(), u = (lt * 0.5 + i / 5) % 1; q.attr("d", `M ${200 + u * 200} ${480 + i * 30} l 80 0`).attr("opacity", ai * (1 - u)); }); dr.forEach((q, i) => { const u = (lt * 0.5 + rnd(i)) % 1; q.attr("cx", 380 + rnd(i + 2) * 240).attr("cy", 560 - u * 160).attr("opacity", ai * (1 - ha) * (1 - u)); }); };
  };

  // ---- a clay pot: water seeps through tiny pores, evaporates, and takes heat from the pot ----   at: pores, seep, evap, cool
  MODES.matka = (s, k, a) => {
    s.append("path").attr("d", "M 380 440 Q 300 520 290 660 Q 290 860 500 880 Q 710 860 710 660 Q 700 520 620 440 Z").attr("fill", "#c8802f").attr("stroke", "#7b4a2b").attr("stroke-width", 10); const wat = s.append("path").attr("d", "M 320 560 Q 500 540 680 560 Q 700 700 680 780 Q 640 850 500 856 Q 360 850 320 780 Q 300 700 320 560 Z").attr("fill", "#4fb8e8").attr("opacity", 0.85), pores = dots(s, 18, "#4a2a17", 4, 2), seep = dots(s, 20, "#4fb8e8", 7, 4), ev = Array.from({ length: 6 }, (_, i) => s.append("path").attr("fill", "none").attr("stroke", "#9fd8f5").attr("stroke-width", 8).attr("stroke-linecap", "round").attr("opacity", 0).datum(i)), th = M.chayaIcon(s, "thermo", 900, 640, 180).attr("opacity", 0);
    return (lt, f, d, S) => { const po = S("pores", 0.05), se = S("seep", 0.08), ev2 = S("evap", 0.08), co = S("cool", 0.1);
      pores.forEach((q, i) => { const an = (i / 18) * Math.PI * 2, rx = 210, ry = 210; q.attr("cx", 500 + Math.cos(an) * 214).attr("cy", 680 + Math.sin(an) * 190).attr("opacity", po); }); seep.forEach((q, i) => { const an = (i / 20) * Math.PI * 2, u = (lt * 0.4 + rnd(i)) % 1; q.attr("cx", 500 + Math.cos(an) * (170 + u * 80)).attr("cy", 680 + Math.sin(an) * (150 + u * 70)).attr("opacity", se * (1 - u)); });
      ev.forEach((q) => { const i = q.datum(), u = (lt * 0.5 + i / 6) % 1, x = 330 + i * 68; q.attr("d", `M ${x} ${420 - u * 120} q 14 -20 0 -40`).attr("opacity", ev2 * (1 - u)); }); wat.attr("fill", d3.interpolateRgb("#4fb8e8", "#9fe0f8")(co)); th.attr("opacity", co).attr("transform", `translate(900,640) scale(1.8)`); };
  };

  // ---- Aranmula mirror vs a glass mirror: a glass mirror reflects from the back, giving a faint second image; the metal one reflects from its surface ----   at: glass, double, metal
  MODES.aranmula = (s, k, a) => {
    const gl = s.append("g").attr("transform", "translate(260,620)"); gl.append("rect").attr("x", -40).attr("y", -200).attr("width", 80).attr("height", 400).attr("fill", "#bfe3f6").attr("stroke", "#5e6b78").attr("stroke-width", 6); gl.append("rect").attr("x", 30).attr("y", -200).attr("width", 14).attr("height", 400).attr("fill", "#c9cfd4");
    const mt = s.append("g").attr("transform", "translate(740,620)"); mt.append("rect").attr("x", 20).attr("y", -200).attr("width", 28).attr("height", 400).attr("fill", "#d9b25a").attr("stroke", "#7b5a1f").attr("stroke-width", 6);
    const r1 = s.append("path").attr("fill", "none").attr("stroke", "#ffd23f").attr("stroke-width", 8).attr("opacity", 0), r2 = s.append("path").attr("fill", "none").attr("stroke", "#ffd23f").attr("stroke-width", 6).attr("stroke-dasharray", "10 8").attr("opacity", 0), r3 = s.append("path").attr("fill", "none").attr("stroke", "#ffd23f").attr("stroke-width", 8).attr("opacity", 0), lb1 = s.append("text").attr("x", 260).attr("y", 920).attr("text-anchor", "middle").attr("font-size", 44).attr("font-weight", 800).attr("fill", "#2a1a10").attr("opacity", 0).text("ഗ്ലാസ് കണ്ണാടി"), lb2 = s.append("text").attr("x", 740).attr("y", 920).attr("text-anchor", "middle").attr("font-size", 44).attr("font-weight", 800).attr("fill", "#2a1a10").attr("opacity", 0).text("ആറന്മുള കണ്ണാടി");
    return (lt, f, d, S) => { const g2 = S("glass", 0.06), dbl = S("double", 0.08), me = S("metal", 0.08);
      r1.attr("d", "M 80 420 L 285 560 L 80 700").attr("opacity", g2); r2.attr("d", "M 80 430 L 218 560 L 80 690").attr("opacity", dbl * 0.9); r3.attr("d", "M 560 420 L 748 560 L 560 700").attr("opacity", me); lb1.attr("opacity", g2); lb2.attr("opacity", me); };
  };

  // ---- coir: husk soaked, beaten into fibres, twisted into rope ----   at: soak, beat, twist
  MODES.coir = (s, k, a) => {
    s.append("rect").attr("x", -400).attr("y", 760).attr("width", 1800).attr("height", 400).attr("fill", k.lg("w", [[0, "#3a90b8"], [1, "#1a5a7a"]])); const husk = M.chayaIcon(s, "coconut", 300, 620, 240), fibres = Array.from({ length: 14 }, (_, i) => s.append("path").attr("fill", "none").attr("stroke", "#a8774a").attr("stroke-width", 6).attr("stroke-linecap", "round").attr("opacity", 0).datum(i)), rope = s.append("path").attr("fill", "none").attr("stroke", "#8a5a36").attr("stroke-width", 36).attr("stroke-linecap", "round").attr("opacity", 0), strands = s.append("path").attr("fill", "none").attr("stroke", "#c9a064").attr("stroke-width", 8).attr("stroke-dasharray", "14 14").attr("opacity", 0), bub = dots(s, 12, "#fff", 8, 3);
    return (lt, f, d, S) => { const so = S("soak", 0.05), be = S("beat", 0.1), tw = S("twist", 0.1); husk.attr("transform", `translate(300,${620 + 120 * so}) scale(2.3)`).attr("opacity", 1 - be * 0.8); bub.forEach((q, i) => { const u = (lt * 0.4 + rnd(i)) % 1; q.attr("cx", 220 + rnd(i + 2) * 160).attr("cy", 880 - u * 160).attr("opacity", so * (1 - be) * (1 - u)); });
      fibres.forEach((q) => { const i = q.datum(); q.attr("d", `M ${420 + i * 8} ${560 + i * 10} q 140 ${(i - 7) * 8} 280 ${(i - 7) * 5}`).attr("opacity", be * (1 - tw)); }); rope.attr("d", "M 480 760 Q 640 700 800 760 T 1100 760").attr("opacity", tw); strands.attr("d", "M 480 760 Q 640 700 800 760 T 1100 760").attr("stroke-dashoffset", -lt * 20).attr("opacity", tw); };
  };

  // ---- a tiled roof: rain runs off, the Sun heats the tiles, hot air escapes through the gaps ----   at: rain, heat, air
  MODES.tileroof = (s, k, a) => {
    s.append("rect").attr("x", 240).attr("y", 600).attr("width", 520).attr("height", 280).attr("fill", "#f1dcc0").attr("stroke", "#a89878").attr("stroke-width", 6); const roof = s.append("path").attr("d", "M 180 610 L 500 330 L 820 610 Z").attr("fill", "#c8442f").attr("stroke", "#7b2a1c").attr("stroke-width", 8); for (let i = 1; i < 6; i++) s.append("line").attr("x1", 180 + i * 26).attr("y1", 610 - i * 46).attr("x2", 820 - i * 26).attr("y2", 610 - i * 46).attr("stroke", "#7b2a1c").attr("stroke-width", 3);
    const rain = dots(s, 24, "#4aa3d8", 6, 3), sun = M.chayaIcon(s, "sun", 880, 200, 180).attr("opacity", 0), hot = Array.from({ length: 5 }, (_, i) => s.append("path").attr("fill", "none").attr("stroke", "#ff7a3c").attr("stroke-width", 9).attr("stroke-linecap", "round").attr("opacity", 0).datum(i)), air = Array.from({ length: 4 }, (_, i) => s.append("path").attr("fill", "none").attr("stroke", "#7fb8e8").attr("stroke-width", 9).attr("stroke-linecap", "round").attr("opacity", 0).datum(i));
    return (lt, f, d, S) => { const ra = S("rain", 0.05), he = S("heat", 0.08), ai = S("air", 0.08);
      rain.forEach((q, i) => { const u = (lt * 0.8 + rnd(i)) % 1, x = 250 + rnd(i + 2) * 500, roofY = x < 500 ? 610 - (x - 180) * 0.875 : 610 - (820 - x) * 0.875; q.attr("cx", x + (x < 500 ? -u * 70 : u * 70)).attr("cy", lerp(120, 870, u)).attr("opacity", ra * 0.8); }); sun.attr("opacity", he).attr("transform", "translate(880,200) scale(1.8)");
      hot.forEach((q) => { const i = q.datum(), u = (lt * 0.5 + i / 5) % 1; q.attr("d", `M ${380 + i * 60} ${620 - u * 200} q 14 -20 0 -40`).attr("opacity", ai * (1 - u)); }); air.forEach((q) => { const i = q.datum(), u = (lt * 0.5 + i / 4) % 1; q.attr("d", `M ${130 + u * 160} ${700 - i * 36} l 70 0`).attr("opacity", ai * (1 - Math.abs(u - 0.5) * 2)); }); };
  };

  // ---- copper ions damage bacteria slowly; boiling is still needed ----   at: water, ions, kill, boil
  MODES.copper = (s, k, a) => {
    s.append("path").attr("d", "M 320 440 Q 280 520 280 680 Q 290 860 500 880 Q 710 860 720 680 Q 720 520 680 440 Z").attr("fill", "#c8803a").attr("stroke", "#7b4a1f").attr("stroke-width", 10); s.append("path").attr("d", "M 330 540 Q 500 520 670 540 Q 700 700 650 820 Q 500 850 350 820 Q 300 700 330 540 Z").attr("fill", "#bfe3f6").attr("opacity", 0.85);
    const bact = Array.from({ length: 8 }, (_, i) => s.append("ellipse").attr("rx", 22).attr("ry", 12).attr("fill", "#d05a5a").attr("opacity", 0).datum(i)), ions = dots(s, 20, "#e8832e", 7, 2), kettle = M.chayaIcon(s, "cup", 900, 700, 160).attr("opacity", 0), steam = Array.from({ length: 3 }, (_, i) => s.append("path").attr("fill", "none").attr("stroke", "#fff").attr("stroke-width", 7).attr("stroke-linecap", "round").attr("opacity", 0).datum(i));
    return (lt, f, d, S) => { const wa = S("water", 0.05), io = S("ions", 0.08), ki = S("kill", 0.12), bo = S("boil", 0.08);
      bact.forEach((q) => { const i = q.datum(); q.attr("cx", 400 + (i % 4) * 70 + Math.sin(lt + i) * 14).attr("cy", 640 + Math.floor(i / 4) * 80 + Math.cos(lt * 1.3 + i) * 10).attr("opacity", wa * (1 - ki * (i < 6 ? 1 : 0.3))).attr("fill", d3.interpolateRgb("#d05a5a", "#7a5a5a")(ki)); });
      ions.forEach((q, i) => { const u = (lt * 0.4 + rnd(i)) % 1, an = rnd(i + 3) * Math.PI * 2; q.attr("cx", 500 + Math.cos(an) * 190 * (1 - u * 0.6)).attr("cy", 700 + Math.sin(an) * 140 * (1 - u * 0.6)).attr("opacity", io * (1 - u * 0.5)); });
      kettle.attr("opacity", bo).attr("transform", "translate(900,700) scale(1.8)"); steam.forEach((q) => { const i = q.datum(), u = (lt * 0.6 + i / 3) % 1; q.attr("d", `M ${860 + i * 40} ${620 - u * 100} q 12 -18 0 -36`).attr("opacity", bo * (1 - u)); }); };
  };

  // ---- why the sea is salty: rain dissolves rocks, rivers carry the salts, water evaporates and salt stays ----   at: rain, rivers, evap, salt
  MODES.saltysea = (s, k, a) => {
    s.append("rect").attr("x", 650).attr("y", 640).attr("width", 900).attr("height", 400).attr("fill", k.lg("w", [[0, "#2a8fc0"], [1, "#146a95"]])); s.append("path").attr("d", "M -300 760 L 100 420 L 260 560 L 450 360 L 650 640 L 650 1000 L -300 1000 Z").attr("fill", "#8a8f94"); const cl = M.chayaIcon(s, "cloudDark", 200, 240, 260).attr("opacity", 0), rain = dots(s, 20, "#4aa3d8", 6, 3), river = s.append("path").attr("d", "M 450 380 Q 480 520 560 600 Q 620 640 700 650").attr("fill", "none").attr("stroke", "#4fb8e8").attr("stroke-width", 16).attr("stroke-linecap", "round").attr("stroke-dasharray", "20 14").attr("opacity", 0), salts = dots(s, 24, "#fff", 7, 2), evap = Array.from({ length: 5 }, (_, i) => s.append("path").attr("fill", "none").attr("stroke", "#9fd8f5").attr("stroke-width", 8).attr("stroke-linecap", "round").attr("opacity", 0).datum(i)), lab = s.append("text").attr("x", 1100).attr("y", 920).attr("text-anchor", "middle").attr("font-size", 60).attr("font-weight", 800).attr("fill", "#fff6e2").attr("opacity", 0).text("1 kg ൽ ≈ 35 g");
    return (lt, f, d, S) => { const ra = S("rain", 0.05), ri = S("rivers", 0.08), ev = S("evap", 0.08), sa = S("salt", 0.1); cl.attr("opacity", ra).attr("transform", "translate(200,240) scale(2.6)"); rain.forEach((q, i) => { const u = (lt * 0.8 + rnd(i)) % 1; q.attr("cx", 60 + rnd(i + 2) * 320 - u * 20).attr("cy", 300 + u * 300).attr("opacity", ra * (1 - u)); }); river.attr("opacity", ri).attr("stroke-dashoffset", -lt * 50);
      salts.forEach((q, i) => { const u = (lt * 0.3 + rnd(i)) % 1; q.attr("cx", lerp(300 + rnd(i) * 200, 700 + rnd(i + 3) * 700, clamp(sa * 3 - u * 0.0 * 0 + ri))).attr("cy", lerp(500, 820 + rnd(i + 4) * 120, clamp(ri + sa))).attr("opacity", ri * 0.85); }); evap.forEach((q) => { const i = q.datum(), u = (lt * 0.5 + i / 5) % 1; q.attr("d", `M ${800 + i * 120} ${620 - u * 150} q 14 -20 0 -40`).attr("opacity", ev * (1 - u)); }); lab.attr("opacity", sa); };
  };

  // ---- the blue sea: water absorbs red first, then green, and returns blue ----   at: ray, red, blue
  MODES.bluesea = (s, k, a) => {
    s.append("rect").attr("x", -1400).attr("y", 200).attr("width", 3800).attr("height", 1000).attr("fill", k.lg("w", [[0, "#7fd0f0"], [0.4, "#2a8fc0"], [1, "#0a2a4a"]])); s.append("rect").attr("x", -1400).attr("y", -400).attr("width", 3800).attr("height", 600).attr("fill", "#cfe8f4"); const sun = M.chayaIcon(s, "sun", 500, 90, 140);
    const rays = [["#e23b2e", 320, 0], ["#f6d12a", 520, 1], ["#2d8fd0", 900, 2]].map(([col, depth, i]) => s.append("path").attr("fill", "none").attr("stroke", col).attr("stroke-width", 14).attr("stroke-linecap", "round").attr("opacity", 0).datum([col, depth, i])), back = dots(s, 14, "#2d8fd0", 10, 3);
    return (lt, f, d, S) => { const ra = S("ray", 0.05), re = S("red", 0.08), bl = S("blue", 0.1); sun.attr("transform", "translate(500,90) scale(1.4)");
      rays.forEach((q) => { const [col, depth, i] = q.datum(), x = 360 + i * 140, len = i === 0 ? 120 + 200 * ra * (1 - re) + 0 : i === 1 ? 260 : 540 + 120 * bl; q.attr("d", `M ${x} 200 L ${x + 30} ${200 + Math.min(depth - 200, i === 0 ? lerp(60, 160, re) : len) }`).attr("opacity", ra); });
      back.forEach((q, i) => { const u = (lt * 0.5 + rnd(i)) % 1; q.attr("cx", 620 + rnd(i + 2) * 200 - u * 340).attr("cy", 700 - u * 460).attr("opacity", bl * (1 - u)); }); };
  };

  // ---- black sand: heavy dark minerals from the hills stay on the beach while the waves carry the light sand away ----   at: mountain, river, wave, heavy
  MODES.blacksand = (s, k, a) => {
    s.append("path").attr("d", "M -400 700 L -100 320 L 120 520 L 300 380 L 480 640 L 480 1000 L -400 1000 Z").attr("fill", "#8a8f94"); s.append("rect").attr("x", 480).attr("y", 700).attr("width", 1100).attr("height", 400).attr("fill", k.lg("w", [[0, "#2a8fc0"], [1, "#146a95"]])); s.append("path").attr("d", "M 480 700 L 700 780 L 1000 1000 L 480 1000 Z").attr("fill", "#d9c48a");
    const grains = Array.from({ length: 40 }, (_, i) => s.append("circle").attr("r", 6 + rnd(i) * 4).attr("fill", i % 3 === 0 ? "#2a2a30" : "#e8d8a0").attr("opacity", 0).datum(i)), waves = Array.from({ length: 3 }, (_, i) => s.append("path").attr("fill", "none").attr("stroke", "#e9f8ff").attr("stroke-width", 8).attr("opacity", 0).datum(i)), lab = s.append("text").attr("x", 800).attr("y", 960).attr("text-anchor", "middle").attr("font-size", 56).attr("font-weight", 800).attr("fill", "#2a1a10").attr("opacity", 0).text("ഭാരമുള്ളവ ബാക്കി");
    return (lt, f, d, S) => { const mo = S("mountain", 0.05), ri = S("river", 0.08), wa = S("wave", 0.08), he = S("heavy", 0.1);
      grains.forEach((q) => { const i = q.datum(), dark = i % 3 === 0, u = (lt * 0.3 + rnd(i)) % 1, tx = lerp(160 + rnd(i) * 200, 700 + rnd(i + 3) * 300, clamp(ri * 1.2 + wa * 0)), ty = lerp(560, 800 + rnd(i + 4) * 180, ri); let x = tx, y = ty; if (wa > 0 && !dark) { x = tx + (wa * (lt * 80 + i * 40)) % 700; y = ty - 30 * Math.sin(x * 0.02); } q.attr("cx", x).attr("cy", y).attr("opacity", mo * (dark || he < 0.9 ? 0.95 : 0.15) * (!dark && wa > 0.8 ? 0 : 1)); });
      waves.forEach((q) => { const i = q.datum(), u = (lt * 0.6 + i / 3) % 1; q.attr("d", `M ${1300 - u * 700} ${760 + i * 40} q 30 -30 60 0 t 60 0`).attr("opacity", wa * (1 - u)); }); lab.attr("opacity", he); };
  };

  // ---- fish gills: water in at the mouth, over the gill filaments, oxygen into the blood ----   at: mouth, gill, oxygen
  MODES.fishgill = (s, k, a) => {
    s.append("rect").attr("x", -400).attr("y", 300).attr("width", 1800).attr("height", 800).attr("fill", k.lg("w", [[0, "#7fd0f0"], [1, "#2a8fc0"]])).attr("opacity", 0.5); const fish = s.append("g").attr("transform", "translate(500,600)"); fish.append("path").attr("d", "M -300 0 Q -200 -140 100 -120 Q 260 -100 340 0 Q 260 100 100 120 Q -200 140 -300 0 Z").attr("fill", "#e8a33d").attr("stroke", "#7b4a1f").attr("stroke-width", 8); fish.append("path").attr("d", "M 340 0 L 440 -90 L 440 90 Z").attr("fill", "#e8832e"); fish.append("circle").attr("cx", -220).attr("cy", -30).attr("r", 18).attr("fill", "#2a1a10");
    const gills = Array.from({ length: 6 }, (_, i) => fish.append("path").attr("d", `M ${-40 + i * 22} -90 Q ${-30 + i * 22} 0 ${-40 + i * 22} 90`).attr("fill", "none").attr("stroke", "#d8323a").attr("stroke-width", 12).attr("stroke-linecap", "round").attr("opacity", 0.9)), water = dots(s, 20, "#bfe8fb", 8, 2), o2 = dots(s, 14, "#4aa8ff", 8, 5), cap = s.append("text").attr("x", 500).attr("y", 900).attr("text-anchor", "middle").attr("font-size", 54).attr("font-weight", 800).attr("fill", "#fff6e2").attr("opacity", 0).text("ഓക്സിജൻ → രക്തത്തിലേക്ക്");
    return (lt, f, d, S) => { const mo = S("mouth", 0.05), gi = S("gill", 0.08), ox = S("oxygen", 0.1);
      water.forEach((q, i) => { const u = (lt * 0.5 + rnd(i)) % 1, x = lerp(100, 700, u); q.attr("cx", x).attr("cy", 600 + (rnd(i + 2) - 0.5) * 80 + Math.sin(u * 6) * 14).attr("opacity", mo * 0.8); }); o2.forEach((q, i) => { const u = (lt * 0.6 + rnd(i)) % 1; q.attr("cx", lerp(420 + rnd(i + 3) * 60, 480 + (i % 6) * 22 - 40, u)).attr("cy", lerp(600, 560 + (rnd(i) - 0.5) * 120, u)).attr("opacity", gi * (1 - ox * 0.0) * (1 - u * 0.2)).attr("fill", u > 0.6 && ox > 0 ? "#d8323a" : "#4aa8ff"); }); cap.attr("opacity", ox); };
  };

  // ---- floating: salt water is denser, so it pushes up harder ----   at: fresh, salt, force
  MODES.floating = (s, k, a) => {
    const tank = (x, col) => s.append("rect").attr("x", x).attr("y", 520).attr("width", 360).attr("height", 400).attr("rx", 20).attr("fill", col).attr("opacity", 0.65).attr("stroke", "#5e6b78").attr("stroke-width", 8); tank(140, "#9fd8f0"); tank(520, "#2a8fc0"); s.append("text").attr("x", 320).attr("y", 980).attr("text-anchor", "middle").attr("font-size", 44).attr("font-weight", 800).attr("fill", "#2a1a10").text("ശുദ്ധജലം"); s.append("text").attr("x", 700).attr("y", 980).attr("text-anchor", "middle").attr("font-size", 44).attr("font-weight", 800).attr("fill", "#2a1a10").text("കടൽവെള്ളം");
    const b1 = s.append("circle").attr("cx", 320).attr("r", 56).attr("fill", "#e8a33d").attr("stroke", "#7b4a1f").attr("stroke-width", 6), b2 = s.append("circle").attr("cx", 700).attr("r", 56).attr("fill", "#e8a33d").attr("stroke", "#7b4a1f").attr("stroke-width", 6), ar = s.append("path").attr("fill", "none").attr("stroke", "#2f7d4f").attr("stroke-width", 12).attr("stroke-linecap", "round").attr("opacity", 0), salt = dots(s, 20, "#fff", 6, 3);
    return (lt, f, d, S) => { const fr = S("fresh", 0.08), sa = S("salt", 0.08), fo = S("force", 0.08);
      b1.attr("cy", lerp(300, 800, E.out(fr))).attr("opacity", 1); b2.attr("cy", lerp(300, 536, E.out(sa))).attr("opacity", sa > 0 ? 1 : 0); ar.attr("d", "M 700 650 L 700 480 M 670 520 L 700 480 L 730 520").attr("opacity", fo); salt.forEach((q, i) => q.attr("cx", 540 + rnd(i) * 320).attr("cy", 560 + rnd(i + 3) * 340 + Math.sin(lt + i) * 6).attr("opacity", sa * 0.7)); };
  };

  // ================= the scene: background + a mode + tags =================
  K.lab = (g, p, c) => {
    const id = c.id + rid(), k = M.setKit(g, c, id), s = k.set, a = p.at || {};
    BG(s, k, p.bg || (p.mode === "firefly" ? "night" : p.mode === "petrichor" ? "sky" : "kitchen"));
    const mode = (MODES[p.mode] || (() => () => {}))(s, k, a, p), tags = (p.tags || []).map((t) => ({ t, pg: k.pill2(t.x, t.y, t.ml, t.en, t.col || "#c8442f") }));
    const DEF = { qr: [500, 620, 1.45], phoneheat: [560, 560, 1.4], induction: [500, 720, 1.7], gps: [550, 600, 1.2], touchscreen: [500, 640, 1.7], microwave: [500, 620, 1.5], laterite: [500, 640, 1.8], matka: [550, 660, 1.6], aranmula: [500, 620, 1.5], coir: [650, 700, 1.6], tileroof: [550, 560, 1.5], copper: [600, 660, 1.5], saltysea: [550, 640, 1.2], bluesea: [500, 520, 1.2], blacksand: [500, 700, 1.3], fishgill: [500, 600, 1.5], floating: [500, 640, 1.6], ghats: [650, 560, 1.15], neelakurinji: [450, 700, 1.2], kingfisher: [450, 560, 1.5], beedance: [650, 560, 1.4], bat: [500, 520, 1.5], mangrove: [500, 650, 1.5], peacock: [500, 560, 1.5], thermostat: [560, 560, 1.7], hiccup: [500, 560, 1.3], pruning: [500, 620, 1.9], goosebumps: [450, 700, 1.9], yawn: [500, 560, 1.8], soap: [500, 560, 1.7], heart: [500, 640, 1.45], pepperberry: [500, 640, 2.0], muziris: [550, 520, 1.1], receptor: [500, 520, 1.9], turmeric: [500, 640, 1.6], puttu: [500, 660, 1.8], pappadam: [500, 640, 1.9], cardamom: [500, 580, 1.6], pickle: [500, 640, 1.7], seabreeze: [500, 600, 1.2], humid: [500, 560, 1.3], hail: [500, 560, 1.3], cloudweight: [500, 580, 1.3], raindropspeed: [500, 400, 1.2], bluesky: [500, 520, 1.1], twinkle: [500, 500, 1.2], moonillusion: [500, 480, 1.3], ringeclipse: [500, 500, 1.25], iss: [500, 400, 1.2], moonface: [500, 560, 1.3], sunshadow: [500, 440, 1.1], tealeaf: [500, 560, 1.5], adenosine: [500, 560, 1.5], steep: [500, 650, 1.8], ferment: [500, 650, 1.8], cooker: [500, 640, 1.7], onion: [620, 600, 1.4], oilsolid: [550, 540, 1.5], tide: [800, 560, 1.0], mudbank: [550, 560, 1.4], sweat: [500, 580, 1.5], snakeboat: [40, 540, 1.1], coconutwater: [620, 570, 1.5], seismic: [510, 640, 1.4], petrichor: [500, 560, 1.5], firefly: [700, 600, 1.35], goli: [500, 560, 1.9], cassette: [520, 640, 1.5], osmosis: [450, 640, 1.7], lamp: [500, 500, 1.9] }[p.mode] || [500, 540, 1.2], tall = c.stage.h > c.stage.w;
    const move = k.camMover(p.cams || [{ at: 0, x: DEF[0], y: DEF[1], z: DEF[2] * (tall ? 0.8 : 1) }]);
    return (lt, d) => { const f = lt / d; move(f, d); mode(lt, f, d, (name, w = 0.1) => prog(f, at(a, name), w));
      tags.forEach(({ t, pg }, i) => { pop(pg, t.x, t.y, f, d, t.at ?? 9); const nxt = tags[i + 1] ? tags[i + 1].t.at : 9; pg.attr("opacity", +pg.attr("opacity") * (1 - prog(f, Math.min((t.at ?? 9) + 0.2, nxt + 0.02), 0.03))); }); };
  };
})();
