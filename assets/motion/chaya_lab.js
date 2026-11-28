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

  // ================= the scene: background + a mode + tags =================
  K.lab = (g, p, c) => {
    const id = c.id + rid(), k = M.setKit(g, c, id), s = k.set, a = p.at || {};
    BG(s, k, p.bg || (p.mode === "firefly" ? "night" : p.mode === "petrichor" ? "sky" : "kitchen"));
    const mode = (MODES[p.mode] || (() => () => {}))(s, k, a), tags = (p.tags || []).map((t) => ({ t, pg: k.pill2(t.x, t.y, t.ml, t.en, t.col || "#c8442f") }));
    const DEF = { petrichor: [500, 560, 1.5], firefly: [700, 600, 1.35], goli: [500, 560, 1.9], cassette: [520, 640, 1.5], osmosis: [450, 640, 1.7], lamp: [500, 500, 1.9] }[p.mode] || [500, 540, 1.2], tall = c.stage.h > c.stage.w;
    const move = k.camMover(p.cams || [{ at: 0, x: DEF[0], y: DEF[1], z: DEF[2] * (tall ? 0.62 : 1) }]);
    return (lt, d) => { const f = lt / d; move(f, d); mode(lt, f, d, (name, w = 0.1) => prog(f, at(a, name), w));
      tags.forEach(({ t, pg }, i) => { pop(pg, t.x, t.y, f, d, t.at ?? 9); const nxt = tags[i + 1] ? tags[i + 1].t.at : 9; pg.attr("opacity", +pg.attr("opacity") * (1 - prog(f, Math.min((t.at ?? 9) + 0.2, nxt + 0.02), 0.03))); }); };
  };
})();
