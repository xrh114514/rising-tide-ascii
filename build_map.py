"""Build the ASCII world map masks from world-atlas TopoJSON (land + country borders).

Downloads (or reads locally):
  land-110m.json      - land polygons
  countries-110m.json - country polygons (for border lines)

Writes worldmap.json: {"w","h","lon0","lon1","lat0","lat1","land":[...rows],"border":[...rows]}
"""
import json
import sys
import urllib.request
from pathlib import Path

MW, MH = 512, 100          # mask resolution (chars)
LON0, LON1 = -180.0, 180.0
LAT0, LAT1 = 83.0, -58.0   # crop Antarctica

URLS = {
    "land-110m.json": "https://cdn.jsdelivr.net/npm/world-atlas@2/land-110m.json",
    "countries-110m.json": "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json",
}


def fetch(name: str) -> dict:
    p = Path(name)
    if not p.exists():
        print(f"downloading {name} ...")
        p.write_bytes(urllib.request.urlopen(URLS[name], timeout=60).read())
    return json.loads(p.read_text(encoding="utf-8"))


def decode_arcs(topo):
    sx, sy = topo["transform"]["scale"]
    tx, ty = topo["transform"]["translate"]
    out = []
    for arc in topo["arcs"]:
        x = y = 0
        pts = []
        for dx, dy in arc:
            x += dx
            y += dy
            pts.append((x * sx + tx, y * sy + ty))
        out.append(pts)
    return out


def ring_points(arcs, ring):
    pts = []
    for idx in ring:
        arc = arcs[~idx][::-1] if idx < 0 else arcs[idx]
        pts.extend(arc[1:] if pts else arc)
    return pts


def iter_rings(topo, arcs):
    """Yield (country_id, outer_ring_points) for every polygon ring."""
    geoms = []
    for obj in topo["objects"].values():
        if obj.get("type") == "GeometryCollection":
            geoms.extend(obj["geometries"])
        else:
            geoms.append(obj)
    for geom in geoms:
        cid = geom.get("id")
        gtype = geom.get("type")
        if gtype == "Polygon":
            polys = [geom["arcs"]]
        elif gtype == "MultiPolygon":
            polys = geom["arcs"]
        else:
            continue
        for poly in polys:
            for ring in poly:
                yield cid, ring_points(arcs, ring)


def rasterize(rings):
    """rings: list of (cid, points). Returns (land_rows, border_rows, cid_rows)."""
    land = [[0] * MW for _ in range(MH)]
    cid_grid = [[-1] * MW for _ in range(MH)]
    boxes = []
    for cid, pts in rings:
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        boxes.append((cid, min(xs), max(xs), min(ys), max(ys), pts))

    def inside(x, y, pts):
        c = False
        j = len(pts) - 1
        for i in range(len(pts)):
            xi, yi = pts[i]
            xj, yj = pts[j]
            if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
                c = not c
            j = i
        return c

    for r in range(MH):
        lat = LAT0 + (LAT1 - LAT0) * (r + 0.5) / MH
        for c in range(MW):
            lon = LON0 + (LON1 - LON0) * (c + 0.5) / MW
            for cid, x0, x1, y0, y1, pts in boxes:
                if lon < x0 or lon > x1 or lat < y0 or lat > y1:
                    continue
                if inside(lon, lat, pts):
                    land[r][c] = 1
                    cid_grid[r][c] = cid if cid is not None else -2
                    break

    border = [[0] * MW for _ in range(MH)]
    for r in range(MH):
        for c in range(MW):
            if not land[r][c]:
                continue
            here = cid_grid[r][c]
            for dr, dc in ((0, 1), (1, 0)):
                rr, cc = r + dr, c + dc
                if 0 <= rr < MH and 0 <= cc < MW and land[rr][cc] and cid_grid[rr][cc] != here:
                    border[r][c] = border[rr][cc] = 1
    return land, border


def rows_to_str(grid):
    return ["".join("#" if v else "." for v in row) for row in grid]


def main():
    land_topo = fetch("land-110m.json")
    land_rings = list(iter_rings(land_topo, decode_arcs(land_topo)))
    print(f"land rings: {len(land_rings)}")

    try:
        c_topo = fetch("countries-110m.json")
        c_rings = list(iter_rings(c_topo, decode_arcs(c_topo)))
        print(f"country rings: {len(c_rings)}")
    except Exception as e:                       # borders are optional
        print("country data unavailable:", e)
        c_rings = []

    land, _ = rasterize(land_rings)
    if c_rings:
        _, border = rasterize(c_rings)
    else:
        border = [[0] * MW for _ in range(MH)]

    out = Path("worldmap.json")
    out.write_text(json.dumps({
        "w": MW, "h": MH,
        "lon0": LON0, "lon1": LON1, "lat0": LAT0, "lat1": LAT1,
        "land": rows_to_str(land), "border": rows_to_str(border),
    }), encoding="utf-8")
    print(f"wrote {out} ({MW}x{MH})")
    if "--print" in sys.argv:
        for row in rows_to_str(land):
            print(row.replace(".", " "))


if __name__ == "__main__":
    main()
