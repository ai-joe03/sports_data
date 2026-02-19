"""Build the self-contained index.html with all seasons data embedded."""
import json

data = json.load(open("data/all_seasons.json"))
data_js = json.dumps(data, separators=(",", ":"))

counts_data = json.load(open("data/pl_setpiece_counts.json"))
counts_js = json.dumps(counts_data, separators=(",", ":"))

html = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>EPL Set Piece xG</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Lora:wght@400;600;700&family=Open+Sans:wght@400;600;700&display=swap" rel="stylesheet">
  <script src="https://d3js.org/d3.v7.min.js"></script>
  <style>
    :root {
      --bg: #FFFBFF;
      --surface: #ffffff;
      --border: #d0d7de;
      --text: #020202;
      --text-muted: #555555;
      --accent: #FBB13D;
      --accent-deep: #1B149F;
    }
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      background: var(--bg);
      color: var(--text);
      font-family: 'Open Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
      padding: 24px;
      min-height: 100vh;
    }
    header { max-width: 1200px; margin: 0 auto 32px; }
    header h1 { font-family: 'Lora', Georgia, serif; font-size: 28px; font-weight: 700; margin-bottom: 6px; }
    header h1 span { color: var(--accent-deep); }
    header p { color: var(--text-muted); font-size: 14px; line-height: 1.5; }

    /* Controls row */
    .controls {
      max-width: 1200px;
      margin: 0 auto 20px;
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
      align-items: center;
    }
    .controls select {
      background: var(--surface);
      border: 1px solid var(--border);
      color: var(--text);
      padding: 6px 10px;
      border-radius: 6px;
      font-size: 13px;
      cursor: pointer;
    }
    .controls button {
      background: var(--surface);
      border: 1px solid var(--border);
      color: var(--text);
      padding: 6px 14px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 13px;
      transition: all 0.15s;
    }
    .controls button:hover { border-color: var(--accent-deep); color: var(--accent-deep); }
    .controls button.active {
      background: var(--accent-deep);
      color: #fff;
      border-color: var(--accent-deep);
      font-weight: 600;
    }
    .controls .label {
      color: var(--text-muted);
      font-size: 13px;
      margin-right: 4px;
    }
    .controls .separator {
      width: 1px;
      height: 24px;
      background: var(--border);
    }

    /* Tab bar */
    .tab-bar {
      max-width: 1200px;
      margin: 0 auto 24px;
      display: flex;
      gap: 0;
      border-bottom: 2px solid var(--border);
    }
    .tab-bar button {
      background: none;
      border: none;
      border-bottom: 3px solid transparent;
      margin-bottom: -2px;
      padding: 10px 24px;
      font-family: 'Lora', Georgia, serif;
      font-size: 15px;
      font-weight: 600;
      color: var(--text-muted);
      cursor: pointer;
      transition: all 0.15s;
    }
    .tab-bar button:hover { color: var(--text); }
    .tab-bar button.active {
      color: var(--accent-deep);
      border-bottom-color: var(--accent-deep);
    }
    .tab-content { display: none; }
    .tab-content.active { display: block; }

    /* Chart container */
    .chart-container {
      max-width: 1200px;
      margin: 0 auto;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 24px 16px 16px;
      overflow-x: auto;
    }
    svg text { fill: var(--text); }
    .axis path, .axis line { stroke: var(--border); }
    .axis text { fill: var(--text-muted); font-size: 14px; }
    .grid line { stroke: var(--border); stroke-opacity: 0.4; stroke-dasharray: 2,3; }
    .grid path { display: none; }

    /* Tooltip */
    .tooltip {
      position: fixed;
      pointer-events: none;
      background: #ffffff;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 12px 16px;
      font-size: 13px;
      line-height: 1.6;
      box-shadow: 0 8px 24px rgba(0,0,0,.12);
      z-index: 100;
      opacity: 0;
      transition: opacity 0.15s;
      max-width: 360px;
    }
    .tooltip .tt-team { font-weight: 700; font-size: 15px; margin-bottom: 6px; }
    .tooltip .tt-row { display: flex; justify-content: space-between; gap: 16px; }
    .tooltip .tt-label { color: var(--text-muted); }
    .tooltip .tt-val { font-weight: 600; font-variant-numeric: tabular-nums; }
    .tooltip .tt-total { border-top: 1px solid var(--border); margin-top: 6px; padding-top: 6px; }

    .section-title {
      max-width: 1200px;
      margin: 40px auto 16px;
      font-family: 'Lora', Georgia, serif;
      font-size: 22px;
      font-weight: 600;
    }
    .section-subtitle {
      max-width: 1200px;
      margin: -10px auto 16px;
      font-size: 14px;
      color: var(--text-muted);
    }

    .no-data-msg {
      max-width: 1200px;
      margin: 60px auto;
      text-align: center;
      color: var(--text-muted);
      font-size: 15px;
      line-height: 1.8;
    }
    .no-data-msg code {
      background: var(--surface);
      border: 1px solid var(--border);
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 13px;
    }

    footer {
      max-width: 1200px;
      margin: 40px auto 0;
      padding-top: 16px;
      border-top: 1px solid var(--border);
      color: var(--text-muted);
      font-size: 12px;
      line-height: 1.6;
    }
    footer a { color: var(--accent-deep); text-decoration: none; }
  </style>
</head>
<body>

<header>
  <h1>EPL Set Piece <span>xG</span></h1>
  <p>Expected goals from set pieces per Premier League team, broken down by situation type.
     xG data from <a href="https://understat.com" style="color:var(--accent-deep)">Understat</a>,
     set piece counts from the <a href="https://www.premierleague.com" style="color:var(--accent-deep)">Premier League</a>.</p>
</header>

<!-- Global: Season selector -->
<div class="controls" id="controls">
  <span class="label">Season:</span>
  <select id="season-select"></select>
</div>

<!-- Tab bar -->
<div class="tab-bar" id="tab-bar">
  <button class="active" data-tab="setpieces">Set Pieces</button>
  <button data-tab="shotzones">Shot Zones</button>
  <button data-tab="attackspeed">Attack Speed</button>
</div>

<!-- ═══════════ TAB: Set Pieces ═══════════ -->
<div class="tab-content active" id="tab-setpieces">
  <div class="controls" id="sp-filters">
    <span class="label">Show:</span>
    <button class="active" data-filter="all">All Set Pieces</button>
    <button data-filter="FromCorner">Corners</button>
    <button data-filter="SetPiece">Set Piece</button>
    <button data-filter="DirectFreekick">Direct FK</button>
    <button data-filter="Penalty">Penalties</button>
  </div>
  <h2 class="section-title" id="sp-c1-title">Total Set Piece xG Created</h2>
  <p class="section-subtitle" id="sp-c1-sub">Total expected goals created from set pieces per team</p>
  <div class="chart-container"><svg id="sp-c1"></svg></div>

  <h2 class="section-title" id="sp-c2-title">Net Set Piece xG</h2>
  <p class="section-subtitle" id="sp-c2-sub">Net xG (created − conceded)</p>
  <div class="chart-container"><svg id="sp-c2"></svg></div>

  <h2 class="section-title" id="sp-c3-title">xG per Action</h2>
  <p class="section-subtitle" id="sp-c3-sub">Expected goals generated per set piece taken</p>
  <div class="chart-container"><svg id="sp-c3"></svg></div>

  <h2 class="section-title" id="sp-c4-title">xG Allowed per Action</h2>
  <p class="section-subtitle" id="sp-c4-sub">Expected goals conceded per set piece faced</p>
  <div class="chart-container"><svg id="sp-c4"></svg></div>

  <h2 class="section-title" id="sp-c5-title">Raw Set Piece Counts</h2>
  <p class="section-subtitle" id="sp-c5-sub">Total corners, free kicks and penalties — taken vs conceded</p>
  <div class="chart-container"><svg id="sp-c5"></svg></div>
</div>

<!-- ═══════════ TAB: Shot Zones ═══════════ -->
<div class="tab-content" id="tab-shotzones">
  <div class="controls" id="sz-filters">
    <span class="label">Show:</span>
    <button class="active" data-filter="all">All Zones</button>
    <button data-filter="shotOboxTotal">Outside Box</button>
    <button data-filter="shotPenaltyArea">Penalty Area</button>
    <button data-filter="shotSixYardBox">Six-Yard Box</button>
  </div>
  <div id="sz-no-data" class="no-data-msg" style="display:none">
    <p>Shot zone data is not yet available for this season.</p>
    <p>Re-run <code>python scrape_all_seasons.py</code> to fetch shot zone breakdowns from Understat.</p>
  </div>
  <div id="sz-charts">
    <h2 class="section-title" id="sz-c1-title">Total xG Created by Shot Zone</h2>
    <p class="section-subtitle" id="sz-c1-sub">Expected goals by pitch zone</p>
    <div class="chart-container"><svg id="sz-c1"></svg></div>

    <h2 class="section-title" id="sz-c2-title">Net xG by Shot Zone</h2>
    <p class="section-subtitle" id="sz-c2-sub">Net xG (created − conceded) by zone</p>
    <div class="chart-container"><svg id="sz-c2"></svg></div>

    <h2 class="section-title" id="sz-c3-title">xG per Shot by Zone</h2>
    <p class="section-subtitle" id="sz-c3-sub">Shot quality — xG per shot taken from each zone</p>
    <div class="chart-container"><svg id="sz-c3"></svg></div>

    <h2 class="section-title" id="sz-c4-title">xG Balance by Shot Zone</h2>
    <p class="section-subtitle" id="sz-c4-sub">xG created vs xG conceded — attacking and defensive breakdown</p>
    <div class="chart-container"><svg id="sz-c4"></svg></div>

    <h2 class="section-title" id="sz-c5-title">Shot Efficiency — xG/Shot vs xGA/Shot</h2>
    <p class="section-subtitle" id="sz-c5-sub">Offensive shot quality vs defensive shot quality conceded</p>
    <div class="chart-container"><svg id="sz-c5"></svg></div>
  </div>
</div>

<!-- ═══════════ TAB: Attack Speed ═══════════ -->
<div class="tab-content" id="tab-attackspeed">
  <div class="controls" id="as-filters">
    <span class="label">Show:</span>
    <button class="active" data-filter="all">All Speeds</button>
    <button data-filter="Normal">Normal</button>
    <button data-filter="Standard">Standard</button>
    <button data-filter="Fast">Fast</button>
    <button data-filter="Slow">Slow</button>
  </div>
  <div id="as-no-data" class="no-data-msg" style="display:none">
    <p>Attack speed data is not yet available for this season.</p>
    <p>Re-run <code>python scrape_all_seasons.py</code> to fetch attack speed breakdowns from Understat.</p>
  </div>
  <div id="as-charts">
    <h2 class="section-title" id="as-c1-title">Total xG Created by Attack Speed</h2>
    <p class="section-subtitle" id="as-c1-sub">Expected goals by attack tempo</p>
    <div class="chart-container"><svg id="as-c1"></svg></div>

    <h2 class="section-title" id="as-c2-title">Net xG by Attack Speed</h2>
    <p class="section-subtitle" id="as-c2-sub">Net xG (created − conceded) by tempo</p>
    <div class="chart-container"><svg id="as-c2"></svg></div>

    <h2 class="section-title" id="as-c3-title">xG per Shot by Attack Speed</h2>
    <p class="section-subtitle" id="as-c3-sub">Shot quality — xG per shot from each attack tempo</p>
    <div class="chart-container"><svg id="as-c3"></svg></div>

    <h2 class="section-title" id="as-c4-title">xG Balance by Attack Speed</h2>
    <p class="section-subtitle" id="as-c4-sub">xG created vs xG conceded — attacking and defensive breakdown</p>
    <div class="chart-container"><svg id="as-c4"></svg></div>

    <h2 class="section-title" id="as-c5-title">Shot Efficiency — xG/Shot vs xGA/Shot</h2>
    <p class="section-subtitle" id="as-c5-sub">Offensive shot quality vs defensive shot quality conceded</p>
    <div class="chart-container"><svg id="as-c5"></svg></div>
  </div>
</div>

<div class="tooltip" id="tooltip"></div>

<footer>
  xG data via <a href="https://understat.com">understat.com</a>.
  Set piece counts via <a href="https://www.premierleague.com">premierleague.com</a>.
  Visualised with <a href="https://d3js.org">D3.js v7</a>.
</footer>

<script>
// ── Data ────────────────────────────────────────────────────────────
const ALL_DATA = """ + data_js + r""";
const PL_COUNTS = """ + counts_js + r""";

const SHORT_NAMES = {
  "Wolverhampton Wanderers": "Wolves",
  "Manchester United": "Man Utd",
  "Manchester City": "Man City",
  "Newcastle United": "Newcastle",
  "Nottingham Forest": "Nott'm Forest",
  "Crystal Palace": "C. Palace",
  "Ipswich Town": "Ipswich",
  "Sheffield United": "Sheff Utd",
  "Huddersfield": "Huddersfield",
  "Hull City": "Hull",
  "Stoke City": "Stoke",
  "West Brom": "West Brom",
};

// ── Category definitions ────────────────────────────────────────────
const SITUATIONS = [
  { key: "FromCorner",     label: "Corners",    color: "#6B6EAF" },
  { key: "SetPiece",       label: "Set Piece",  color: "#3D35C1" },
  { key: "DirectFreekick", label: "Direct FK",  color: "#4A9B6F" },
  { key: "Penalty",        label: "Penalties",  color: "#FF5A5F" },
];

const SHOT_ZONES = [
  { key: "shotOboxTotal",   label: "Outside Box",   color: "#6B6EAF" },
  { key: "shotPenaltyArea", label: "Penalty Area",  color: "#FF5A5F" },
  { key: "shotSixYardBox",  label: "Six-Yard Box",  color: "#4A9B6F" },
];

const ATTACK_SPEEDS = [
  { key: "Normal",   label: "Normal",   color: "#6B6EAF" },
  { key: "Standard", label: "Standard", color: "#4A9B6F" },
  { key: "Fast",     label: "Fast",     color: "#FF5A5F" },
  { key: "Slow",     label: "Slow",     color: "#E59500" },
];

// ── State ───────────────────────────────────────────────────────────
let activeSeason = "2025";
let activeTab = "setpieces";
const tabFilters = { setpieces: "all", shotzones: "all", attackspeed: "all" };

// ── Season dropdown ─────────────────────────────────────────────────
const seasonSelect = d3.select("#season-select");
Object.keys(ALL_DATA).sort((a, b) => +b - +a).forEach(key => {
  seasonSelect.append("option").attr("value", key).text(ALL_DATA[key].season);
});
seasonSelect.property("value", activeSeason);

function getTeams() {
  return ALL_DATA[activeSeason].teams.map(t => ({
    ...t,
    short: SHORT_NAMES[t.team] || t.team,
  }));
}

function getCountsLookup() {
  const seasonCounts = PL_COUNTS[activeSeason];
  if (!seasonCounts) return {};
  const lookup = {};
  seasonCounts.teams.forEach(t => { lookup[t.team] = t; });
  return lookup;
}

function seasonLabel() { return ALL_DATA[activeSeason].season; }

// ── Tab switching ───────────────────────────────────────────────────
d3.selectAll("#tab-bar button").on("click", function () {
  d3.selectAll("#tab-bar button").classed("active", false);
  d3.select(this).classed("active", true);
  activeTab = d3.select(this).attr("data-tab");
  d3.selectAll(".tab-content").classed("active", false);
  d3.select("#tab-" + activeTab).classed("active", true);
  redrawActiveTab();
});

// Per-tab filter wiring
["sp", "sz", "as"].forEach((prefix, idx) => {
  const tabKey = ["setpieces", "shotzones", "attackspeed"][idx];
  d3.selectAll(`#${prefix}-filters button[data-filter]`).on("click", function () {
    d3.selectAll(`#${prefix}-filters button[data-filter]`).classed("active", false);
    d3.select(this).classed("active", true);
    tabFilters[tabKey] = d3.select(this).attr("data-filter");
    redrawActiveTab();
  });
});

seasonSelect.on("change", function () {
  activeSeason = this.value;
  d3.select("header h1").html(`EPL <span>xG</span> — ${seasonLabel()}`);
  redrawActiveTab();
});

function redrawActiveTab() {
  const teams = getTeams();
  d3.select("header h1").html(`EPL <span>xG</span> — ${seasonLabel()}`);
  if (activeTab === "setpieces") redrawSetPieces(teams);
  else if (activeTab === "shotzones") redrawShotZones(teams);
  else if (activeTab === "attackspeed") redrawAttackSpeed(teams);
}

// ── Shared tooltip helpers ──────────────────────────────────────────
function moveTooltip(event) {
  const tooltip = d3.select("#tooltip");
  const pad = 16;
  let left = event.clientX + pad, top = event.clientY + pad;
  const rect = tooltip.node().getBoundingClientRect();
  if (left + rect.width > window.innerWidth - 8) left = event.clientX - rect.width - pad;
  if (top + rect.height > window.innerHeight - 8) top = event.clientY - rect.height - pad;
  tooltip.style("left", left + "px").style("top", top + "px");
}
function hideTooltip() { d3.select("#tooltip").style("opacity", 0); }

// ╔══════════════════════════════════════════════════════════════════╗
// ║  SET PIECES TAB                                                  ║
// ╚══════════════════════════════════════════════════════════════════╝
function redrawSetPieces(teams) {
  const f = tabFilters.setpieces;
  drawSpTotal(teams, f);
  drawSpNet(teams, f);
  drawSpPerAction(teams, f);
  drawSpAllowedPerAction(teams, f);
  drawSpRawCounts(teams, f);
}

// ── SP Chart 1: Total xG Created ─────────────────────────────────
function drawSpTotal(teamsRaw, filter) {
  const svg = d3.select("#sp-c1"); svg.selectAll("*").remove();
  const isAll = filter === "all";
  const cats = isAll ? SITUATIONS : SITUATIONS.filter(s => s.key === filter);
  const lbl = isAll ? "All Set Pieces" : cats[0].label;
  d3.select("#sp-c1-title").text(`Total Set Piece xG Created — ${lbl} — ${seasonLabel()}`);
  d3.select("#sp-c1-sub").text(`Total expected goals created from set pieces per team, sorted highest to lowest.`);

  const teams = [...teamsRaw].sort((a, b) => {
    return cats.reduce((s, c) => s + b[c.key].xG, 0) - cats.reduce((s, c) => s + a[c.key].xG, 0);
  });

  const margin = {top:32,right:60,bottom:40,left:110}, barH=28, gap=6, W=1160;
  const H = margin.top + margin.bottom + teams.length*(barH+gap);
  svg.attr("viewBox",`0 0 ${W} ${H}`).attr("width","100%");
  const xMax = d3.max(teams, d => cats.reduce((s,c) => s+d[c.key].xG, 0));
  const x = d3.scaleLinear().domain([0,xMax*1.12]).range([margin.left,W-margin.right]);
  const y = d3.scaleBand().domain(teams.map(d=>d.short)).range([margin.top,H-margin.bottom]).paddingInner(gap/(barH+gap));

  svg.append("g").attr("class","grid").attr("transform",`translate(0,${margin.top})`).call(d3.axisTop(x).ticks(8).tickSize(-(H-margin.top-margin.bottom)).tickFormat(""));
  svg.append("g").attr("class","axis").attr("transform",`translate(${margin.left},0)`).call(d3.axisLeft(y).tickSize(0).tickPadding(8)).select(".domain").remove();
  svg.append("g").attr("class","axis").attr("transform",`translate(0,${H-margin.bottom})`).call(d3.axisBottom(x).ticks(8).tickFormat(d=>d.toFixed(1)));

  const tooltip = d3.select("#tooltip"), barsG = svg.append("g");
  teams.forEach(team => {
    let off = 0;
    cats.forEach(sit => {
      const val = team[sit.key].xG;
      barsG.append("rect").attr("x",x(off)).attr("y",y(team.short)).attr("width",Math.max(0,x(off+val)-x(off))).attr("height",y.bandwidth()).attr("rx",3).attr("fill",sit.color).attr("opacity",0.85)
        .on("mouseover",(event)=>{
          let h=`<div class="tt-team">${team.team}</div>`;
          cats.forEach(s=>{const b=s.key===sit.key?"font-weight:700":"";h+=`<div class="tt-row" style="${b}"><span class="tt-label"><span style="color:${s.color}">&#9632;</span> ${s.label}</span><span class="tt-val">${team[s.key].xG.toFixed(2)} xG (${team[s.key].goals}g / ${team[s.key].shots}sh)</span></div>`;});
          if(isAll){const t=cats.reduce((s,c)=>s+team[c.key].xG,0);h+=`<div class="tt-row tt-total"><span class="tt-label">Total</span><span class="tt-val">${t.toFixed(2)} xG</span></div>`;}
          tooltip.html(h).style("opacity",1);moveTooltip(event);
        }).on("mousemove",moveTooltip).on("mouseout",hideTooltip);
      off += val;
    });
    barsG.append("text").attr("x",x(off)+6).attr("y",y(team.short)+y.bandwidth()/2).attr("dy","0.35em").attr("font-size",14).attr("font-weight",600).attr("fill","#020202").text(off.toFixed(1));
  });
  if(isAll){const lg=svg.append("g").attr("transform",`translate(${margin.left},6)`);let lx=0;SITUATIONS.forEach(s=>{lg.append("rect").attr("x",lx).attr("width",10).attr("height",10).attr("rx",2).attr("fill",s.color).attr("opacity",0.85);lg.append("text").attr("x",lx+14).attr("y",9).attr("font-size",13).attr("fill","#555555").text(s.label);lx+=s.label.length*7+24;});}
}

// ── SP Chart 2: Net xG ──────────────────────────────────────────
function drawSpNet(teamsRaw, filter) {
  const svg = d3.select("#sp-c2"); svg.selectAll("*").remove();
  const isAll = filter === "all";
  const cats = isAll ? SITUATIONS : SITUATIONS.filter(s => s.key === filter);
  const lbl = isAll ? "All Set Pieces" : cats[0].label;
  d3.select("#sp-c2-title").text(`Net Set Piece xG — ${lbl} — ${seasonLabel()}`);
  d3.select("#sp-c2-sub").text(`Net xG (created − conceded). Green = positive balance, red = conceding more than creating.`);

  const teams = [...teamsRaw].map(t => {
    const forXG = cats.reduce((s,c) => s+t[c.key].xG,0);
    const againstXG = cats.reduce((s,c) => s+t[c.key].against_xG,0);
    return {...t,forXG,againstXG,net:+(forXG-againstXG).toFixed(2)};
  }).sort((a,b)=>b.net-a.net);

  const margin={top:12,right:60,bottom:40,left:110}, rowH=30, W=1160;
  const H=margin.top+margin.bottom+teams.length*rowH;
  svg.attr("viewBox",`0 0 ${W} ${H}`).attr("width","100%");
  const absMax=d3.max(teams,d=>Math.abs(d.net))*1.2;
  const x=d3.scaleLinear().domain([-absMax,absMax]).range([margin.left,W-margin.right]);
  const y=d3.scaleBand().domain(teams.map(d=>d.short)).range([margin.top,H-margin.bottom]).paddingInner(0.25);

  svg.append("g").attr("class","grid").attr("transform",`translate(0,${margin.top})`).call(d3.axisTop(x).ticks(10).tickSize(-(H-margin.top-margin.bottom)).tickFormat(""));
  svg.append("line").attr("x1",x(0)).attr("x2",x(0)).attr("y1",margin.top).attr("y2",H-margin.bottom).attr("stroke","#020202").attr("stroke-width",1).attr("stroke-opacity",0.25);
  svg.append("g").attr("class","axis").attr("transform",`translate(${margin.left},0)`).call(d3.axisLeft(y).tickSize(0).tickPadding(8)).select(".domain").remove();
  svg.append("g").attr("class","axis").attr("transform",`translate(0,${H-margin.bottom})`).call(d3.axisBottom(x).ticks(10).tickFormat(d=>(d>0?"+":"")+d.toFixed(1)));

  const tooltip=d3.select("#tooltip");
  teams.forEach(team=>{
    const pos=team.net>=0, col=pos?"#16a34a":"#dc2626";
    svg.append("rect").attr("x",pos?x(0):x(team.net)).attr("y",y(team.short)).attr("width",Math.abs(x(team.net)-x(0))).attr("height",y.bandwidth()).attr("rx",3).attr("fill",col).attr("opacity",0.75).style("cursor","pointer")
      .on("mouseover",(event)=>{
        let h=`<div class="tt-team">${team.team}</div>`;
        cats.forEach(s=>{h+=`<div class="tt-row"><span class="tt-label"><span style="color:${s.color}">&#9632;</span> ${s.label}</span><span class="tt-val">+${team[s.key].xG.toFixed(2)} / −${team[s.key].against_xG.toFixed(2)}</span></div>`;});
        h+=`<div class="tt-row tt-total"><span class="tt-label">xG Created</span><span class="tt-val">${team.forXG.toFixed(2)}</span></div>`;
        h+=`<div class="tt-row"><span class="tt-label">xG Conceded</span><span class="tt-val">${team.againstXG.toFixed(2)}</span></div>`;
        h+=`<div class="tt-row" style="font-weight:700"><span class="tt-label">Net</span><span class="tt-val" style="color:${col}">${(team.net>0?"+":"")+team.net.toFixed(2)}</span></div>`;
        tooltip.html(h).style("opacity",1);moveTooltip(event);
      }).on("mousemove",moveTooltip).on("mouseout",hideTooltip);
    const lx=pos?x(team.net)+6:x(team.net)-6, anch=pos?"start":"end";
    svg.append("text").attr("x",lx).attr("y",y(team.short)+y.bandwidth()/2).attr("dy","0.35em").attr("text-anchor",anch).attr("font-size",13).attr("font-weight",600).attr("fill",col).text((team.net>0?"+":"")+team.net.toFixed(2));
  });
}

// ── SP Chart 3: xG per Action ───────────────────────────────────
function drawSpPerAction(teamsRaw, filter) {
  const countsLookup = getCountsLookup();
  const hasCounts = Object.keys(countsLookup).length > 0;
  const ETYPE = [
    {key:"FromCorner",countKey:"corners_taken",label:"Corners",color:"#6B6EAF",unit:"corner"},
    {key:"DirectFreekick",countKey:"freekicks_won",label:"Free Kicks",color:"#4A9B6F",unit:"FK won"},
    {key:"Penalty",countKey:"penalties_won",label:"Penalties",color:"#FF5A5F",unit:"pen"},
  ];
  const isAll = filter === "all";
  if(!isAll && filter==="SetPiece"){const svg=d3.select("#sp-c3");svg.selectAll("*").remove();d3.select("#sp-c3-title").text("xG per Action");d3.select("#sp-c3-sub").text("No raw count data available for indirect set pieces.");svg.attr("viewBox","0 0 1160 60").attr("width","100%");svg.append("text").attr("x",580).attr("y",35).attr("text-anchor","middle").attr("font-size",14).attr("fill","#555555").text("Select a different filter to see xG per action.");return;}
  const activeTypes = isAll ? ETYPE : ETYPE.filter(e => e.key === filter);
  const lbl = isAll ? "All Measurable Set Pieces" : activeTypes[0].label;
  d3.select("#sp-c3-title").text(`xG per Action — ${lbl} — ${seasonLabel()}`);
  d3.select("#sp-c3-sub").text(isAll?"xG generated per set piece taken (corners, free kicks, penalties). Grouped bars show efficiency by type.":`xG generated per ${activeTypes[0].unit} — higher = more dangerous from each opportunity.`);
  if(!hasCounts){const svg=d3.select("#sp-c3");svg.selectAll("*").remove();svg.attr("viewBox","0 0 1160 60").attr("width","100%");svg.append("text").attr("x",580).attr("y",35).attr("text-anchor","middle").attr("font-size",14).attr("fill","#555555").text("No Premier League count data available for this season.");return;}

  const teams = teamsRaw.map(t=>{const c=countsLookup[t.team];if(!c)return null;const e={team:t.team,short:SHORT_NAMES[t.team]||t.team};let txg=0,tc=0;
    activeTypes.forEach(et=>{const xg=t[et.key]?t[et.key].xG:0,cnt=c[et.countKey]||0,eff=cnt>0?xg/cnt:0;e[et.key]={xG:xg,count:cnt,efficiency:eff,goals:t[et.key]?t[et.key].goals:0,shots:t[et.key]?t[et.key].shots:0};txg+=xg;tc+=cnt;});
    e.totalEfficiency=tc>0?txg/tc:0;e.totalXG=txg;e.totalCount=tc;return e;}).filter(Boolean);
  if(isAll)teams.sort((a,b)=>b.totalEfficiency-a.totalEfficiency);else{const k=activeTypes[0].key;teams.sort((a,b)=>b[k].efficiency-a[k].efficiency);}

  drawGroupedBar({svgId:"#sp-c3",teams,activeTypes,isAll,xAccessor:et=>"efficiency",xLabel:`xG per Action — ${lbl}`,xFormat:d=>d.toFixed(3),
    tooltipFn:(team,etype)=>{
      let h=`<div class="tt-team">${team.team}</div>`;
      activeTypes.forEach(et=>{const d=team[et.key],b=et.key===etype.key?"font-weight:700":"";h+=`<div class="tt-row" style="${b}"><span class="tt-label"><span style="color:${et.color}">&#9632;</span> ${et.label}</span><span class="tt-val">${d.efficiency.toFixed(4)} xG/${et.unit}</span></div>`;h+=`<div class="tt-row" style="font-size:11px;${b}"><span class="tt-label" style="padding-left:16px">${d.xG.toFixed(2)} xG from ${d.count} ${et.unit}s</span><span class="tt-val">${d.goals}g / ${d.shots}sh</span></div>`;});
      if(isAll)h+=`<div class="tt-row tt-total" style="font-weight:700"><span class="tt-label">Overall</span><span class="tt-val">${team.totalEfficiency.toFixed(4)} xG/action (${team.totalCount} total)</span></div>`;
      return h;
    },legendSuffix:et=>`xG/${et.unit}`});
}

// ── SP Chart 4: xG Allowed per Action ───────────────────────────
function drawSpAllowedPerAction(teamsRaw, filter) {
  const countsLookup = getCountsLookup();
  const hasCounts = Object.keys(countsLookup).length > 0;
  const DTYPE = [
    {key:"FromCorner",countKey:"corners_conceded",label:"Corners",color:"#6B6EAF",unit:"corner"},
    {key:"DirectFreekick",countKey:"freekicks_conceded",label:"Free Kicks",color:"#4A9B6F",unit:"FK"},
    {key:"Penalty",countKey:"penalties_conceded",label:"Penalties",color:"#FF5A5F",unit:"pen"},
  ];
  const isAll = filter === "all";
  if(!isAll && filter==="SetPiece"){const svg=d3.select("#sp-c4");svg.selectAll("*").remove();d3.select("#sp-c4-title").text("xG Allowed per Action");d3.select("#sp-c4-sub").text("No raw count data available for indirect set pieces.");svg.attr("viewBox","0 0 1160 60").attr("width","100%");svg.append("text").attr("x",580).attr("y",35).attr("text-anchor","middle").attr("font-size",14).attr("fill","#555555").text("Select a different filter to see xG allowed per action.");return;}
  const activeTypes = isAll ? DTYPE : DTYPE.filter(e => e.key === filter);
  const lbl = isAll ? "All Measurable Set Pieces" : activeTypes[0].label;
  d3.select("#sp-c4-title").text(`xG Allowed per Action — ${lbl} — ${seasonLabel()}`);
  d3.select("#sp-c4-sub").text(isAll?"xG conceded per set piece faced (corners, free kicks, penalties). Higher = more vulnerable defensively.":`xG conceded per ${activeTypes[0].unit} faced — higher = more vulnerable from each opponent opportunity.`);
  if(!hasCounts){const svg=d3.select("#sp-c4");svg.selectAll("*").remove();svg.attr("viewBox","0 0 1160 60").attr("width","100%");svg.append("text").attr("x",580).attr("y",35).attr("text-anchor","middle").attr("font-size",14).attr("fill","#555555").text("No Premier League count data available for this season.");return;}

  const teams = teamsRaw.map(t=>{const c=countsLookup[t.team];if(!c)return null;const e={team:t.team,short:SHORT_NAMES[t.team]||t.team};let txg=0,tc=0;
    activeTypes.forEach(et=>{const axg=t[et.key]?t[et.key].against_xG:0,cnt=c[et.countKey]||0,eff=cnt>0?axg/cnt:0;e[et.key]={against_xG:axg,conceded:cnt,efficiency:eff,against_goals:t[et.key]?t[et.key].against_goals:0,against_shots:t[et.key]?t[et.key].against_shots:0};txg+=axg;tc+=cnt;});
    e.totalEfficiency=tc>0?txg/tc:0;e.totalAgainstXG=txg;e.totalConcededCount=tc;return e;}).filter(Boolean);
  if(isAll)teams.sort((a,b)=>b.totalEfficiency-a.totalEfficiency);else{const k=activeTypes[0].key;teams.sort((a,b)=>b[k].efficiency-a[k].efficiency);}

  drawGroupedBar({svgId:"#sp-c4",teams,activeTypes,isAll,xAccessor:et=>"efficiency",xLabel:`xG Allowed per Action — ${lbl}`,xFormat:d=>d.toFixed(3),
    tooltipFn:(team,etype)=>{
      let h=`<div class="tt-team">${team.team}</div>`;
      activeTypes.forEach(et=>{const d=team[et.key],b=et.key===etype.key?"font-weight:700":"";h+=`<div class="tt-row" style="${b}"><span class="tt-label"><span style="color:${et.color}">&#9632;</span> ${et.label}</span><span class="tt-val">${d.efficiency.toFixed(4)} xG/${et.unit}</span></div>`;h+=`<div class="tt-row" style="font-size:11px;${b}"><span class="tt-label" style="padding-left:16px">${d.against_xG.toFixed(2)} xG from ${d.conceded} ${et.unit}s faced</span><span class="tt-val">${d.against_goals}g / ${d.against_shots}sh</span></div>`;});
      if(isAll)h+=`<div class="tt-row tt-total" style="font-weight:700"><span class="tt-label">Overall</span><span class="tt-val">${team.totalEfficiency.toFixed(4)} xG/action (${team.totalConcededCount} faced)</span></div>`;
      return h;
    },legendSuffix:et=>`xG/${et.unit} faced`});
}

// ── SP Chart 5: Raw Set Piece Counts ─────────────────────────────
function drawSpRawCounts(teamsRaw, filter) {
  const countsLookup = getCountsLookup();
  const hasCounts = Object.keys(countsLookup).length > 0;
  const CTYPE = [
    {takenKey:"corners_taken",concKey:"corners_conceded",label:"Corners",color:"#6B6EAF",filterKey:"FromCorner"},
    {takenKey:"freekicks_won",concKey:"freekicks_conceded",label:"Free Kicks",color:"#4A9B6F",filterKey:"DirectFreekick"},
    {takenKey:"penalties_won",concKey:"penalties_conceded",label:"Penalties",color:"#FF5A5F",filterKey:"Penalty"},
  ];
  const isAll = filter === "all";
  if(!isAll && filter==="SetPiece"){const svg=d3.select("#sp-c5");svg.selectAll("*").remove();d3.select("#sp-c5-title").text("Raw Set Piece Counts");d3.select("#sp-c5-sub").text("No raw count data available for indirect set pieces.");svg.attr("viewBox","0 0 1160 60").attr("width","100%");svg.append("text").attr("x",580).attr("y",35).attr("text-anchor","middle").attr("font-size",14).attr("fill","#555555").text("Select a different filter to see raw counts.");return;}
  const activeTypes = isAll ? CTYPE : CTYPE.filter(c => c.filterKey === filter);
  const lbl = isAll ? "All Measurable Set Pieces" : activeTypes[0].label;
  d3.select("#sp-c5-title").text(`Raw Set Piece Counts — ${lbl} — ${seasonLabel()}`);
  d3.select("#sp-c5-sub").text(`Total ${lbl.toLowerCase()} taken (green, right) vs conceded (red, left). Use this to cross-check the efficiency charts above.`);
  if(!hasCounts){const svg=d3.select("#sp-c5");svg.selectAll("*").remove();svg.attr("viewBox","0 0 1160 60").attr("width","100%");svg.append("text").attr("x",580).attr("y",35).attr("text-anchor","middle").attr("font-size",14).attr("fill","#555555").text("No Premier League count data available for this season.");return;}

  const teams = teamsRaw.map(t=>{
    const c=countsLookup[t.team];if(!c)return null;
    const e={team:t.team,short:SHORT_NAMES[t.team]||t.team};
    let totalTaken=0,totalConc=0;
    activeTypes.forEach(ct=>{
      const tk=c[ct.takenKey]||0, cn=c[ct.concKey]||0;
      e[ct.filterKey]={taken:tk,conceded:cn,label:ct.label};
      totalTaken+=tk;totalConc+=cn;
    });
    e.totalTaken=totalTaken;e.totalConceded=totalConc;
    return e;
  }).filter(Boolean).sort((a,b)=>b.totalTaken-a.totalTaken);

  const svg=d3.select("#sp-c5");svg.selectAll("*").remove();
  const margin={top:32,right:60,bottom:40,left:110},rowH=30,W=1160;
  const H=margin.top+margin.bottom+teams.length*rowH;
  svg.attr("viewBox",`0 0 ${W} ${H}`).attr("width","100%");
  const absMax=d3.max(teams,d=>Math.max(d.totalTaken,d.totalConceded))*1.15||1;
  const x=d3.scaleLinear().domain([-absMax,absMax]).range([margin.left,W-margin.right]);
  const y=d3.scaleBand().domain(teams.map(d=>d.short)).range([margin.top,H-margin.bottom]).paddingInner(0.22);

  svg.append("g").attr("class","grid").attr("transform",`translate(0,${margin.top})`).call(d3.axisTop(x).ticks(10).tickSize(-(H-margin.top-margin.bottom)).tickFormat(""));
  svg.append("line").attr("x1",x(0)).attr("x2",x(0)).attr("y1",margin.top).attr("y2",H-margin.bottom).attr("stroke","#020202").attr("stroke-width",1.5).attr("stroke-opacity",0.3);
  svg.append("g").attr("class","axis").attr("transform",`translate(${margin.left},0)`).call(d3.axisLeft(y).tickSize(0).tickPadding(8)).select(".domain").remove();
  svg.append("g").attr("class","axis").attr("transform",`translate(0,${H-margin.bottom})`).call(d3.axisBottom(x).ticks(10).tickFormat(d=>Math.abs(d)));

  svg.append("text").attr("x",x(-absMax/2)).attr("y",H-4).attr("text-anchor","middle").attr("font-size",12).attr("fill","#dc2626").text("\u2190 Conceded");
  svg.append("text").attr("x",x(absMax/2)).attr("y",H-4).attr("text-anchor","middle").attr("font-size",12).attr("fill","#16a34a").text("Taken \u2192");

  const tooltip=d3.select("#tooltip");
  teams.forEach(team=>{
    svg.append("rect").attr("x",x(-team.totalConceded)).attr("y",y(team.short)).attr("width",Math.abs(x(0)-x(-team.totalConceded))).attr("height",y.bandwidth()).attr("rx",3).attr("fill","#dc2626").attr("opacity",0.7).style("cursor","pointer")
      .on("mouseover",event=>{tooltip.html(countsTT(team)).style("opacity",1);moveTooltip(event);}).on("mousemove",moveTooltip).on("mouseout",hideTooltip);
    svg.append("rect").attr("x",x(0)).attr("y",y(team.short)).attr("width",Math.max(0,x(team.totalTaken)-x(0))).attr("height",y.bandwidth()).attr("rx",3).attr("fill","#16a34a").attr("opacity",0.7).style("cursor","pointer")
      .on("mouseover",event=>{tooltip.html(countsTT(team)).style("opacity",1);moveTooltip(event);}).on("mousemove",moveTooltip).on("mouseout",hideTooltip);
    svg.append("text").attr("x",x(-team.totalConceded)-5).attr("y",y(team.short)+y.bandwidth()/2).attr("dy","0.35em").attr("text-anchor","end").attr("font-size",12).attr("font-weight",600).attr("fill","#dc2626").text(team.totalConceded);
    svg.append("text").attr("x",x(team.totalTaken)+5).attr("y",y(team.short)+y.bandwidth()/2).attr("dy","0.35em").attr("text-anchor","start").attr("font-size",12).attr("font-weight",600).attr("fill","#16a34a").text(team.totalTaken);
  });

  const lg=svg.append("g").attr("transform",`translate(${margin.left},6)`);
  lg.append("rect").attr("x",0).attr("width",10).attr("height",10).attr("rx",2).attr("fill","#16a34a").attr("opacity",0.7);
  lg.append("text").attr("x",14).attr("y",9).attr("font-size",13).attr("fill","#555555").text("Taken");
  lg.append("rect").attr("x",70).attr("width",10).attr("height",10).attr("rx",2).attr("fill","#dc2626").attr("opacity",0.7);
  lg.append("text").attr("x",84).attr("y",9).attr("font-size",13).attr("fill","#555555").text("Conceded");

  function countsTT(team){
    let h=`<div class="tt-team">${team.team}</div>`;
    activeTypes.forEach(ct=>{
      const d=team[ct.filterKey];
      h+=`<div class="tt-row"><span class="tt-label"><span style="color:${ct.color}">\u25A0</span> ${d.label}</span><span class="tt-val" style="color:#16a34a">${d.taken} taken</span></div>`;
      h+=`<div class="tt-row"><span class="tt-label" style="padding-left:16px">Conceded</span><span class="tt-val" style="color:#dc2626">${d.conceded}</span></div>`;
    });
    if(isAll){
      h+=`<div class="tt-row tt-total"><span class="tt-label">Total Taken</span><span class="tt-val" style="color:#16a34a">${team.totalTaken}</span></div>`;
      h+=`<div class="tt-row"><span class="tt-label">Total Conceded</span><span class="tt-val" style="color:#dc2626">${team.totalConceded}</span></div>`;
    }
    return h;
  }
}

// ╔══════════════════════════════════════════════════════════════════╗
// ║  GENERIC GROUPED BAR (used by SP charts 3 & 4)                  ║
// ╚══════════════════════════════════════════════════════════════════╝
function drawGroupedBar(cfg) {
  const {svgId,teams,activeTypes,isAll,xLabel,xFormat,tooltipFn,legendSuffix} = cfg;
  const svg = d3.select(svgId); svg.selectAll("*").remove();
  const margin={top:32,right:80,bottom:40,left:110};
  const groupH=isAll?50:28, gap=isAll?10:6, W=1160;
  const H=margin.top+margin.bottom+teams.length*(groupH+gap);
  svg.attr("viewBox",`0 0 ${W} ${H}`).attr("width","100%");

  let xMax;
  if(isAll)xMax=d3.max(teams,d=>d3.max(activeTypes,et=>d[et.key].efficiency));
  else xMax=d3.max(teams,d=>d[activeTypes[0].key].efficiency);
  xMax=Math.max((xMax||0.01)*1.15,0.01);

  const x=d3.scaleLinear().domain([0,xMax]).range([margin.left,W-margin.right]);
  const y=d3.scaleBand().domain(teams.map(d=>d.short)).range([margin.top,H-margin.bottom]).paddingInner(gap/(groupH+gap));

  svg.append("g").attr("class","grid").attr("transform",`translate(0,${margin.top})`).call(d3.axisTop(x).ticks(8).tickSize(-(H-margin.top-margin.bottom)).tickFormat(""));
  svg.append("g").attr("class","axis").attr("transform",`translate(${margin.left},0)`).call(d3.axisLeft(y).tickSize(0).tickPadding(8)).select(".domain").remove();
  svg.append("g").attr("class","axis").attr("transform",`translate(0,${H-margin.bottom})`).call(d3.axisBottom(x).ticks(8).tickFormat(xFormat));
  svg.append("text").attr("x",(margin.left+W-margin.right)/2).attr("y",H-4).attr("text-anchor","middle").attr("font-size",14).attr("fill","#555555").text(xLabel);

  const tooltip=d3.select("#tooltip"), barsG=svg.append("g");
  if(isAll){
    const subH=y.bandwidth()/activeTypes.length;
    teams.forEach(team=>{activeTypes.forEach((et,i)=>{
      const eff=team[et.key].efficiency, barY=y(team.short)+i*subH;
      barsG.append("rect").attr("x",x(0)).attr("y",barY).attr("width",Math.max(0,x(eff)-x(0))).attr("height",subH-1).attr("rx",2).attr("fill",et.color).attr("opacity",0.85).style("cursor","pointer")
        .on("mouseover",event=>{tooltip.html(tooltipFn(team,et)).style("opacity",1);moveTooltip(event);}).on("mousemove",moveTooltip).on("mouseout",hideTooltip);
      barsG.append("text").attr("x",x(eff)+4).attr("y",barY+(subH-1)/2).attr("dy","0.35em").attr("font-size",13).attr("font-weight",600).attr("fill",et.color).text(eff.toFixed(4));
    });});
  } else {
    const et=activeTypes[0];
    teams.forEach(team=>{
      const eff=team[et.key].efficiency;
      barsG.append("rect").attr("x",x(0)).attr("y",y(team.short)).attr("width",Math.max(0,x(eff)-x(0))).attr("height",y.bandwidth()).attr("rx",3).attr("fill",et.color).attr("opacity",0.85).style("cursor","pointer")
        .on("mouseover",event=>{tooltip.html(tooltipFn(team,et)).style("opacity",1);moveTooltip(event);}).on("mousemove",moveTooltip).on("mouseout",hideTooltip);
      barsG.append("text").attr("x",x(eff)+6).attr("y",y(team.short)+y.bandwidth()/2).attr("dy","0.35em").attr("font-size",13).attr("font-weight",600).attr("fill","#020202").text(eff.toFixed(4));
    });
  }
  if(isAll){const lg=svg.append("g").attr("transform",`translate(${margin.left},6)`);let lx=0;activeTypes.forEach(et=>{lg.append("rect").attr("x",lx).attr("width",10).attr("height",10).attr("rx",2).attr("fill",et.color).attr("opacity",0.85);lg.append("text").attr("x",lx+14).attr("y",9).attr("font-size",13).attr("fill","#555555").text(`${et.label} (${legendSuffix(et)})`);lx+=(et.label.length+legendSuffix(et).length+3)*6.5+30;});}
}

// ╔══════════════════════════════════════════════════════════════════╗
// ║  SHOT ZONES TAB                                                  ║
// ╚══════════════════════════════════════════════════════════════════╝
function redrawShotZones(teams) {
  const hasData = teams.length > 0 && teams[0].shotZone && Object.keys(teams[0].shotZone).length > 0;
  d3.select("#sz-no-data").style("display", hasData ? "none" : "block");
  d3.select("#sz-charts").style("display", hasData ? "block" : "none");
  if (!hasData) return;
  const f = tabFilters.shotzones;
  drawCatTotal("sz", teams, SHOT_ZONES, f, "shotZone", "Shot Zone");
  drawCatNet("sz", teams, SHOT_ZONES, f, "shotZone", "Shot Zone");
  drawCatPerShot("sz", teams, SHOT_ZONES, f, "shotZone", "Shot Zone");
  drawCatBalance("sz", teams, SHOT_ZONES, f, "shotZone", "Shot Zone");
  drawCatShotEfficiency("sz", teams, SHOT_ZONES, f, "shotZone", "Shot Zone");
}

// ╔══════════════════════════════════════════════════════════════════╗
// ║  ATTACK SPEED TAB                                                ║
// ╚══════════════════════════════════════════════════════════════════╝
function redrawAttackSpeed(teams) {
  const hasData = teams.length > 0 && teams[0].attackSpeed && Object.keys(teams[0].attackSpeed).length > 0;
  d3.select("#as-no-data").style("display", hasData ? "none" : "block");
  d3.select("#as-charts").style("display", hasData ? "block" : "none");
  if (!hasData) return;
  const f = tabFilters.attackspeed;
  drawCatTotal("as", teams, ATTACK_SPEEDS, f, "attackSpeed", "Attack Speed");
  drawCatNet("as", teams, ATTACK_SPEEDS, f, "attackSpeed", "Attack Speed");
  drawCatPerShot("as", teams, ATTACK_SPEEDS, f, "attackSpeed", "Attack Speed");
  drawCatBalance("as", teams, ATTACK_SPEEDS, f, "attackSpeed", "Attack Speed");
  drawCatShotEfficiency("as", teams, ATTACK_SPEEDS, f, "attackSpeed", "Attack Speed");
}

// ╔══════════════════════════════════════════════════════════════════╗
// ║  GENERIC CATEGORY CHARTS (Shot Zones + Attack Speed)             ║
// ╚══════════════════════════════════════════════════════════════════╝

// Helper: get data for a category from a team object
function catData(team, dataKey, catKey) {
  const group = team[dataKey];
  if (!group || !group[catKey]) return { xG:0, goals:0, shots:0, against_xG:0, against_goals:0, against_shots:0 };
  return group[catKey];
}

// ── Generic Total xG ────────────────────────────────────────────
function drawCatTotal(prefix, teamsRaw, allCats, filter, dataKey, tabLabel) {
  const svg = d3.select(`#${prefix}-c1`); svg.selectAll("*").remove();
  const isAll = filter === "all";
  const cats = isAll ? allCats : allCats.filter(c => c.key === filter);
  const lbl = isAll ? `All ${tabLabel}s` : cats[0].label;
  d3.select(`#${prefix}-c1-title`).text(`Total xG Created — ${lbl} — ${seasonLabel()}`);
  d3.select(`#${prefix}-c1-sub`).text(`Total expected goals created, grouped by ${tabLabel.toLowerCase()}.`);

  const teams = [...teamsRaw].sort((a,b) => {
    return cats.reduce((s,c)=>s+catData(b,dataKey,c.key).xG,0) - cats.reduce((s,c)=>s+catData(a,dataKey,c.key).xG,0);
  });

  const margin={top:32,right:60,bottom:40,left:110}, barH=28, gap=6, W=1160;
  const H=margin.top+margin.bottom+teams.length*(barH+gap);
  svg.attr("viewBox",`0 0 ${W} ${H}`).attr("width","100%");
  const xMax=d3.max(teams,d=>cats.reduce((s,c)=>s+catData(d,dataKey,c.key).xG,0));
  const x=d3.scaleLinear().domain([0,(xMax||1)*1.12]).range([margin.left,W-margin.right]);
  const y=d3.scaleBand().domain(teams.map(d=>d.short)).range([margin.top,H-margin.bottom]).paddingInner(gap/(barH+gap));

  svg.append("g").attr("class","grid").attr("transform",`translate(0,${margin.top})`).call(d3.axisTop(x).ticks(8).tickSize(-(H-margin.top-margin.bottom)).tickFormat(""));
  svg.append("g").attr("class","axis").attr("transform",`translate(${margin.left},0)`).call(d3.axisLeft(y).tickSize(0).tickPadding(8)).select(".domain").remove();
  svg.append("g").attr("class","axis").attr("transform",`translate(0,${H-margin.bottom})`).call(d3.axisBottom(x).ticks(8).tickFormat(d=>d.toFixed(1)));

  const tooltip=d3.select("#tooltip"), barsG=svg.append("g");
  teams.forEach(team=>{
    let off=0;
    cats.forEach(cat=>{
      const d=catData(team,dataKey,cat.key), val=d.xG;
      barsG.append("rect").attr("x",x(off)).attr("y",y(team.short)).attr("width",Math.max(0,x(off+val)-x(off))).attr("height",y.bandwidth()).attr("rx",3).attr("fill",cat.color).attr("opacity",0.85)
        .on("mouseover",(event)=>{
          let h=`<div class="tt-team">${team.team}</div>`;
          cats.forEach(c=>{const dd=catData(team,dataKey,c.key),b=c.key===cat.key?"font-weight:700":"";h+=`<div class="tt-row" style="${b}"><span class="tt-label"><span style="color:${c.color}">&#9632;</span> ${c.label}</span><span class="tt-val">${dd.xG.toFixed(2)} xG (${dd.goals}g / ${dd.shots}sh)</span></div>`;});
          if(isAll){const t=cats.reduce((s,c)=>s+catData(team,dataKey,c.key).xG,0);h+=`<div class="tt-row tt-total"><span class="tt-label">Total</span><span class="tt-val">${t.toFixed(2)} xG</span></div>`;}
          tooltip.html(h).style("opacity",1);moveTooltip(event);
        }).on("mousemove",moveTooltip).on("mouseout",hideTooltip);
      off+=val;
    });
    barsG.append("text").attr("x",x(off)+6).attr("y",y(team.short)+y.bandwidth()/2).attr("dy","0.35em").attr("font-size",14).attr("font-weight",600).attr("fill","#020202").text(off.toFixed(1));
  });
  if(isAll){const lg=svg.append("g").attr("transform",`translate(${margin.left},6)`);let lx=0;allCats.forEach(c=>{lg.append("rect").attr("x",lx).attr("width",10).attr("height",10).attr("rx",2).attr("fill",c.color).attr("opacity",0.85);lg.append("text").attr("x",lx+14).attr("y",9).attr("font-size",13).attr("fill","#555555").text(c.label);lx+=c.label.length*7+24;});}
}

// ── Generic Net xG ──────────────────────────────────────────────
function drawCatNet(prefix, teamsRaw, allCats, filter, dataKey, tabLabel) {
  const svg = d3.select(`#${prefix}-c2`); svg.selectAll("*").remove();
  const isAll = filter === "all";
  const cats = isAll ? allCats : allCats.filter(c => c.key === filter);
  const lbl = isAll ? `All ${tabLabel}s` : cats[0].label;
  d3.select(`#${prefix}-c2-title`).text(`Net xG — ${lbl} — ${seasonLabel()}`);
  d3.select(`#${prefix}-c2-sub`).text(`Net xG (created − conceded). Green = positive, red = negative.`);

  const teams = [...teamsRaw].map(t=>{
    const forXG=cats.reduce((s,c)=>s+catData(t,dataKey,c.key).xG,0);
    const againstXG=cats.reduce((s,c)=>s+catData(t,dataKey,c.key).against_xG,0);
    return {...t,forXG,againstXG,net:+(forXG-againstXG).toFixed(2)};
  }).sort((a,b)=>b.net-a.net);

  const margin={top:12,right:60,bottom:40,left:110}, rowH=30, W=1160;
  const H=margin.top+margin.bottom+teams.length*rowH;
  svg.attr("viewBox",`0 0 ${W} ${H}`).attr("width","100%");
  const absMax=d3.max(teams,d=>Math.abs(d.net))*1.2||1;
  const x=d3.scaleLinear().domain([-absMax,absMax]).range([margin.left,W-margin.right]);
  const y=d3.scaleBand().domain(teams.map(d=>d.short)).range([margin.top,H-margin.bottom]).paddingInner(0.25);

  svg.append("g").attr("class","grid").attr("transform",`translate(0,${margin.top})`).call(d3.axisTop(x).ticks(10).tickSize(-(H-margin.top-margin.bottom)).tickFormat(""));
  svg.append("line").attr("x1",x(0)).attr("x2",x(0)).attr("y1",margin.top).attr("y2",H-margin.bottom).attr("stroke","#020202").attr("stroke-width",1).attr("stroke-opacity",0.25);
  svg.append("g").attr("class","axis").attr("transform",`translate(${margin.left},0)`).call(d3.axisLeft(y).tickSize(0).tickPadding(8)).select(".domain").remove();
  svg.append("g").attr("class","axis").attr("transform",`translate(0,${H-margin.bottom})`).call(d3.axisBottom(x).ticks(10).tickFormat(d=>(d>0?"+":"")+d.toFixed(1)));

  const tooltip=d3.select("#tooltip");
  teams.forEach(team=>{
    const pos=team.net>=0, col=pos?"#16a34a":"#dc2626";
    svg.append("rect").attr("x",pos?x(0):x(team.net)).attr("y",y(team.short)).attr("width",Math.abs(x(team.net)-x(0))).attr("height",y.bandwidth()).attr("rx",3).attr("fill",col).attr("opacity",0.75).style("cursor","pointer")
      .on("mouseover",(event)=>{
        let h=`<div class="tt-team">${team.team}</div>`;
        cats.forEach(c=>{const d=catData(team,dataKey,c.key);h+=`<div class="tt-row"><span class="tt-label"><span style="color:${c.color}">&#9632;</span> ${c.label}</span><span class="tt-val">+${d.xG.toFixed(2)} / −${d.against_xG.toFixed(2)}</span></div>`;});
        h+=`<div class="tt-row tt-total"><span class="tt-label">xG Created</span><span class="tt-val">${team.forXG.toFixed(2)}</span></div>`;
        h+=`<div class="tt-row"><span class="tt-label">xG Conceded</span><span class="tt-val">${team.againstXG.toFixed(2)}</span></div>`;
        h+=`<div class="tt-row" style="font-weight:700"><span class="tt-label">Net</span><span class="tt-val" style="color:${col}">${(team.net>0?"+":"")+team.net.toFixed(2)}</span></div>`;
        tooltip.html(h).style("opacity",1);moveTooltip(event);
      }).on("mousemove",moveTooltip).on("mouseout",hideTooltip);
    const lx=pos?x(team.net)+6:x(team.net)-6;
    svg.append("text").attr("x",lx).attr("y",y(team.short)+y.bandwidth()/2).attr("dy","0.35em").attr("text-anchor",pos?"start":"end").attr("font-size",13).attr("font-weight",600).attr("fill",col).text((team.net>0?"+":"")+team.net.toFixed(2));
  });
}

// ── Generic xG per Shot ─────────────────────────────────────────
function drawCatPerShot(prefix, teamsRaw, allCats, filter, dataKey, tabLabel) {
  const svg = d3.select(`#${prefix}-c3`); svg.selectAll("*").remove();
  const isAll = filter === "all";
  const cats = isAll ? allCats : allCats.filter(c => c.key === filter);
  const lbl = isAll ? `All ${tabLabel}s` : cats[0].label;
  d3.select(`#${prefix}-c3-title`).text(`xG per Shot — ${lbl} — ${seasonLabel()}`);
  d3.select(`#${prefix}-c3-sub`).text(`Shot quality: xG per shot taken. Higher = better quality chances from this ${tabLabel.toLowerCase()}.`);

  // Build team data with per-shot efficiency
  const teams = teamsRaw.map(t=>{
    const e={team:t.team,short:SHORT_NAMES[t.team]||t.team};let txg=0,tsh=0;
    cats.forEach(cat=>{
      const d=catData(t,dataKey,cat.key);
      const eff=d.shots>0?d.xG/d.shots:0;
      e[cat.key]={xG:d.xG,shots:d.shots,goals:d.goals,efficiency:eff};
      txg+=d.xG;tsh+=d.shots;
    });
    e.totalEfficiency=tsh>0?txg/tsh:0;e.totalXG=txg;e.totalShots=tsh;
    return e;
  });
  if(isAll)teams.sort((a,b)=>b.totalEfficiency-a.totalEfficiency);
  else{const k=cats[0].key;teams.sort((a,b)=>b[k].efficiency-a[k].efficiency);}

  drawGroupedBar({svgId:`#${prefix}-c3`,teams,activeTypes:cats,isAll,xLabel:`xG per Shot — ${lbl}`,xFormat:d=>d.toFixed(3),
    tooltipFn:(team,etype)=>{
      let h=`<div class="tt-team">${team.team}</div>`;
      cats.forEach(c=>{const d=team[c.key],b=c.key===etype.key?"font-weight:700":"";h+=`<div class="tt-row" style="${b}"><span class="tt-label"><span style="color:${c.color}">&#9632;</span> ${c.label}</span><span class="tt-val">${d.efficiency.toFixed(4)} xG/shot</span></div>`;h+=`<div class="tt-row" style="font-size:11px;${b}"><span class="tt-label" style="padding-left:16px">${d.xG.toFixed(2)} xG from ${d.shots} shots</span><span class="tt-val">${d.goals}g</span></div>`;});
      if(isAll)h+=`<div class="tt-row tt-total" style="font-weight:700"><span class="tt-label">Overall</span><span class="tt-val">${team.totalEfficiency.toFixed(4)} xG/shot (${team.totalShots} shots)</span></div>`;
      return h;
    },legendSuffix:()=>"xG/shot"});
}

// ── Generic xG Balance (Butterfly chart) ─────────────────────────
function drawCatBalance(prefix, teamsRaw, allCats, filter, dataKey, tabLabel) {
  const svg = d3.select(`#${prefix}-c4`); svg.selectAll("*").remove();
  const isAll = filter === "all";
  const cats = isAll ? allCats : allCats.filter(c => c.key === filter);
  const lbl = isAll ? `All ${tabLabel}s` : cats[0].label;
  d3.select(`#${prefix}-c4-title`).text(`xG Balance — ${lbl} — ${seasonLabel()}`);
  d3.select(`#${prefix}-c4-sub`).text(`xG created (right, green) vs xG conceded (left, red). Shows attacking output and defensive exposure side by side.`);

  const teams = [...teamsRaw].map(t => {
    const forXG = cats.reduce((s,c) => s + catData(t,dataKey,c.key).xG, 0);
    const againstXG = cats.reduce((s,c) => s + catData(t,dataKey,c.key).against_xG, 0);
    const forShots = cats.reduce((s,c) => s + catData(t,dataKey,c.key).shots, 0);
    const againstShots = cats.reduce((s,c) => s + catData(t,dataKey,c.key).against_shots, 0);
    const forGoals = cats.reduce((s,c) => s + catData(t,dataKey,c.key).goals, 0);
    const againstGoals = cats.reduce((s,c) => s + catData(t,dataKey,c.key).against_goals, 0);
    return {...t, forXG, againstXG, forShots, againstShots, forGoals, againstGoals, net: +(forXG - againstXG).toFixed(2)};
  }).sort((a,b) => b.net - a.net);

  const margin = {top:32, right:60, bottom:40, left:110}, rowH = 30, W = 1160;
  const H = margin.top + margin.bottom + teams.length * rowH;
  svg.attr("viewBox", `0 0 ${W} ${H}`).attr("width", "100%");
  const absMax = d3.max(teams, d => Math.max(d.forXG, d.againstXG)) * 1.15 || 1;
  const x = d3.scaleLinear().domain([-absMax, absMax]).range([margin.left, W - margin.right]);
  const y = d3.scaleBand().domain(teams.map(d => d.short)).range([margin.top, H - margin.bottom]).paddingInner(0.22);

  svg.append("g").attr("class","grid").attr("transform",`translate(0,${margin.top})`).call(d3.axisTop(x).ticks(10).tickSize(-(H-margin.top-margin.bottom)).tickFormat(""));
  svg.append("line").attr("x1",x(0)).attr("x2",x(0)).attr("y1",margin.top).attr("y2",H-margin.bottom).attr("stroke","#020202").attr("stroke-width",1.5).attr("stroke-opacity",0.3);
  svg.append("g").attr("class","axis").attr("transform",`translate(${margin.left},0)`).call(d3.axisLeft(y).tickSize(0).tickPadding(8)).select(".domain").remove();
  svg.append("g").attr("class","axis").attr("transform",`translate(0,${H-margin.bottom})`).call(d3.axisBottom(x).ticks(10).tickFormat(d => Math.abs(d).toFixed(1)));
  // Axis labels
  svg.append("text").attr("x", x(-absMax/2)).attr("y", H - 4).attr("text-anchor","middle").attr("font-size",12).attr("fill","#dc2626").text("\u2190 xG Conceded");
  svg.append("text").attr("x", x(absMax/2)).attr("y", H - 4).attr("text-anchor","middle").attr("font-size",12).attr("fill","#16a34a").text("xG Created \u2192");

  const tooltip = d3.select("#tooltip");
  teams.forEach(team => {
    // xG Against bar (left, red)
    svg.append("rect").attr("x", x(-team.againstXG)).attr("y", y(team.short)).attr("width", Math.abs(x(0) - x(-team.againstXG))).attr("height", y.bandwidth()).attr("rx",3).attr("fill","#dc2626").attr("opacity",0.7).style("cursor","pointer")
      .on("mouseover", event => { tooltip.html(balanceTT(team, cats, dataKey)).style("opacity",1); moveTooltip(event); }).on("mousemove",moveTooltip).on("mouseout",hideTooltip);
    // xG For bar (right, green)
    svg.append("rect").attr("x", x(0)).attr("y", y(team.short)).attr("width", Math.max(0, x(team.forXG) - x(0))).attr("height", y.bandwidth()).attr("rx",3).attr("fill","#16a34a").attr("opacity",0.7).style("cursor","pointer")
      .on("mouseover", event => { tooltip.html(balanceTT(team, cats, dataKey)).style("opacity",1); moveTooltip(event); }).on("mousemove",moveTooltip).on("mouseout",hideTooltip);
    // Labels
    svg.append("text").attr("x", x(-team.againstXG) - 5).attr("y", y(team.short) + y.bandwidth()/2).attr("dy","0.35em").attr("text-anchor","end").attr("font-size",12).attr("font-weight",600).attr("fill","#dc2626").text(team.againstXG.toFixed(1));
    svg.append("text").attr("x", x(team.forXG) + 5).attr("y", y(team.short) + y.bandwidth()/2).attr("dy","0.35em").attr("text-anchor","start").attr("font-size",12).attr("font-weight",600).attr("fill","#16a34a").text(team.forXG.toFixed(1));
  });

  // Legend
  const lg = svg.append("g").attr("transform", `translate(${margin.left}, 6)`);
  lg.append("rect").attr("x",0).attr("width",10).attr("height",10).attr("rx",2).attr("fill","#16a34a").attr("opacity",0.7);
  lg.append("text").attr("x",14).attr("y",9).attr("font-size",13).attr("fill","#555555").text("xG Created");
  lg.append("rect").attr("x",110).attr("width",10).attr("height",10).attr("rx",2).attr("fill","#dc2626").attr("opacity",0.7);
  lg.append("text").attr("x",124).attr("y",9).attr("font-size",13).attr("fill","#555555").text("xG Conceded");

  function balanceTT(team, cats, dk) {
    let h = `<div class="tt-team">${team.team}</div>`;
    cats.forEach(c => {
      const d = catData(team, dk, c.key);
      h += `<div class="tt-row"><span class="tt-label"><span style="color:${c.color}">\u25A0</span> ${c.label}</span><span class="tt-val" style="color:#16a34a">+${d.xG.toFixed(2)}</span></div>`;
      h += `<div class="tt-row"><span class="tt-label" style="padding-left:16px">Conceded</span><span class="tt-val" style="color:#dc2626">\u2212${d.against_xG.toFixed(2)}</span></div>`;
    });
    h += `<div class="tt-row tt-total"><span class="tt-label">Total Created</span><span class="tt-val" style="color:#16a34a">${team.forXG.toFixed(2)} (${team.forGoals}g / ${team.forShots}sh)</span></div>`;
    h += `<div class="tt-row"><span class="tt-label">Total Conceded</span><span class="tt-val" style="color:#dc2626">${team.againstXG.toFixed(2)} (${team.againstGoals}g / ${team.againstShots}sh)</span></div>`;
    const col = team.net >= 0 ? "#16a34a" : "#dc2626";
    h += `<div class="tt-row" style="font-weight:700"><span class="tt-label">Net</span><span class="tt-val" style="color:${col}">${(team.net>0?"+":"") + team.net.toFixed(2)}</span></div>`;
    return h;
  }
}

// ── Generic Shot Efficiency (xG/Shot vs xGA/Shot) ────────────────
function drawCatShotEfficiency(prefix, teamsRaw, allCats, filter, dataKey, tabLabel) {
  const svg = d3.select(`#${prefix}-c5`); svg.selectAll("*").remove();
  const isAll = filter === "all";
  const cats = isAll ? allCats : allCats.filter(c => c.key === filter);
  const lbl = isAll ? `All ${tabLabel}s` : cats[0].label;
  d3.select(`#${prefix}-c5-title`).text(`Shot Efficiency — ${lbl} — ${seasonLabel()}`);
  d3.select(`#${prefix}-c5-sub`).text(`xG/Shot (offensive quality, green) vs xGA/Shot (defensive quality conceded, red). Bigger green gap = more efficient team.`);

  const teams = teamsRaw.map(t => {
    let txg=0, tsh=0, taxg=0, tash=0;
    cats.forEach(c => {
      const d = catData(t, dataKey, c.key);
      txg += d.xG; tsh += d.shots; taxg += d.against_xG; tash += d.against_shots;
    });
    const offEff = tsh > 0 ? txg / tsh : 0;
    const defEff = tash > 0 ? taxg / tash : 0;
    return {
      team: t.team, short: SHORT_NAMES[t.team] || t.team,
      offEff, defEff, diff: offEff - defEff,
      totalXG: txg, totalShots: tsh, totalAXG: taxg, totalAShots: tash,
      _src: t
    };
  }).sort((a,b) => b.diff - a.diff);

  const margin = {top:32, right:80, bottom:40, left:110}, rowH = 36, W = 1160;
  const H = margin.top + margin.bottom + teams.length * rowH;
  svg.attr("viewBox", `0 0 ${W} ${H}`).attr("width", "100%");
  const xMax = d3.max(teams, d => Math.max(d.offEff, d.defEff)) * 1.18 || 0.01;
  const x = d3.scaleLinear().domain([0, xMax]).range([margin.left, W - margin.right]);
  const y = d3.scaleBand().domain(teams.map(d => d.short)).range([margin.top, H - margin.bottom]).paddingInner(0.2);

  svg.append("g").attr("class","grid").attr("transform",`translate(0,${margin.top})`).call(d3.axisTop(x).ticks(8).tickSize(-(H-margin.top-margin.bottom)).tickFormat(""));
  svg.append("g").attr("class","axis").attr("transform",`translate(${margin.left},0)`).call(d3.axisLeft(y).tickSize(0).tickPadding(8)).select(".domain").remove();
  svg.append("g").attr("class","axis").attr("transform",`translate(0,${H-margin.bottom})`).call(d3.axisBottom(x).ticks(8).tickFormat(d => d.toFixed(3)));
  svg.append("text").attr("x",(margin.left + W - margin.right)/2).attr("y",H-4).attr("text-anchor","middle").attr("font-size",12).attr("fill","#555555").text("xG per Shot");

  const tooltip = d3.select("#tooltip"), barsG = svg.append("g");
  const subH = y.bandwidth() / 2;

  teams.forEach(team => {
    // Offensive bar (top half, green)
    barsG.append("rect").attr("x", x(0)).attr("y", y(team.short)).attr("width", Math.max(0, x(team.offEff) - x(0))).attr("height", subH - 1).attr("rx",2).attr("fill","#16a34a").attr("opacity",0.8).style("cursor","pointer")
      .on("mouseover", event => { tooltip.html(effTT(team, cats, dataKey)).style("opacity",1); moveTooltip(event); }).on("mousemove",moveTooltip).on("mouseout",hideTooltip);
    barsG.append("text").attr("x", x(team.offEff) + 4).attr("y", y(team.short) + (subH-1)/2).attr("dy","0.35em").attr("font-size",12).attr("font-weight",600).attr("fill","#16a34a").text(team.offEff.toFixed(4));

    // Defensive bar (bottom half, red)
    barsG.append("rect").attr("x", x(0)).attr("y", y(team.short) + subH).attr("width", Math.max(0, x(team.defEff) - x(0))).attr("height", subH - 1).attr("rx",2).attr("fill","#dc2626").attr("opacity",0.8).style("cursor","pointer")
      .on("mouseover", event => { tooltip.html(effTT(team, cats, dataKey)).style("opacity",1); moveTooltip(event); }).on("mousemove",moveTooltip).on("mouseout",hideTooltip);
    barsG.append("text").attr("x", x(team.defEff) + 4).attr("y", y(team.short) + subH + (subH-1)/2).attr("dy","0.35em").attr("font-size",12).attr("font-weight",600).attr("fill","#dc2626").text(team.defEff.toFixed(4));
  });

  // Legend
  const lg = svg.append("g").attr("transform",`translate(${margin.left}, 6)`);
  lg.append("rect").attr("x",0).attr("width",10).attr("height",10).attr("rx",2).attr("fill","#16a34a").attr("opacity",0.8);
  lg.append("text").attr("x",14).attr("y",9).attr("font-size",13).attr("fill","#555555").text("xG/Shot (Offensive)");
  lg.append("rect").attr("x",160).attr("width",10).attr("height",10).attr("rx",2).attr("fill","#dc2626").attr("opacity",0.8);
  lg.append("text").attr("x",174).attr("y",9).attr("font-size",13).attr("fill","#555555").text("xGA/Shot (Defensive)");

  function effTT(team, cats, dk) {
    let h = `<div class="tt-team">${team.team}</div>`;
    h += `<div style="margin-bottom:6px;font-size:12px;color:#555">Sorted by efficiency differential (xG/Shot \u2212 xGA/Shot)</div>`;
    cats.forEach(c => {
      const d = catData(team._src, dk, c.key);
      const oE = d.shots > 0 ? (d.xG / d.shots) : 0;
      const dE = d.against_shots > 0 ? (d.against_xG / d.against_shots) : 0;
      h += `<div class="tt-row"><span class="tt-label"><span style="color:${c.color}">\u25A0</span> ${c.label}</span><span class="tt-val" style="color:#16a34a">${oE.toFixed(4)}</span></div>`;
      h += `<div class="tt-row"><span class="tt-label" style="padding-left:16px">xGA/Shot</span><span class="tt-val" style="color:#dc2626">${dE.toFixed(4)}</span></div>`;
    });
    h += `<div class="tt-row tt-total"><span class="tt-label">Overall xG/Shot</span><span class="tt-val" style="color:#16a34a">${team.offEff.toFixed(4)} (${team.totalXG.toFixed(1)} xG / ${team.totalShots} sh)</span></div>`;
    h += `<div class="tt-row"><span class="tt-label">Overall xGA/Shot</span><span class="tt-val" style="color:#dc2626">${team.defEff.toFixed(4)} (${team.totalAXG.toFixed(1)} xGA / ${team.totalAShots} sh)</span></div>`;
    const diffCol = team.diff >= 0 ? "#16a34a" : "#dc2626";
    h += `<div class="tt-row" style="font-weight:700"><span class="tt-label">Differential</span><span class="tt-val" style="color:${diffCol}">${(team.diff>0?"+":"") + team.diff.toFixed(4)}</span></div>`;
    return h;
  }
}

// ── Init ────────────────────────────────────────────────────────
redrawActiveTab();
</script>
</body>
</html>"""

with open("index.html", "w") as f:
    f.write(html)
print(f"Wrote index.html ({len(html)} bytes)")
