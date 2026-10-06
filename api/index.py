from flask import Flask, jsonify, request, render_template_string

app = Flask(__name__)

LOCATIONS = {
    "main_gate": {"name": "Main Gate", "x": 12, "y": 78},
    "admin": {"name": "Admin Block", "x": 28, "y": 62},
    "library": {"name": "Central Library", "x": 48, "y": 48},
    "academic": {"name": "Academic Block", "x": 68, "y": 38},
    "labs": {"name": "Lab Complex", "x": 84, "y": 28},
    "cafeteria": {"name": "Cafeteria", "x": 42, "y": 68},
    "auditorium": {"name": "Auditorium", "x": 62, "y": 58},
    "hostel": {"name": "Hostel", "x": 22, "y": 88},
    "sports": {"name": "Sports Complex", "x": 78, "y": 82},
    "parking": {"name": "Parking Lot", "x": 8, "y": 52},
}

# Predefined walking routes: (from, to, minutes, meters)
EDGES = [
    ("main_gate", "parking", 3, 180),
    ("main_gate", "admin", 4, 250),
    ("main_gate", "hostel", 5, 320),
    ("parking", "admin", 3, 200),
    ("admin", "library", 4, 240),
    ("admin", "cafeteria", 3, 190),
    ("library", "academic", 3, 210),
    ("library", "cafeteria", 4, 230),
    ("library", "auditorium", 3, 180),
    ("academic", "labs", 3, 200),
    ("academic", "auditorium", 4, 220),
    ("cafeteria", "auditorium", 3, 170),
    ("cafeteria", "hostel", 5, 300),
    ("cafeteria", "sports", 6, 380),
    ("auditorium", "sports", 5, 310),
    ("hostel", "sports", 7, 450),
    ("labs", "auditorium", 5, 290),
]


def build_graph():
    graph = {key: [] for key in LOCATIONS}
    for src, dst, minutes, meters in EDGES:
        graph[src].append((dst, minutes, meters))
        graph[dst].append((src, minutes, meters))
    return graph


GRAPH = build_graph()


def shortest_path(start, end):
    if start not in GRAPH or end not in GRAPH:
        return None
    if start == end:
        return {
            "path": [start],
            "minutes": 0,
            "meters": 0,
            "steps": [],
        }

    dist = {node: (float("inf"), float("inf")) for node in GRAPH}
    dist[start] = (0, 0)
    prev = {node: None for node in GRAPH}
    visited = set()
    queue = list(GRAPH.keys())

    while queue:
        current = min(queue, key=lambda n: dist[n][0])
        queue.remove(current)
        visited.add(current)
        if current == end:
            break
        cur_min, cur_m = dist[current]
        for neighbor, minutes, meters in GRAPH[current]:
            if neighbor in visited:
                continue
            new_min = cur_min + minutes
            new_m = cur_m + meters
            if new_min < dist[neighbor][0]:
                dist[neighbor] = (new_min, new_m)
                prev[neighbor] = current

    if dist[end][0] == float("inf"):
        return None

    path = []
    node = end
    while node is not None:
        path.append(node)
        node = prev[node]
    path.reverse()

    steps = []
    total_min = 0
    total_m = 0
    for i in range(len(path) - 1):
        a, b = path[i], path[i + 1]
        for neighbor, minutes, meters in GRAPH[a]:
            if neighbor == b:
                steps.append(
                    {
                        "from": LOCATIONS[a]["name"],
                        "to": LOCATIONS[b]["name"],
                        "minutes": minutes,
                        "meters": meters,
                    }
                )
                total_min += minutes
                total_m += meters
                break

    return {
        "path": path,
        "minutes": total_min,
        "meters": total_m,
        "steps": steps,
    }


PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Campus Navigation</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet" />
  <style>
    :root {
      --bg: #07140f;
      --panel: #0e2219;
      --line: #1e4a34;
      --accent: #3dcc8a;
      --accent-2: #f4c95d;
      --text: #e8f6ee;
      --muted: #8fb5a0;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      font-family: Outfit, system-ui, sans-serif;
      color: var(--text);
      background:
        radial-gradient(1200px 500px at 10% -10%, #123526 0%, transparent 55%),
        radial-gradient(900px 400px at 100% 0%, #1a3d28 0%, transparent 50%),
        var(--bg);
    }
    .wrap {
      max-width: 1100px;
      margin: 0 auto;
      padding: 28px 20px 48px;
    }
    h1 { margin: 0 0 6px; font-size: 2rem; letter-spacing: -0.03em; }
    .sub { color: var(--muted); margin-bottom: 24px; }
    .grid {
      display: grid;
      grid-template-columns: 340px 1fr;
      gap: 20px;
    }
    @media (max-width: 860px) {
      .grid { grid-template-columns: 1fr; }
    }
    .card {
      background: color-mix(in srgb, var(--panel) 92%, black);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 18px;
      box-shadow: 0 12px 40px rgba(0,0,0,.28);
    }
    label { display: block; font-size: 0.82rem; color: var(--muted); margin: 10px 0 6px; }
    select, button {
      width: 100%;
      border-radius: 12px;
      border: 1px solid var(--line);
      font: inherit;
    }
    select {
      background: #0a1a13;
      color: var(--text);
      padding: 12px 12px;
    }
    button {
      margin-top: 16px;
      background: linear-gradient(180deg, #47d894, #2db873);
      color: #04210f;
      font-weight: 700;
      padding: 12px;
      cursor: pointer;
      border: 0;
    }
    button:hover { filter: brightness(1.05); }
    .stats {
      display: flex;
      gap: 10px;
      margin-top: 16px;
    }
    .stat {
      flex: 1;
      background: #0a1a13;
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 10px;
    }
    .stat b { display: block; font-size: 1.15rem; }
    .stat span { color: var(--muted); font-size: 0.78rem; }
    .steps { margin: 14px 0 0; padding: 0; list-style: none; }
    .steps li {
      display: flex;
      justify-content: space-between;
      gap: 8px;
      padding: 8px 0;
      border-bottom: 1px dashed var(--line);
      color: var(--muted);
      font-size: 0.92rem;
    }
    .map {
      position: relative;
      min-height: 520px;
      background:
        linear-gradient(rgba(61,204,138,.06) 1px, transparent 1px),
        linear-gradient(90deg, rgba(61,204,138,.06) 1px, transparent 1px),
        #0a1c14;
      background-size: 28px 28px, 28px 28px, auto;
      overflow: hidden;
    }
    svg.routes { position: absolute; inset: 0; width: 100%; height: 100%; }
    .pin {
      position: absolute;
      transform: translate(-50%, -50%);
      text-align: center;
    }
    .dot {
      width: 14px;
      height: 14px;
      margin: 0 auto 4px;
      border-radius: 50%;
      background: #1f6b45;
      border: 2px solid var(--accent);
      box-shadow: 0 0 0 4px rgba(61,204,138,.15);
    }
    .pin.active .dot { background: var(--accent-2); border-color: #fff; }
    .pin.onpath .dot { background: var(--accent); }
    .pin span {
      display: inline-block;
      font-size: 0.72rem;
      background: #07140fcc;
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 2px 8px;
      white-space: nowrap;
    }
    .error { color: #ffb4b4; margin-top: 10px; min-height: 1.2em; }
  </style>
</head>
<body>
  <div class="wrap">
    <h1>Campus Navigation</h1>
    <p class="sub">Find the shortest walking route between campus buildings.</p>
    <div class="grid">
      <section class="card">
        <label for="from">From</label>
        <select id="from"></select>
        <label for="to">To</label>
        <select id="to"></select>
        <button id="go" type="button">Show route</button>
        <div class="stats">
          <div class="stat"><b id="minutes">—</b><span>Minutes</span></div>
          <div class="stat"><b id="meters">—</b><span>Distance</span></div>
          <div class="stat"><b id="stops">—</b><span>Stops</span></div>
        </div>
        <ul class="steps" id="steps"></ul>
        <p class="error" id="error"></p>
      </section>
      <section class="card map" id="map">
        <svg class="routes" id="svg"></svg>
      </section>
    </div>
  </div>
  <script>
    const locations = {{ locations|safe }};
    const edges = {{ edges|safe }};
    const fromEl = document.getElementById("from");
    const toEl = document.getElementById("to");
    const map = document.getElementById("map");
    const svg = document.getElementById("svg");

    function options() {
      const keys = Object.keys(locations);
      fromEl.innerHTML = keys.map(k => `<option value="${k}">${locations[k].name}</option>`).join("");
      toEl.innerHTML = fromEl.innerHTML;
      fromEl.value = "main_gate";
      toEl.value = "labs";
    }

    function drawPins(path = []) {
      map.querySelectorAll(".pin").forEach(n => n.remove());
      Object.entries(locations).forEach(([id, loc]) => {
        const pin = document.createElement("div");
        pin.className = "pin";
        if (path.includes(id)) pin.classList.add("onpath");
        if (id === fromEl.value || id === toEl.value) pin.classList.add("active");
        pin.style.left = loc.x + "%";
        pin.style.top = loc.y + "%";
        pin.innerHTML = `<div class="dot"></div><span>${loc.name}</span>`;
        map.appendChild(pin);
      });
    }

    function drawEdges(path = []) {
      const pairs = new Set();
      for (let i = 0; i < path.length - 1; i++) {
        pairs.add(path[i] + ">" + path[i + 1]);
        pairs.add(path[i + 1] + ">" + path[i]);
      }
      svg.innerHTML = edges.map(([a, b]) => {
        const A = locations[a], B = locations[b];
        const active = pairs.has(a + ">" + b);
        return `<line x1="${A.x}%" y1="${A.y}%" x2="${B.x}%" y2="${B.y}%"
          stroke="${active ? "#f4c95d" : "#1e4a34"}" stroke-width="${active ? 4 : 2}"
          stroke-linecap="round" />`;
      }).join("");
    }

    async function navigate() {
      const error = document.getElementById("error");
      error.textContent = "";
      const res = await fetch(`/navigate?from=${fromEl.value}&to=${toEl.value}`);
      const data = await res.json();
      if (!res.ok) {
        error.textContent = data.error || "Could not find a route.";
        document.getElementById("minutes").textContent = "—";
        document.getElementById("meters").textContent = "—";
        document.getElementById("stops").textContent = "—";
        document.getElementById("steps").innerHTML = "";
        drawEdges([]);
        drawPins([]);
        return;
      }
      document.getElementById("minutes").textContent = data.minutes;
      document.getElementById("meters").textContent = data.meters + " m";
      document.getElementById("stops").textContent = Math.max(data.path.length - 2, 0);
      document.getElementById("steps").innerHTML = data.steps.map(
        s => `<li><span>${s.from} → ${s.to}</span><span>${s.minutes} min · ${s.meters} m</span></li>`
      ).join("");
      drawEdges(data.path);
      drawPins(data.path);
    }

    options();
    drawEdges([]);
    drawPins([]);
    document.getElementById("go").addEventListener("click", navigate);
    navigate();
  </script>
</body>
</html>
"""


@app.get("/")
def home():
    import json

    return render_template_string(
        PAGE,
        locations=json.dumps(LOCATIONS),
        edges=json.dumps([[a, b] for a, b, *_ in EDGES]),
    )


@app.get("/locations")
def locations():
    return jsonify(
        {
            "locations": {
                key: {"id": key, "name": value["name"]}
                for key, value in LOCATIONS.items()
            }
        }
    )


@app.get("/navigate")
def navigate():
    start = request.args.get("from", "")
    end = request.args.get("to", "")
    if start not in LOCATIONS or end not in LOCATIONS:
        return jsonify({"error": "Unknown campus location."}), 400
    result = shortest_path(start, end)
    if result is None:
        return jsonify({"error": "No route between those locations."}), 404
    result["from"] = LOCATIONS[start]["name"]
    result["to"] = LOCATIONS[end]["name"]
    result["path_names"] = [LOCATIONS[node]["name"] for node in result["path"]]
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
