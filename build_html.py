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
  <script src="https://d3js.org/d3.v7.min.js"></script>
  <style>
    :root {
      --bg: #f5f5f0;
      --surface: #ffffff;
      --border: #d0d7de;
      --text: #1f2328;
      --text-muted: #656d76;
      --accent: #0969da;
    }
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      background: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
      padding: 24px;
      min-height: 100vh;
    }
    header { max-width: 1200px; margin: 0 auto 32px; }
    header h1 { font-size: 28px; font-weight: 700; margin-bottom: 6px; }
    header h1 span { color: var(--accent); }
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
    .controls button:hover { border-color: var(--accent); color: var(--accent); }
    .controls button.active {
      background: var(--accent);
      color: #fff;
      border-color: var(--accent);
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
    .axis text { fill: var(--text-muted); font-size: 12px; }
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
      font-size: 20px;
      font-weight: 600;
    }
    .section-subtitle {
      max-width: 1200px;
      margin: -10px auto 16px;
      font-size: 13px;
      color: var(--text-muted);
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
    footer a { color: var(--accent); text-decoration: none; }
  </style>
</head>
<body>

<header>
  <h1>EPL Set Piece <span>xG</span></h1>
  <p>Expected goals from set pieces per Premier League team, broken down by situation type.
     xG data from <a href="https://understat.com" style="color:var(--accent)">Understat</a>,
     set piece counts from the <a href="https://www.premierleague.com" style="color:var(--accent)">Premier League</a>.</p>
</header>

<!-- Controls -->
<div class="controls" id="controls">
  <span class="label">Season:</span>
  <select id="season-select"></select>
  <div class="separator"></div>
  <span class="label">Show:</span>
  <button class="active" data-filter="all">All Set Pieces</button>
  <button data-filter="FromCorner">Corners</button>
  <button data-filter="SetPiece">Set Piece</button>
  <button data-filter="DirectFreekick">Direct FK</button>
  <button data-filter="Penalty">Penalties</button>
</div>

<!-- Chart 1: Total xG created -->
<h2 class="section-title" id="chart1-title">Total Set Piece xG Created</h2>
<p class="section-subtitle" id="chart1-subtitle">Total expected goals created from set pieces per team, sorted highest to lowest</p>
<div class="chart-container" id="chart1-container">
  <svg id="chart1"></svg>
</div>

<!-- Chart 2: Efficiency (for - against) -->
<h2 class="section-title" id="chart2-title">Set Piece Efficiency: xG Created &#8722; Conceded</h2>
<p class="section-subtitle" id="chart2-subtitle">Net set piece xG (positive = create more than they concede from set pieces)</p>
<div class="chart-container" id="chart2-container">
  <svg id="chart2"></svg>
</div>

<!-- Chart 3: xG per Action (efficiency) -->
<h2 class="section-title" id="chart3-title">Set Piece Conversion Efficiency: xG per Action</h2>
<p class="section-subtitle" id="chart3-subtitle">Expected goals generated per set piece taken. Higher = more dangerous from each opportunity.</p>
<div class="chart-container" id="chart3-container">
  <svg id="chart3"></svg>
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

const SITUATIONS = [
  { key: "FromCorner",     label: "Corners",    color: "#f97316" },
  { key: "SetPiece",       label: "Set Piece",  color: "#a78bfa" },
  { key: "DirectFreekick", label: "Direct FK",  color: "#10b981" },
  { key: "Penalty",        label: "Penalties",  color: "#60a5fa" },
];

// Maps Understat situation keys to PL API count field names
const SITUATION_TO_COUNT = {
  "FromCorner": "corners_taken",
  "DirectFreekick": "freekicks_won",
  "Penalty": "penalties_won",
};

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

let activeFilter = "all";
let activeSeason = "2024";

// ── Season dropdown ─────────────────────────────────────────────────
const seasonSelect = d3.select("#season-select");
Object.keys(ALL_DATA).sort((a, b) => +b - +a).forEach(key => {
  seasonSelect.append("option")
    .attr("value", key)
    .text(ALL_DATA[key].season);
});
seasonSelect.property("value", activeSeason);

function getTeams() {
  return ALL_DATA[activeSeason].teams.map(t => ({
    ...t,
    short: SHORT_NAMES[t.team] || t.team,
  }));
}

// Build a lookup of PL counts by team name for current season
function getCountsLookup() {
  const seasonCounts = PL_COUNTS[activeSeason];
  if (!seasonCounts) return {};
  const lookup = {};
  seasonCounts.teams.forEach(t => {
    lookup[t.team] = t;
  });
  return lookup;
}

function redrawAll() {
  const teams = getTeams();
  const seasonLabel = ALL_DATA[activeSeason].season;
  d3.select("header h1").html(`EPL Set Piece <span>xG</span> — ${seasonLabel}`);
  drawBarChart(teams);
  drawEfficiency(teams);
  drawXgPerAction(teams);
}

seasonSelect.on("change", function () {
  activeSeason = this.value;
  redrawAll();
});

d3.selectAll("#controls button[data-filter]").on("click", function () {
  d3.selectAll("#controls button[data-filter]").classed("active", false);
  d3.select(this).classed("active", true);
  activeFilter = d3.select(this).attr("data-filter");
  redrawAll();
});

redrawAll();

// ── Shared tooltip helper ───────────────────────────────────────────
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

// ── Chart 1: Total xG Created (stacked bar) ────────────────────────
function drawBarChart(teamsRaw) {
  const svg = d3.select("#chart1");
  svg.selectAll("*").remove();

  const isAll = activeFilter === "all";
  const activeSituations = isAll ? SITUATIONS : SITUATIONS.filter(s => s.key === activeFilter);
  const filterLabel = isAll ? "All Set Pieces" : activeSituations[0].label;

  d3.select("#chart1-title").text(`Total Set Piece xG Created — ${filterLabel}`);

  const teams = [...teamsRaw].sort((a, b) => {
    const aVal = activeSituations.reduce((s, sit) => s + a[sit.key].xG, 0);
    const bVal = activeSituations.reduce((s, sit) => s + b[sit.key].xG, 0);
    return bVal - aVal;
  });

  const margin = { top: 32, right: 60, bottom: 40, left: 110 };
  const barHeight = 28;
  const gap = 6;
  const width = 1160;
  const height = margin.top + margin.bottom + teams.length * (barHeight + gap);

  svg.attr("viewBox", `0 0 ${width} ${height}`).attr("width", "100%");

  const xMax = d3.max(teams, d => activeSituations.reduce((s, sit) => s + d[sit.key].xG, 0));
  const x = d3.scaleLinear().domain([0, xMax * 1.12]).range([margin.left, width - margin.right]);
  const y = d3.scaleBand()
    .domain(teams.map(d => d.short))
    .range([margin.top, height - margin.bottom])
    .paddingInner(gap / (barHeight + gap));

  svg.append("g").attr("class", "grid").attr("transform", `translate(0,${margin.top})`)
    .call(d3.axisTop(x).ticks(8).tickSize(-(height - margin.top - margin.bottom)).tickFormat(""));

  svg.append("g").attr("class", "axis").attr("transform", `translate(${margin.left},0)`)
    .call(d3.axisLeft(y).tickSize(0).tickPadding(8)).select(".domain").remove();

  svg.append("g").attr("class", "axis").attr("transform", `translate(0,${height - margin.bottom})`)
    .call(d3.axisBottom(x).ticks(8).tickFormat(d => d.toFixed(1)));

  svg.append("text")
    .attr("x", (margin.left + width - margin.right) / 2).attr("y", height - 4)
    .attr("text-anchor", "middle").attr("font-size", 12).attr("fill", "#656d76")
    .text(`Expected Goals (xG) — ${filterLabel}`);

  const tooltip = d3.select("#tooltip");
  const barsG = svg.append("g");

  teams.forEach(team => {
    let offset = 0;
    activeSituations.forEach(sit => {
      const val = team[sit.key].xG;
      barsG.append("rect")
        .attr("x", x(offset)).attr("y", y(team.short))
        .attr("width", Math.max(0, x(offset + val) - x(offset)))
        .attr("height", y.bandwidth()).attr("rx", 3)
        .attr("fill", sit.color).attr("opacity", 0.85)
        .on("mouseover", (event) => {
          let html = `<div class="tt-team">${team.team}</div>`;
          activeSituations.forEach(s => {
            const bold = s.key === sit.key ? "font-weight:700" : "";
            html += `<div class="tt-row" style="${bold}">
              <span class="tt-label"><span style="color:${s.color}">&#9632;</span> ${s.label}</span>
              <span class="tt-val">${team[s.key].xG.toFixed(2)} xG (${team[s.key].goals}g / ${team[s.key].shots}sh)</span>
            </div>`;
          });
          if (isAll) {
            const total = activeSituations.reduce((s, sit) => s + team[sit.key].xG, 0);
            html += `<div class="tt-row tt-total"><span class="tt-label">Total</span><span class="tt-val">${total.toFixed(2)} xG</span></div>`;
          }
          tooltip.html(html).style("opacity", 1);
          moveTooltip(event);
        })
        .on("mousemove", moveTooltip)
        .on("mouseout", hideTooltip);
      offset += val;
    });
    barsG.append("text")
      .attr("x", x(offset) + 6).attr("y", y(team.short) + y.bandwidth() / 2)
      .attr("dy", "0.35em").attr("font-size", 12).attr("font-weight", 600).attr("fill", "#1f2328")
      .text(offset.toFixed(1));
  });

  // Legend in top margin
  if (isAll) {
    const lg = svg.append("g").attr("transform", `translate(${margin.left}, 6)`);
    let lx = 0;
    SITUATIONS.forEach(s => {
      lg.append("rect").attr("x", lx).attr("width", 10).attr("height", 10).attr("rx", 2).attr("fill", s.color).attr("opacity", 0.85);
      lg.append("text").attr("x", lx + 14).attr("y", 9).attr("font-size", 11).attr("fill", "#656d76").text(s.label);
      lx += s.label.length * 7 + 24;
    });
  }
}

// ── Chart 2: Efficiency (for − against) centered on zero ────────────
function drawEfficiency(teamsRaw) {
  const isAll = activeFilter === "all";
  const activeSituations = isAll ? SITUATIONS : SITUATIONS.filter(s => s.key === activeFilter);
  const filterLabel = isAll ? "All Set Pieces" : activeSituations[0].label;

  d3.select("#chart2-title").text(`Set Piece Efficiency — ${filterLabel}`);
  d3.select("#chart2-subtitle").text(`Net xG (created − conceded). Green = positive balance, red = conceding more than creating.`);

  const teams = [...teamsRaw].map(t => {
    const forXG = activeSituations.reduce((s, sit) => s + t[sit.key].xG, 0);
    const againstXG = activeSituations.reduce((s, sit) => s + t[sit.key].against_xG, 0);
    return {
      ...t,
      short: SHORT_NAMES[t.team] || t.team,
      forXG, againstXG,
      net: +(forXG - againstXG).toFixed(2),
    };
  }).sort((a, b) => b.net - a.net);

  const svg = d3.select("#chart2");
  svg.selectAll("*").remove();

  const margin = { top: 12, right: 60, bottom: 40, left: 110 };
  const rowH = 30;
  const width = 1160;
  const height = margin.top + margin.bottom + teams.length * rowH;

  svg.attr("viewBox", `0 0 ${width} ${height}`).attr("width", "100%");

  const absMax = d3.max(teams, d => Math.abs(d.net)) * 1.2;
  const x = d3.scaleLinear().domain([-absMax, absMax]).range([margin.left, width - margin.right]);
  const y = d3.scaleBand()
    .domain(teams.map(d => d.short))
    .range([margin.top, height - margin.bottom])
    .paddingInner(0.25);

  // Grid
  svg.append("g").attr("class", "grid").attr("transform", `translate(0,${margin.top})`)
    .call(d3.axisTop(x).ticks(10).tickSize(-(height - margin.top - margin.bottom)).tickFormat(""));

  // Zero line
  svg.append("line")
    .attr("x1", x(0)).attr("x2", x(0))
    .attr("y1", margin.top).attr("y2", height - margin.bottom)
    .attr("stroke", "#1f2328").attr("stroke-width", 1).attr("stroke-opacity", 0.25);

  // Y axis
  svg.append("g").attr("class", "axis").attr("transform", `translate(${margin.left},0)`)
    .call(d3.axisLeft(y).tickSize(0).tickPadding(8)).select(".domain").remove();

  // X axis
  svg.append("g").attr("class", "axis").attr("transform", `translate(0,${height - margin.bottom})`)
    .call(d3.axisBottom(x).ticks(10).tickFormat(d => (d > 0 ? "+" : "") + d.toFixed(1)));

  svg.append("text")
    .attr("x", (margin.left + width - margin.right) / 2).attr("y", height - 4)
    .attr("text-anchor", "middle").attr("font-size", 12).attr("fill", "#656d76")
    .text(`Net Set Piece xG (Created − Conceded) — ${filterLabel}`);

  const tooltip = d3.select("#tooltip");

  teams.forEach(team => {
    const midY = y(team.short) + y.bandwidth() / 2;
    const positive = team.net >= 0;
    const col = positive ? "#16a34a" : "#dc2626";
    const barX = positive ? x(0) : x(team.net);
    const barW = Math.abs(x(team.net) - x(0));

    // Bar
    svg.append("rect")
      .attr("x", barX).attr("y", y(team.short))
      .attr("width", barW).attr("height", y.bandwidth())
      .attr("rx", 3).attr("fill", col).attr("opacity", 0.75)
      .style("cursor", "pointer")
      .on("mouseover", (event) => {
        let html = `<div class="tt-team">${team.team}</div>`;
        activeSituations.forEach(sit => {
          html += `<div class="tt-row">
            <span class="tt-label"><span style="color:${sit.color}">&#9632;</span> ${sit.label}</span>
            <span class="tt-val">+${team[sit.key].xG.toFixed(2)} / −${team[sit.key].against_xG.toFixed(2)}</span>
          </div>`;
        });
        html += `<div class="tt-row tt-total"><span class="tt-label">xG Created</span><span class="tt-val">${team.forXG.toFixed(2)}</span></div>`;
        html += `<div class="tt-row"><span class="tt-label">xG Conceded</span><span class="tt-val">${team.againstXG.toFixed(2)}</span></div>`;
        html += `<div class="tt-row" style="font-weight:700"><span class="tt-label">Net</span><span class="tt-val" style="color:${col}">${(team.net > 0 ? "+" : "") + team.net.toFixed(2)}</span></div>`;
        tooltip.html(html).style("opacity", 1);
        moveTooltip(event);
      })
      .on("mousemove", moveTooltip)
      .on("mouseout", hideTooltip);

    // Value label
    const labelX = positive ? x(team.net) + 6 : x(team.net) - 6;
    const anchor = positive ? "start" : "end";
    svg.append("text")
      .attr("x", labelX).attr("y", midY).attr("dy", "0.35em")
      .attr("text-anchor", anchor).attr("font-size", 11).attr("font-weight", 600).attr("fill", col)
      .text((team.net > 0 ? "+" : "") + team.net.toFixed(2));
  });
}

// ── Chart 3: xG per Action (efficiency per set piece taken) ─────────
function drawXgPerAction(teamsRaw) {
  const countsLookup = getCountsLookup();
  const hasCounts = Object.keys(countsLookup).length > 0;

  // Determine which efficiency metrics to show based on active filter
  // "SetPiece" from Understat has no direct PL count equivalent, so we exclude it
  // when a specific filter is chosen and it's "SetPiece"
  const EFFICIENCY_TYPES = [
    { key: "FromCorner",     countKey: "corners_taken",   label: "Corners",     color: "#f97316", unit: "corner" },
    { key: "DirectFreekick", countKey: "freekicks_won",   label: "Free Kicks",  color: "#10b981", unit: "FK won" },
    { key: "Penalty",        countKey: "penalties_won",    label: "Penalties",   color: "#60a5fa", unit: "pen" },
  ];

  const isAll = activeFilter === "all";

  // For "SetPiece" filter there's no PL count, show a notice
  if (!isAll && activeFilter === "SetPiece") {
    const svg = d3.select("#chart3");
    svg.selectAll("*").remove();
    d3.select("#chart3-title").text("Set Piece Conversion Efficiency: xG per Action");
    d3.select("#chart3-subtitle").text(
      "No raw count data available for indirect set pieces. Select Corners, Direct FK, Penalties, or All."
    );
    svg.attr("viewBox", "0 0 1160 60").attr("width", "100%");
    svg.append("text")
      .attr("x", 580).attr("y", 35).attr("text-anchor", "middle")
      .attr("font-size", 14).attr("fill", "#656d76")
      .text("Select a different filter to see xG per action.");
    return;
  }

  const activeTypes = isAll ? EFFICIENCY_TYPES : EFFICIENCY_TYPES.filter(e => e.key === activeFilter);
  const filterLabel = isAll ? "All Measurable Set Pieces" : activeTypes[0].label;

  d3.select("#chart3-title").text(`xG per Action — ${filterLabel}`);
  d3.select("#chart3-subtitle").text(
    isAll
      ? "xG generated per set piece taken (corners, free kicks, penalties). Grouped bars show efficiency by type."
      : `xG generated per ${activeTypes[0].unit} — higher = more dangerous from each opportunity.`
  );

  if (!hasCounts) {
    const svg = d3.select("#chart3");
    svg.selectAll("*").remove();
    svg.attr("viewBox", "0 0 1160 60").attr("width", "100%");
    svg.append("text")
      .attr("x", 580).attr("y", 35).attr("text-anchor", "middle")
      .attr("font-size", 14).attr("fill", "#656d76")
      .text("No Premier League count data available for this season.");
    return;
  }

  // Build team data with efficiency values
  const teams = teamsRaw.map(t => {
    const counts = countsLookup[t.team];
    if (!counts) return null;

    const entry = {
      team: t.team,
      short: SHORT_NAMES[t.team] || t.team,
    };

    let totalXG = 0;
    let totalCount = 0;

    activeTypes.forEach(etype => {
      const xg = t[etype.key] ? t[etype.key].xG : 0;
      const count = counts[etype.countKey] || 0;
      const efficiency = count > 0 ? xg / count : 0;
      entry[etype.key] = {
        xG: xg,
        count: count,
        efficiency: efficiency,
        goals: t[etype.key] ? t[etype.key].goals : 0,
        shots: t[etype.key] ? t[etype.key].shots : 0,
      };
      totalXG += xg;
      totalCount += count;
    });

    entry.totalEfficiency = totalCount > 0 ? totalXG / totalCount : 0;
    entry.totalXG = totalXG;
    entry.totalCount = totalCount;

    return entry;
  }).filter(Boolean);

  // Sort by overall efficiency for "all", or by the single type's efficiency
  if (isAll) {
    teams.sort((a, b) => b.totalEfficiency - a.totalEfficiency);
  } else {
    const k = activeTypes[0].key;
    teams.sort((a, b) => b[k].efficiency - a[k].efficiency);
  }

  const svg = d3.select("#chart3");
  svg.selectAll("*").remove();

  const margin = { top: 32, right: 80, bottom: 40, left: 110 };
  const groupHeight = isAll ? 50 : 28;
  const gap = isAll ? 10 : 6;
  const width = 1160;
  const height = margin.top + margin.bottom + teams.length * (groupHeight + gap);

  svg.attr("viewBox", `0 0 ${width} ${height}`).attr("width", "100%");

  // X scale based on max efficiency
  let xMax;
  if (isAll) {
    xMax = d3.max(teams, d => d3.max(activeTypes, et => d[et.key].efficiency));
  } else {
    xMax = d3.max(teams, d => d[activeTypes[0].key].efficiency);
  }
  xMax = Math.max(xMax * 1.15, 0.01);

  const x = d3.scaleLinear().domain([0, xMax]).range([margin.left, width - margin.right]);
  const y = d3.scaleBand()
    .domain(teams.map(d => d.short))
    .range([margin.top, height - margin.bottom])
    .paddingInner(gap / (groupHeight + gap));

  // Grid
  svg.append("g").attr("class", "grid").attr("transform", `translate(0,${margin.top})`)
    .call(d3.axisTop(x).ticks(8).tickSize(-(height - margin.top - margin.bottom)).tickFormat(""));

  // Y axis
  svg.append("g").attr("class", "axis").attr("transform", `translate(${margin.left},0)`)
    .call(d3.axisLeft(y).tickSize(0).tickPadding(8)).select(".domain").remove();

  // X axis
  svg.append("g").attr("class", "axis").attr("transform", `translate(0,${height - margin.bottom})`)
    .call(d3.axisBottom(x).ticks(8).tickFormat(d => d.toFixed(3)));

  svg.append("text")
    .attr("x", (margin.left + width - margin.right) / 2).attr("y", height - 4)
    .attr("text-anchor", "middle").attr("font-size", 12).attr("fill", "#656d76")
    .text(`xG per Action — ${filterLabel}`);

  const tooltip = d3.select("#tooltip");
  const barsG = svg.append("g");

  if (isAll) {
    // Grouped bars: one sub-bar per efficiency type within each team band
    const subBarHeight = y.bandwidth() / activeTypes.length;

    teams.forEach(team => {
      activeTypes.forEach((etype, i) => {
        const eff = team[etype.key].efficiency;
        const barY = y(team.short) + i * subBarHeight;

        barsG.append("rect")
          .attr("x", x(0)).attr("y", barY)
          .attr("width", Math.max(0, x(eff) - x(0)))
          .attr("height", subBarHeight - 1).attr("rx", 2)
          .attr("fill", etype.color).attr("opacity", 0.85)
          .style("cursor", "pointer")
          .on("mouseover", (event) => {
            let html = `<div class="tt-team">${team.team}</div>`;
            activeTypes.forEach(et => {
              const d = team[et.key];
              const bold = et.key === etype.key ? "font-weight:700" : "";
              html += `<div class="tt-row" style="${bold}">
                <span class="tt-label"><span style="color:${et.color}">&#9632;</span> ${et.label}</span>
                <span class="tt-val">${d.efficiency.toFixed(4)} xG/${et.unit}</span>
              </div>`;
              html += `<div class="tt-row" style="font-size:11px;${bold}">
                <span class="tt-label" style="padding-left:16px">${d.xG.toFixed(2)} xG from ${d.count} ${et.unit}s</span>
                <span class="tt-val">${d.goals}g / ${d.shots}sh</span>
              </div>`;
            });
            html += `<div class="tt-row tt-total" style="font-weight:700">
              <span class="tt-label">Overall</span>
              <span class="tt-val">${team.totalEfficiency.toFixed(4)} xG/action (${team.totalCount} total)</span>
            </div>`;
            tooltip.html(html).style("opacity", 1);
            moveTooltip(event);
          })
          .on("mousemove", moveTooltip)
          .on("mouseout", hideTooltip);

        // Value label for each sub-bar
        barsG.append("text")
          .attr("x", x(eff) + 4).attr("y", barY + (subBarHeight - 1) / 2)
          .attr("dy", "0.35em").attr("font-size", 10).attr("font-weight", 600).attr("fill", etype.color)
          .text(eff.toFixed(4));
      });
    });
  } else {
    // Single bar per team
    const etype = activeTypes[0];
    teams.forEach(team => {
      const eff = team[etype.key].efficiency;

      barsG.append("rect")
        .attr("x", x(0)).attr("y", y(team.short))
        .attr("width", Math.max(0, x(eff) - x(0)))
        .attr("height", y.bandwidth()).attr("rx", 3)
        .attr("fill", etype.color).attr("opacity", 0.85)
        .style("cursor", "pointer")
        .on("mouseover", (event) => {
          const d = team[etype.key];
          let html = `<div class="tt-team">${team.team}</div>`;
          html += `<div class="tt-row"><span class="tt-label">${etype.label} taken</span><span class="tt-val">${d.count}</span></div>`;
          html += `<div class="tt-row"><span class="tt-label">xG from ${etype.label.toLowerCase()}</span><span class="tt-val">${d.xG.toFixed(2)}</span></div>`;
          html += `<div class="tt-row"><span class="tt-label">Goals / Shots</span><span class="tt-val">${d.goals} / ${d.shots}</span></div>`;
          html += `<div class="tt-row tt-total" style="font-weight:700"><span class="tt-label">xG per ${etype.unit}</span><span class="tt-val" style="color:${etype.color}">${d.efficiency.toFixed(4)}</span></div>`;
          tooltip.html(html).style("opacity", 1);
          moveTooltip(event);
        })
        .on("mousemove", moveTooltip)
        .on("mouseout", hideTooltip);

      barsG.append("text")
        .attr("x", x(eff) + 6).attr("y", y(team.short) + y.bandwidth() / 2)
        .attr("dy", "0.35em").attr("font-size", 11).attr("font-weight", 600).attr("fill", "#1f2328")
        .text(eff.toFixed(4));
    });
  }

  // Legend in top margin (grouped mode only)
  if (isAll) {
    const lg = svg.append("g").attr("transform", `translate(${margin.left}, 6)`);
    let lx = 0;
    activeTypes.forEach(et => {
      lg.append("rect").attr("x", lx).attr("width", 10).attr("height", 10).attr("rx", 2).attr("fill", et.color).attr("opacity", 0.85);
      lg.append("text").attr("x", lx + 14).attr("y", 9).attr("font-size", 11).attr("fill", "#656d76").text(`${et.label} (xG/${et.unit})`);
      lx += (et.label.length + et.unit.length + 6) * 6.5 + 30;
    });
  }
}
</script>
</body>
</html>"""

with open("index.html", "w") as f:
    f.write(html)
print(f"Wrote index.html ({len(html)} bytes)")
