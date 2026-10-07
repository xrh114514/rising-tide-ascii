"""Scenes 1-3: global situation monitor, title re-index, war games."""
import math

from engine import (
    W, H, Canvas, rgb, mix, scale, red, green, blue, rng, hash2, clamp, lerp,
    ease_out, ease_in, beat_pulse, big_text_cells, big_text_width,
    map_cell, equirect, shot_index, cut_effect,
    DIM, MAIN, DATA, BRIGHT, ALERT, WARN, GREEN, VIOLET, AMBER, WHITE,
)
import chronicle

# ------------------------------------------------------------------ data
TELEGRAMS = [
    "1945-02-04  YALTA CONFERENCE // THREE POWERS DIVIDE THE POSTWAR ORDER",
    "1946-03-05  FULTON MO // IRON CURTAIN SPEECH TRANSMITTED",
    "1947-03-12  TRUMAN DOCTRINE // CONTAINMENT POLICY DECLARED",
    "1947-06-05  MARSHALL PLAN // EUROPEAN RECONSTRUCTION FUNDS AUTHORIZED",
    "1948-06-24  BERLIN BLOCKADE // LAND ACCESS CUT // AIRLIFT AUTHORIZED",
    "1949-04-04  NORTH ATLANTIC TREATY SIGNED // NATO ESTABLISHED",
    "1949-08-29  SEMIPALATINSK // SOVIET ATOMIC DEVICE DETECTED",
    "1950-06-25  KOREAN PENINSULA // CONVENTIONAL WAR RESUMED",
    "1952-11-01  ENIWETOK // THERMONUCLEAR DEVICE TESTED",
    "1955-05-14  WARSAW PACT SIGNED // OPPOSING ALLIANCE FORMED",
    "1956-10-23  BUDAPEST // UPRISING SUPPRESSED BY SOVIET FORCES",
    "1957-10-04  SPUTNIK-1 // FIRST ARTIFICIAL SATELLITE IN ORBIT",
    "1958-11-27  BERLIN ULTIMATUM // DEADLINE SET FOR WESTERN WITHDRAWAL",
    "1961-08-13  BERLIN // DIVIDING BARRIERS ERECTED OVERNIGHT",
    "1962-10-16  CARIBBEAN // MISSILE SITES IDENTIFIED BY U-2 RECONNAISSANCE",
    "1962-10-28  CARIBBEAN CRISIS // MISSILES WITHDRAWN // HOTLINE PROPOSED",
    "1963-08-05  MOSCOW // LIMITED TEST BAN TREATY SIGNED",
    "1968-07-01  NUCLEAR NON-PROLIFERATION TREATY OPENED FOR SIGNATURE",
    "1972-05-26  SALT I AGREEMENT // ABM TREATY SIGNED",
    "1975-07-17  APOLLO-SOYUZ // CREWS DOCK IN EARTH ORBIT",
    "1979-06-18  SALT II SIGNED // STRATEGIC ARMS LIMITED",
    "1983-09-01  KAL-007 // CIVIL AIRCRAFT DOWNED AFTER AIRSPACE INCURSION",
    "1986-04-26  CHERNOBYL // REACTOR ACCIDENT // CROSS-BORDER CONCERN",
    "1987-06-12  BRANDENBURG GATE // PUBLIC ADDRESS ON THE WALL",
    "1989-11-09  BERLIN // CROSSINGS OPEN // BARRIERS BREACHED",
    "1990-10-03  GERMAN REUNIFICATION // DIVIDING LINE ABOLISHED",
    "1991-07-01  START I TREATY // STRATEGIC ARMS REDUCED",
    "1991-12-25  SOVIET UNION // FEDERATION DISSOLVED // FLAG LOWERED",
]

BASES = [
    # (lon, lat, label, side)
    (-68.8, 76.5, "THULE", 0), (-104.8, 38.8, "OFFUTT", 0),
    (-95.4, 41.3, "OFFUTT AFB", 0), (-100.7, 48.4, "MINOT AFB", 0),
    (-85.8, 38.7, "WRIGHT-PAT", 0), (7.6, 49.4, "RAMSTEIN", 0),
    (12.6, 45.9, "AVIANO", 0), (32.7, 39.9, "INCIRLIK", 0),
    (-1.3, 51.4, "GREENHAM", 0), (127.8, 26.3, "KADENA", 0),
    (144.8, 13.5, "ANDERSEN", 0), (72.4, -7.3, "DIEGO GARCIA", 0),
    (-84.5, 30.5, "ELGIN AFB", 0), (-118.1, 34.1, "NORAD WEST", 0),
    (37.6, 55.7, "MOSCOW", 1), (39.8, 64.5, "SEVERODVINSK", 1),
    (40.6, 62.9, "PLESETSK", 1), (63.3, 48.0, "BAIKONUR", 1),
    (131.9, 43.1, "VLADIVOSTOK", 1), (77.8, 64.5, "DUDINKA", 1),
    (78.0, 50.3, "SEMIPALATINSK", 1), (23.5, 54.7, "KLAIPEDA", 1),
    (109.5, 13.0, "CAM RANH", 1), (28.0, 50.4, "KIEV MD", 1),
]

LOG_WARGAME = [
    "> WARGAME 7224-F // CENTRAL EUROPEAN THEATER",
    "> TERRAIN LOAD: ELEV GRID 250M // WINTER",
    "> OPLAN 7224 EXEC // PHASE I MOBILIZATION",
    "> 3/33 AR ADVANCE -> GR 32U QR 4471 2093",
    "> 11 ACR SCREEN LINE // FULDA CORRIDOR",
    "> ENEMY 8TH GUARDS AR MOVING WEST",
    "> ARTILLERY FIRE MISSION // GRID 32U PR 8812 4410",
    "> P(DEFENSE HOLD) = 0.4127 ... RECOMPUTING",
    "> P(DEFENSE HOLD) = 0.5372 // CONFIDENCE 0.62",
    "> SUPPLY ROUTE BRAVO // FLOW 78% // INTERDICTED",
    "> AIR SUPPORT REQUEST // ETA 4 MIN",
    "> TARGET LOCK // T-55 COMPANY // GRID 32U QR 3320 5521",
    "> COMBAT POWER RATIO 1.27 : 1 // NATO",
    "> WEATHER: SNOW / VIS 800M / WIND 240/12",
    "> SIM STEP 0x2F91 // RESOLUTION COMPLETE",
    "> CASUALTY ESTIMATE 30 DAYS: 41200 / 43800",
    "> RESERVES COMMITTED // 2 DIVISIONS",
    "> RADIO TRAFFIC: HIGH // 4471 MSG / MIN",
    "> RECALCULATING ENTIRE BATTLEFIELD ...",
    "> COMPUTER ASSISTED TACTICAL SIMULATION RUNNING",
]

OOB = [
    ("ARMOR", 1284, 1311), ("INFANTRY", 3551, 3620), ("ARTILLERY", 780, 812),
    ("AIR DEFENSE", 244, 251), ("TACTICAL AIR", 412, 388), ("ENGINEER", 96, 104),
    ("HELO", 188, 172), ("LOGISTICS", 2201, 2260),
]


def _wrap(s, w):
    out, cur = [], ""
    for word in s.split(" "):
        if cur and len(cur) + 1 + len(word) > w:
            out.append(cur)
            cur = word
        else:
            cur = (cur + " " + word) if cur else word
    if cur:
        out.append(cur)
    return out


# ------------------------------------------------------------------ shared
def draw_map_grid(cv, x0, y0, w, h, t, jitter=0.0, ocean=".",
                  win=(-180.0, 180.0, 83.0, -58.0)):
    """Equirectangular world map into the given rect, with bloc tinting.

    Land is kept bright and stable so the continents read; ocean stays almost
    empty except for graticules and slow drifting data noise.  `win` is the
    (lon0, lon1, lat0, lat1) camera window used for shot changes.
    """
    scan = (t * 6.0) % (w + 20) - 10
    for ry in range(h):
        for rx in range(w):
            lon = win[0] + (rx + 0.5) / w * (win[1] - win[0])
            lat = win[2] + (ry + 0.5) / h * (win[3] - win[2])
            land, border, coast = map_cell(lon, lat)
            hx = hash2(rx + x0, ry + y0, 7)
            if land:
                bloc = 0
                if 12.0 < lon < 180.0 and 35.0 < lat < 78.0:
                    bloc = 1
                elif -85.0 < lon < -74.0 and 18.0 < lat < 23.0:
                    bloc = 1
                elif (-170.0 < lon < -50.0 and 25.0 < lat < 75.0) or \
                     (-10.0 < lon < 20.0 and 36.0 < lat < 61.0) or \
                     (26.0 < lon < 45.0 and 36.0 < lat < 42.0):
                    bloc = 0
                else:
                    bloc = 2
                base = [mix(MAIN, BRIGHT, 0.55), mix(ALERT, WARN, 0.6),
                        mix(DATA, MAIN, 0.65)][bloc]
                if coast:
                    c, col = "+", mix(base, BRIGHT, 0.75)
                elif border and hash2(rx, ry, 3) > 0.45:
                    c, col = ":", mix(base, BRIGHT, 0.35)      # 虚线国界
                else:
                    c = "#"
                    shimmer = 0.5 + 0.5 * math.sin(t * 1.1 + hx * 9.0 + rx * 0.11)
                    col = mix(base, BRIGHT, 0.10 + 0.22 * shimmer)
                # sparse live cells flickering on the landmass
                if jitter > 0 and hash2(rx, ry, int(t * 3.0)) < jitter * 0.008:
                    c = "01#+*:"[int(hash2(rx, ry, int(t * 9)) * 6) % 6]
                    col = mix(col, BRIGHT, 0.55)
            else:
                if rx % 20 == 0 or ry % 14 == 0:
                    c, col = ".", scale(DIM, 1.15)
                else:
                    n = hash2(rx, ry, int(t * 1.6) % 3 + 31)
                    if n > 0.04:
                        c, col = " ", 0
                    else:
                        c = "0123456789:/\\|+*"[int(n * 300) % 16]
                        col = scale(DATA, 0.35 + n * 3.0)
            # slow scan wave sweeping the map
            d = abs(rx - scan)
            if d < 3.0 and c != " ":
                col = mix(col, BRIGHT, (1.0 - d / 3.0) * 0.35)
            cv.set(x0 + rx, y0 + ry, c, col)


def draw_radar(cv, cx, cy, rad, t, speed=1.0, col=None, phase=0.0):
    col = col or mix(GREEN, BRIGHT, 0.2)
    ang = (t * speed * 0.9 + phase) % (2 * math.pi)
    for k in range(3):
        r = rad * (0.32 + 0.32 * k)
        for i in range(72):
            a = i * math.pi / 36
            cv.set(int(cx + math.cos(a) * r), int(cy + math.sin(a) * r * 0.5),
                   "." if k < 2 else ":", scale(col, 0.26 + 0.08 * k))
    for i in range(int(rad) + 1):
        fade = 1.0 - i / max(1.0, rad)
        cv.set(int(cx + math.cos(ang) * i), int(cy + math.sin(ang) * i * 0.5),
               "*" if i > rad * 0.55 else "-", mix(col, BRIGHT, fade * 0.6))
    for i in range(int(rad * 0.55)):
        a = ang - 0.35
        cv.set(int(cx + math.cos(a) * i), int(cy + math.sin(a) * i * 0.5),
               ".", scale(col, 0.5))


def draw_track(cv, pts, head_char, col, trail=".", head_col=None):
    for (x, y) in pts[:-1]:
        cv.set(int(x), int(y), trail, scale(col, 0.42))
    if pts:
        cv.set(int(pts[-1][0]), int(pts[-1][1]), head_char, head_col or col)


# ------------------------------------------------------------------ 阵营徽标
def draw_nato_emblem(cv, cx, cy, r, col, t):
    """北约徽：罗盘玫瑰（圆环 + 四角星），字符画。"""
    x_r, y_r = r * 2.0, r * 1.0            # 字符格 1:2 比例补偿
    for i in range(72):
        a = i * math.pi / 36
        cv.set(int(cx + math.cos(a) * x_r), int(cy + math.sin(a) * y_r), ".", scale(col, 0.85))
        cv.set(int(cx + math.cos(a) * (x_r - 2)), int(cy + math.sin(a) * (y_r - 1)),
               ".", scale(col, 0.5))
    for d in range(int(x_r)):
        for s in (1, -1):
            cv.set(int(cx + s * d), int(cy), "#" if d < x_r * 0.55 else "*",
                   mix(col, BRIGHT, 0.5))
    for d in range(int(y_r)):
        for s in (1, -1):
            cv.set(int(cx), int(cy + s * d), "#" if d < y_r * 0.55 else "*",
                   mix(col, BRIGHT, 0.5))
    for d in range(1, int(x_r * 0.45)):
        for sx, sy in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
            cv.set(int(cx + sx * d), int(cy + sy * d * 0.5), ".", scale(col, 0.85))
    cv.set(int(cx), int(cy), "O", mix(col, BRIGHT, 0.6))
    cv.text(int(cx) - 2, int(cy + y_r) + 1, "NATO", scale(col, 0.95))
    cv.text(int(cx) - 2, int(cy + y_r) + 2, "1949", scale(col, 0.7))


def draw_pact_emblem(cv, cx, cy, r, col, t):
    """华约徽：五角星 + 橄榄枝，字符画。"""
    x_r, y_r = r * 1.8, r * 0.95
    for ry in range(-int(y_r) - 1, int(y_r) + 2):
        for rx in range(-int(x_r) - 1, int(x_r) + 2):
            dx = rx / x_r
            dy = ry / y_r
            d = math.hypot(dx, dy)
            if d > 1.02:
                continue
            ang = math.atan2(dy, dx)
            std = math.cos(math.pi / 5) / math.cos((ang % (2 * math.pi / 5)) - math.pi / 5)
            bound = 0.42 + (std - 0.809) * 3.04        # 五星锐化：谷径 0.42、峰径 1.0
            edge = abs(d - bound) < 0.14
            if d < bound:
                cv.set(int(cx + rx), int(cy + ry), "+" if edge else "#",
                       mix(col, BRIGHT, 0.5 if edge else 0.38))
            elif edge:
                cv.set(int(cx + rx), int(cy + ry), ".", scale(col, 0.8))
    for side in (-1, 1):
        for k in range(9):
            f = k / 8.0
            a = math.pi * (0.88 - 0.62 * f)
            x = cx + side * math.cos(a) * x_r * 0.92
            y = cy + y_r * 0.8 + math.sin(a) * y_r * 0.55
            cv.set(int(x), int(y), "<" if side > 0 else ">", scale(col, 0.75))
    cv.text(int(cx) - 5, int(cy + y_r) + 1, "WARSAW PACT", scale(col, 0.95))
    cv.text(int(cx) - 2, int(cy + y_r) + 2, "1955", scale(col, 0.7))


# ------------------------------------------------------------------ scene 1
# 世界地图上的新闻弹窗：真实事件电讯（英文，ASCII 画面内不出现中文）
NEWS = [
    (3.5, 6.5, 18, 5, 48, "NEWS FLASH // FULTON MO", [
        "1946-03-05   WIRE SERVICE",
        "IRON CURTAIN SPEECH DELIVERED",
        "TRANSMITTED TO 40 COUNTRIES",
        "REUTER // 4 EDITIONS RELEASED",
    ]),
    (11.5, 6.5, 78, 6, 50, "NEWS FLASH // BERLIN", [
        "1948-06-24   WIRE SERVICE",
        "LAND ROUTES TO BERLIN CUT",
        "ALLIED AIRLIFT AUTHORIZED",
        "TEMPELHOF // 24H OPERATIONS",
    ]),
    (19.5, 6.5, 24, 17, 52, "NEWS FLASH // KOREA", [
        "1950-06-25   WIRE SERVICE",
        "KOREAN PENINSULA // WAR",
        "UN SECURITY COUNCIL CONVENES",
        "SUPERPOWERS BACK RIVAL SIDES",
    ]),
    (29.5, 3.5, 84, 16, 50, "NEWS FLASH // BERLIN", [
        "1961-08-13   ASSOCIATED PRESS",
        "DIVIDING BARRIERS ERECTED",
        "CROSSINGS SEALED // 96 KM",
    ]),
]


def news_windows(cv, t):
    for (t0, life, x, y, w, title, lines) in NEWS:
        if not (t0 <= t < t0 + life):
            continue
        u = t - t0
        close = clamp((life - u) / 0.5, 0.0, 1.0)
        h = len(lines) + 2
        cv.box(x, y, w, h, title, scale(mix(WARN, BRIGHT, 0.35), close), fill=" ")
        for i, s in enumerate(lines):
            n = int(u * 46 - i * 9)
            if n <= 0:
                continue
            col = mix(WARN, BRIGHT, 0.3) if i == 0 else mix(BRIGHT, MAIN, 0.35)
            cv.text(x + 2, y + 1 + i, s[:min(n, len(s))][: w - 4], scale(col, close))
        blink = math.sin(t * 8) > 0
        nx = x + 2 + min(int(u * 46 - (len(lines) - 1) * 9), len(lines[-1]))
        if u * 46 - (len(lines) - 1) * 9 > 0 and blink:
            cv.set(min(nx, x + w - 2), y + len(lines), "_", scale(GREEN, close))


def scene_monitor(cv, t, st):
    p = clamp(t / 33.0, 0.0, 1.0)
    tension = 0.25 + 0.75 * p
    beat = st.pulse(t)

    # ---- 镜头：时间线提到哪个事件，地图就聚焦到事件发生地
    MX, MY, MW_, MH_ = 12, 4, 136, 25
    FOCUS = [
        (34.2, 44.7, "YALTA // CRIMEA"),
        (12.0, 52.0, "CENTRAL EUROPE // THE CURTAIN"),
        (-77.0, 38.9, "WASHINGTON D.C."),
        (13.4, 52.5, "BERLIN // BLOCKADE"),
        (4.3, 50.8, "BRUSSELS // NATO HQ"),
        (127.0, 37.5, "KOREAN PENINSULA"),
        (21.0, 52.2, "WARSAW // PACT HQ"),
        (13.4, 52.5, "BERLIN // THE WALL"),
    ]
    cuts = [st.snap(x) for x in chronicle.event_times(0, 33)]
    shot = shot_index(t, cuts) - 1          # -1: 首个事件之前为全球视野
    if shot < 0:
        win = (-180.0, 180.0, 83.0, -58.0)
        focus_name = "GLOBAL SITUATION"
        fx = fy = None
        shot_t0 = 0.0
    else:
        lon0, lat0, focus_name = FOCUS[min(shot, len(FOCUS) - 1)]
        shot_t0 = cuts[shot]
        drift = (t - shot_t0) * 0.22
        win = (lon0 - 32 + drift, lon0 + 33 + drift, lat0 + 12, lat0 - 12)
        fx, fy = lon0 + drift, lat0

    def P(lon, lat):
        return equirect(lon, lat, MX, MY, MW_, MH_, *win)

    def in_map(x, y):
        return MX <= x < MX + MW_ and MY <= y < MY + MH_

    draw_map_grid(cv, MX, MY, MW_, MH_, t, jitter=tension, win=win)

    # 地图框 + 经纬刻度
    for x in range(MX - 1, MX + MW_ + 1):
        cv.set(x, MY - 1, "-", DIM)
        cv.set(x, MY + MH_, "-", DIM)
    for y in range(MY - 1, MY + MH_ + 1):
        cv.set(MX - 1, y, "|", DIM)
        cv.set(MX + MW_, y, "|", DIM)
    for lon in range(-180, 181, 30):
        x, _ = P(lon, 0)
        if MX - 1 <= x <= MX + MW_:
            cv.set(int(x), MY - 1, "+", DATA)
            cv.set(int(x), MY + MH_, "+", DATA)
    for lat in (60, 30, 0, -30):
        _, y = P(0, lat)
        if MY - 1 <= y <= MY + MH_:
            cv.set(MX - 1, int(y), "+", DATA)
    cv.text(MX + 2, MY - 1, "[FOCUS: %s]" % focus_name, scale(WARN, 0.85))

    # 事件发生地标记（时间线事件位置）
    if fx is not None:
        px, py = P(fx, fy)
        if in_map(px, py):
            xi, yi = int(px), int(py)
            blink = math.sin(t * 5.0) > -0.2
            col = mix(WARN, BRIGHT, 0.5 if blink else 0.1)
            for d in range(-3, 4):
                if d:
                    cv.set(xi + d, yi, "-", scale(col, 0.8))
                    cv.set(xi, yi + d // 2, "|", scale(col, 0.8))
            cv.set(xi, yi, "X", col)
            cv.text(xi + 2, yi - 2, "EVENT", scale(col, 0.9))
            cv.text(xi + 2, yi + 2, focus_name.split(" // ")[0], scale(col, 0.75))

    # 铁幕线
    for lat in range(36, 59):
        x, y = P(11.5, lat)
        if in_map(x, y) and hash2(lat, int(t * 10), 5) > 0.15:
            cv.set(int(x), int(y), "|", mix(ALERT, WARN, 0.3 + 0.3 * beat))

    # ---- 雷达站
    for (rlon, rlat, rr, sp, col) in (
            (-68.8, 76.5, 13, 1.2, None), (-104.8, 38.8, 11, -0.8, None),
            (37.6, 55.7, 12, 0.6, mix(ALERT, WARN, 0.4))):
        x, y = P(rlon, rlat)
        if in_map(x, y):
            draw_radar(cv, x, y, rr * (MW_ / 136.0) * 1.6, t, sp, col)

    # ---- 基地
    for bi, (lon, lat, label, side) in enumerate(BASES):
        x, y = P(lon, lat)
        if not in_map(x, y):
            continue
        xi, yi = int(x), int(y)
        col = mix(ALERT, WARN, 0.35) if side else mix(MAIN, BRIGHT, 0.35)
        blink = 0.5 + 0.5 * math.sin(t * 2.2 + lon)
        cv.set(xi, yi, "X", mix(col, BRIGHT, blink * 0.7))
        if bi % 2 == int(t * 0.7) % 2:
            if xi < MX + MW_ - len(label) - 1:
                cv.text(xi + 1, yi, label[:12], scale(mix(col, BRIGHT, 0.25 * blink), 0.72))

    # ---- 空中航迹
    paths = [
        ((-140, 55), (-60, 45), 0.055, "B-52"),
        ((-30, 52), (60, 58), 0.042, "U-2"),
        ((20, 45), (120, 40), 0.048, "BEAR"),
        ((150, 20), (60, 10), 0.05, "F-15"),
        ((-120, 25), (-40, 35), 0.06, "B-52"),
    ]
    for (a, b, sp, name) in paths:
        u = (t * sp + hash2(a[0], a[1], 3)) % 1.0
        pts = []
        for k in range(7):
            uu = u - k * 0.035
            if uu < 0:
                break
            x, y = P(a[0] + (b[0] - a[0]) * uu,
                     a[1] + (b[1] - a[1]) * uu + math.sin(uu * 6) * 2)
            if in_map(x, y):
                pts.append((x, y))
        col = mix(WHITE, GREEN if name in ("U-2", "F-15") else ALERT, 0.4)
        draw_track(cv, pts, ">", col, ".")
        if pts:
            cv.text(int(pts[-1][0]) + 1, int(pts[-1][1]) - 1, name, scale(col, 0.7))

    # 舰队
    for i in range(6):
        lon = -160 + i * 62 + math.sin(t * 0.12 + i) * 4
        lat = 20 + (i % 3) * 18 + math.cos(t * 0.1 + i * 2) * 3
        x, y = P(lon, lat)
        if in_map(x, y):
            for k in range(3):
                cv.set(int(x) + k * 2, int(y), "~", scale(MAIN, 0.6))
            cv.set(int(x) + 3, int(y) - 1, "#", scale(MAIN, 0.9))

    # 移动十字准星 + 坐标读数
    cxh = MX + int((t * 5.3) % MW_)
    cyh = MY + int((math.sin(t * 0.7) * 0.5 + 0.5) * (MH_ - 1))
    for d in (-2, -1, 1, 2):
        cv.set(cxh + d, cyh, "-", scale(WARN, 0.7))
        cv.set(cxh, cyh + d, "|", scale(WARN, 0.7))
    cv.set(cxh, cyh, "+", WARN)
    lon_at = win[0] + (cxh - MX + 0.5) / MW_ * (win[1] - win[0])
    lat_at = win[2] + (cyh - MY + 0.5) / MH_ * (win[3] - win[2])
    cv.text(cxh + 3, cyh - 2, "%05.1f %s / %05.1f %s" % (
        abs(lat_at), "N" if lat_at >= 0 else "S",
        abs(lon_at), "E" if lon_at >= 0 else "W"), scale(WARN, 0.75))

    # ---- 阵营徽标：北约 vs 华约（字符画，压在最上层）
    em = clamp((t - 1.5) / 1.5, 0.0, 1.0)
    if em > 0:
        cv.rect_fill(21, 21, 19, 10, " ", 0)
        cv.rect_fill(118, 21, 19, 10, " ", 0)
        draw_nato_emblem(cv, 30, 25, 3.5, scale(mix(MAIN, BRIGHT, 0.55 + 0.25 * beat), em), t)
        draw_pact_emblem(cv, 128, 25, 3.5, scale(mix(ALERT, WARN, 0.55 + 0.25 * beat), em), t)

    # ---- side panels
    cv.box(0, 2, 12, 30, "STATUS", scale(DATA, 0.9))
    defcon = 5 - int(p * 2.2)
    rows = [
        ("DEFCON", str(defcon)),
        ("SAC", "ON ALERT" if p > 0.4 else "READY"),
        ("SILOS", "1054"),
        ("BOOMERS", "41"),
        ("BOMBERS", "%d" % int(520 + 54 * math.sin(t * 0.9))),
        ("ALERT", "%02d:%02d" % (int(t) // 60, int(t) % 60)),
        ("SITES", "18 ACTIVE"),
        ("TRAFFIC", "%05d" % int(4000 + 2600 * math.sin(t * 1.7))),
        ("DEFCON", "WATCH"),
        ("BMEWS", "SEARCH"),
        ("DEW", "NOMINAL" if p < 0.7 else "ALARM"),
        ("SIGNALS", "%05d" % int(8200 + 3200 * math.sin(t * 2.3))),
        ("CIPHER", "RUNNING"),
        ("TREATY", "SALT"),
    ]
    for i, (k, v2) in enumerate(rows):
        y = 4 + i * 2
        cv.text(1, y, k, scale(DATA, 0.85))
        col = ALERT if (k == "DEFCON" and defcon <= 3) else mix(GREEN, WARN, p)
        cv.text_right(10, y + 1, v2, col)

    cv.box(148, 2, 12, 30, "SIGINT", scale(DATA, 0.9))
    r = rng(t, 55)
    for i in range(27):
        y = 4 + i
        s = "".join("0123456789ABCDEF"[r.randrange(16)] for _ in range(10))
        col = scale(DATA, 0.45 + 0.5 * hash2(i, int(t * 3), 1))
        cv.text(149, y, s, col)

    # ---- bottom: telegrams + panels
    cv.box(0, 31, 96, 9, "WIRE TRAFFIC", scale(DATA, 0.9))
    idx = int(t / 2.1)
    for k in range(3):
        i = idx - k
        if 0 <= i < len(TELEGRAMS):
            s = TELEGRAMS[i]
            chars = len(s) if k > 0 else int((t % 2.1) / 2.1 * len(s) * 1.4)
            line = s[:min(chars, len(s))]
            col = mix(MAIN, ALERT, 0.5) if k == 0 else scale(DATA, 0.8 - 0.25 * k)
            cv.text(1, 33 + k * 2, line[:92], col)
    cv.text(1, 38, "> ", scale(GREEN, 0.9))
    cv.set(3 + int((t * 12) % 88), 38, "_", GREEN)

    cv.box(97, 31, 22, 9, "RADAR NET", scale(DATA, 0.9))
    for i in range(6):
        y = 33 + i
        on = 0.35 + 0.65 * (0.5 + 0.5 * math.sin(t * 2 + i * 1.3))
        cv.text(98, y, "SITE %02d " % i, scale(DATA, 0.8))
        bar = int(on * 10)
        cv.text(106, y, "[" + "#" * bar + "-" * (10 - bar) + "]", mix(GREEN, WARN, on))

    cv.box(120, 31, 40, 9, "COMMS", scale(DATA, 0.9))
    r2 = rng(t, 88)
    for i in range(6):
        y = 33 + i
        s = "CH%02d %s %s" % (i, "ENC" if i % 2 else "CLR",
                              "".join("0123456789"[r2.randrange(10)] for _ in range(12)))
        cv.text(121, y, s[:38], scale(DATA, 0.6 + 0.3 * hash2(i, int(t * 4), 2)))

    # ---- 新闻弹窗：小窗口播报真实事件
    news_windows(cv, t)

    # 剪辑点闪烁
    cut_effect(cv, t, cuts)

    # alert banner ramping up
    if p > 0.55:
        blink = math.sin(t * 6.0) > 0
        col = ALERT if blink else scale(ALERT, 0.5)
        cv.box(38, 1, 84, 2, "", col, fill=" ")
        cv.text(40, 1, "!!! STRATEGIC SITUATION UPDATE // ALL WATCH STATIONS REPORTING !!!", col)


# ------------------------------------------------------------------ scene 2
_TITLE_SRC = None


def _title_targets():
    """Particle target cells for the title."""
    cells = []
    w1 = big_text_width("RISING TIDE", 2)
    cells += big_text_cells("RISING TIDE", (W - w1) // 2, 8, 2, 2)
    w2 = big_text_width("COLD WAR", 2)
    cells += big_text_cells("COLD WAR", (W - w2) // 2, 25, 2, 2)
    return cells


def scene_title(cv, t, st):
    global _TITLE_SRC
    u = t - 33.0
    if _TITLE_SRC is None:
        tmp = Canvas()
        scene_monitor(tmp, 32.98, st)
        _TITLE_SRC = (tmp.ch[:], tmp.fg[:])
    src_ch, src_fg = _TITLE_SRC

    targets = _title_targets()
    n_src = W * H
    order = list(range(n_src))
    r = rng(0.0, 999)
    # deterministic shuffle of source cells -> target assignment
    for i in range(n_src - 1, 0, -1):
        j = r.randrange(i + 1)
        order[i], order[j] = order[j], order[i]

    tmap = {}
    for k, src_i in enumerate(order):
        if k < len(targets):
            tmap[src_i] = targets[k]

    cv.clear(" ", 0)
    cx, cy = W / 2, H / 2

    for i in range(n_src):
        c = src_ch[i]
        if c == " ":
            continue
        x0, y0 = i % W, i // W
        h1 = hash2(x0, y0, 3)
        h2 = hash2(x0, y0, 9)
        col = src_fg[i]

        if u < 1.25:                       # burst outward
            e = ease_out(u / 1.25)
            vx = (x0 - cx) * (0.9 + h1) + (h2 - 0.5) * 26
            vy = (y0 - cy) * (0.9 + h2) + (h1 - 0.5) * 16
            x = x0 + vx * e * 0.75
            y = y0 + vy * e * 0.75 + math.sin(u * 7 + h1 * 9) * 1.4
            col = mix(col, BRIGHT, 0.35 * e)
        elif u < 3.1:                      # converge to title
            k = ease_in((u - 1.25) / 1.85)
            e0 = 0.75
            vx = (x0 - cx) * (0.9 + h1) + (h2 - 0.5) * 26
            vy = (y0 - cy) * (0.9 + h2) + (h1 - 0.5) * 16
            bx, by = x0 + vx * e0, y0 + vy * e0
            tgt = tmap.get(i)
            if tgt is None:
                tx = x0 + (h1 - 0.5) * 40
                ty = y0 + (h2 - 0.5) * 26
            else:
                tx, ty, _ = tgt
            x = lerp(bx, tx, k) + math.sin(u * 9 + h1 * 12) * (1 - k) * 2.2
            y = lerp(by, ty, k) + math.cos(u * 8 + h2 * 12) * (1 - k) * 1.4
            col = mix(col, mix(BRIGHT, MAIN, h1 * 0.5), k * 0.8)
        elif u < 5.4:                      # hold the title
            tgt = tmap.get(i)
            if tgt is None:
                continue
            tx, ty, _ = tgt
            jx = math.sin(u * 11 + h1 * 20) * 0.32
            jy = math.cos(u * 9 + h2 * 20) * 0.22
            x, y = tx + jx, ty + jy
            col = mix(BRIGHT, mix(MAIN, WARN, h1), 0.25 + 0.35 * hash2(tx, ty, int(u * 8)))
        else:                               # disperse
            tgt = tmap.get(i)
            if tgt is None:
                continue
            tx, ty, _ = tgt
            d = u - 5.4
            x = tx + (tx - cx) * d * 0.9 + math.sin(h1 * 20 + u * 6) * d * 3
            y = ty + (ty - cy) * d * 0.55 + math.cos(h2 * 20 + u * 6) * d * 2
            col = scale(col, max(0.0, 1.0 - d * 0.8))

        xi, yi = int(x), int(y)
        if 0 <= xi < W and 0 <= yi < H:
            cv.set(xi, yi, c, col)

    # crisp title overlay once settled
    if 2.6 <= u < 5.6:
        glow = 0.75 + 0.25 * math.sin(u * 4.2)
        w1 = big_text_width("RISING TIDE", 2)
        cells = big_text_cells("RISING TIDE", (W - w1) // 2, 8, 2, 2)
        for (x, y, ch) in cells:
            cv.set(x, y, "#", mix(MAIN, BRIGHT, glow))
        w2 = big_text_width("COLD WAR", 2)
        for (x, y, ch) in big_text_cells("COLD WAR", (W - w2) // 2, 25, 2, 2):
            cv.set(x, y, "#", mix(ALERT, WARN, 0.35 + 0.3 * glow))
        cv.text((W - 44) // 2, 22, "COMPOSER: JACK WALL / BIG GIANT CIRCLES", scale(DATA, 0.9))
        cv.text((W - 40) // 2, 23, "// TERMINAL SYSTEM REINDEX COMPLETE", scale(DATA, 0.8))

    if u > 3.2:                              # glitch rows (kept light over the title)
        rr = rng(t, 2024)
        for _ in range(1 + int(1 + 1.4 * (u - 3.2))):
            y = rr.randrange(H)
            off = rr.randrange(-3, 4)
            base = y * W
            rowc = cv.ch[base:base + W]
            rowf = cv.fg[base:base + W]
            cv.ch[base:base + W] = rowc[off:] + rowc[:off]
            cv.fg[base:base + W] = rowf[off:] + rowf[:off]


# ------------------------------------------------------------------ scene 3
# 真实历史事件 -> 战区地图 + 双方扩张（红=苏/华约，蓝=美/北约）
THEATERS = [
    dict(t0=41.5, name="CARIBBEAN // CUBA 1962", win=(-95.2, -64.8, 32.0, 15.0),
         markers=[(-82.4, 22.6, "SAN CRISTOBAL // MRBM", 1),
                  (-84.5, 30.4, "KEY WEST NAS", 0),
                  (-79.9, 22.4, "GUANTANAMO", 0),
                  (-77.0, 24.6, "NAVAL QUARANTINE LINE", 0)],
         arrows=[((-73.5, 27.5), (-79.8, 23.8), 0),
                 ((-87.5, 27.5), (-81.2, 23.2), 0),
                 ((-70.0, 28.5), (-78.0, 25.2), 1)],
         notes=["24 MRBM / IRBM SITES IDENTIFIED", "QUARANTINE ENFORCED BY US NAVY"]),
    dict(t0=50.0, name="SOUTHEAST ASIA // VIETNAM 1965", win=(93.0, 119.8, 23.0, 8.0),
         markers=[(105.85, 21.0, "HANOI", 1), (106.7, 10.8, "SAIGON", 0),
                  (108.2, 16.0, "DA NANG", 0), (106.6, 17.0, "DMZ / 17TH PARALLEL", 1)],
         arrows=[((105.8, 21.2), (106.4, 16.6), 1),
                 ((104.6, 19.5), (105.6, 13.5), 1),
                 ((112.5, 11.5), (108.6, 13.2), 0),
                 ((108.2, 15.8), (107.4, 13.8), 0)],
         notes=["NVA / VIET CONG PUSH SOUTH", "US MARINES LAND AT DA NANG"]),
    dict(t0=58.5, name="CENTRAL EUROPE // PRAGUE 1968", win=(5.5, 30.5, 57.0, 43.0),
         markers=[(14.4, 50.1, "PRAGUE", 1), (13.7, 51.05, "DRESDEN", 1),
                  (11.6, 48.1, "MUNICH", 0), (17.1, 48.2, "BRATISLAVA", 1),
                  (19.0, 47.5, "BUDAPEST", 1)],
         arrows=[((21.0, 50.5), (15.8, 50.2), 1),
                 ((17.5, 54.0), (15.2, 51.2), 1),
                 ((15.5, 45.8), (14.9, 48.6), 1),
                 ((24.5, 48.5), (18.5, 49.2), 1),
                 ((10.2, 49.3), (12.6, 50.1), 0)],
         notes=["OPERATION DANUBE // 5 AXES", "WARSAW PACT: 21 DIVISIONS"]),
    dict(t0=66.0, name="EUROPE // STRATEGIC BALANCE 1972", win=(2.0, 32.0, 57.0, 43.0),
         markers=[(14.4, 50.1, "PRAGUE", 1), (13.4, 52.5, "BERLIN", 0),
                  (11.6, 48.1, "MUNICH", 0), (21.0, 52.2, "WARSAW", 1),
                  (37.6, 55.7, "MOSCOW", 1)],
         arrows=[((10.2, 49.5), (12.8, 50.2), 0)],
         notes=["SALT I + ABM TREATY SIGNED", "LAUNCHERS CAPPED: 1054 / 1618",
                "HOTLINE MOSCOW - WASHINGTON"]),
    dict(t0=73.0, name="CENTRAL ASIA // AFGHANISTAN 1979", win=(48.3, 87.7, 46.0, 24.0),
         markers=[(69.2, 34.5, "KABUL", 1), (66.8, 37.2, "TERMEZ // BORDER", 1),
                  (71.6, 34.0, "PESHAWAR", 0), (69.0, 36.7, "BAGRAM", 1)],
         arrows=[((66.9, 37.2), (69.1, 34.7), 1),
                 ((62.5, 36.4), (65.2, 35.2), 1),
                 ((71.6, 34.0), (70.1, 34.4), 0),
                 ((71.0, 32.6), (70.2, 33.6), 0)],
         notes=["OPERATION STORM-333 // KABUL", "40TH ARMY INVADES FROM TERMEZ",
                "CIA / ISI SUPPLY ROUTES OPEN"]),
]

ARCHIVE_NOTES = [
    (42.5, 6.5, "ARCHIVE NOTE // 1962-10-22", [
        "CARIBBEAN CRISIS // NAVAL QUARANTINE",
        "DEFCON 2 // STRATEGIC FORCES READY",
        "SIM PARAMETER: ALERT +40%"]),
    (51.0, 6.5, "ARCHIVE NOTE // 1965-08-05", [
        "GULF OF TONKIN // ESCALATION",
        "RESERVE COMPONENTS ACTIVATED",
        "SIM PARAMETER: DEPLOYMENT +30%"]),
    (59.5, 6.5, "ARCHIVE NOTE // 1968-08-21", [
        "PRAGUE // WARSAW PACT MOBILIZED",
        "21 DIVISIONS // 5 AXES OF ADVANCE",
        "SIM PARAMETER: TEMPO +25%"]),
    (67.0, 6.5, "ARCHIVE NOTE // 1972-05-26", [
        "SALT I AND ABM TREATY SIGNED",
        "LAUNCHERS CAPPED // VERIFIED",
        "SIM PARAMETER: ARSENAL FREEZE"]),
    (74.0, 4.5, "ARCHIVE NOTE // 1979-12-27", [
        "OPERATION STORM-333 // KABUL",
        "SOVIET 40TH ARMY CROSSES TERMEZ",
        "SIM PARAMETER: INSURGENCY +100%"]),
]


def _unit_sprite(cv, x, y, side, typ, name, col, dim=1.0):
    """7x3 的大号单位标识。"""
    tag = ("N" if side == 0 else "W") + typ
    cv.text(x, y, "+-----+", scale(col, dim))
    cv.text(x, y + 1, "|%s|" % (tag + "  " + name)[:5], scale(col, dim))
    cv.text(x, y + 2, "+-----+", scale(col, dim))


def _tracer(cv, x0, y0, x1, y1, u, col, dim=1.0):
    """抛物线弹道：u 0..1 为弹头进度，虚线为已飞过的轨迹。"""
    for k in range(15):
        f = k / 14.0
        if f > u:
            break
        arc = math.sin(f * math.pi) * 5.5
        x = lerp(x0, x1, f)
        y = lerp(y0, y1, f) - arc
        c = "*" if k == int(u * 14) else ("+" if k % 3 == 0 else ".")
        cv.set(int(x), int(y), c, scale(col, dim * (0.45 + 0.55 * f)))


def _draw_arrow(cv, P, in_map, a, b, side, u, beat, t):
    """扩张箭头：u 为推进进度，箭头/虚线/单位随之前进。"""
    x0, y0 = P(*a)
    x1, y1 = P(*b)
    col = mix(ALERT, WARN, 0.35) if side else mix(MAIN, BRIGHT, 0.35)
    if not (in_map(x0, y0) or in_map(x1, y1)):
        return
    xe = lerp(x0, x1, u)
    ye = lerp(y0, y1, u)
    for k in range(26):
        f = k / 25.0
        x = lerp(x0, xe, f)
        y = lerp(y0, ye, f)
        if in_map(x, y) and k % 3 != 2:
            cv.set(int(x), int(y), "=" if k % 3 else "+", scale(col, 0.45 + 0.5 * f))
    # 箭头头部
    ang = math.atan2(y1 - y0, (x1 - x0) or 0.001)
    for d in range(3):
        for s in (-1, 1):
            x = xe - math.cos(ang) * d * 1.2 + math.cos(ang + s * 2.4) * (2.2 - d * 0.5)
            y = ye - math.sin(ang) * d * 1.2 + math.sin(ang + s * 2.4) * (2.2 - d * 0.5) * 0.5
            if in_map(x, y):
                cv.set(int(x), int(y), "*" if d == 0 else ">", mix(col, BRIGHT, 0.3 + 0.2 * beat))
    # 沿途推进单位
    if u > 0.15:
        _unit_sprite(cv, int(lerp(x0, xe, 0.45)) - 3, int(lerp(y0, ye, 0.45)) - 1,
                     side, "A", "ADV", col, 0.95)


def scene_wargame(cv, t, st):
    beat = st.pulse(t)
    base_y, base_x = 5, 15
    tw, th = 118, 33

    # ---- 镜头：跟随时间线事件切换战区（剪辑点对齐鼓点）
    cuts = [st.snap(x) for x in chronicle.event_times(40, 79)]
    ncut = shot_index(t, cuts)
    ti = max(0, ncut - 1)
    theater = THEATERS[min(ti, len(THEATERS) - 1)]
    if ncut == 0:
        prog = 0.0
    else:
        prog = clamp((t - cuts[ti]) / 5.5, 0.0, 1.0)

    # ---- 战区地图（低噪点 + 高亮地区轮廓，便于辨识）
    draw_map_grid(cv, base_x, base_y, tw, th, t, jitter=0.05, win=theater["win"])
    win0, win1, lat0, lat1 = theater["win"]
    for ry in range(th):
        for rx in range(tw):
            lon = win0 + (rx + 0.5) / tw * (win1 - win0)
            lat = lat0 + (ry + 0.5) / th * (lat1 - lat0)
            land, border, coast = map_cell(lon, lat)
            if not land:
                continue
            i = (base_y + ry) * W + (base_x + rx)
            if coast:
                cv.ch[i] = "+"
                cv.fg[i] = mix(cv.fg[i], BRIGHT, 0.75)
            elif border and hash2(rx, ry, 3) > 0.45:
                cv.ch[i] = ":"
                cv.fg[i] = mix(cv.fg[i], BRIGHT, 0.5)
    # 稀疏坐标网
    for rx in range(0, tw, 12):
        for ry in range(0, th, 8):
            cv.set(base_x + rx, base_y + ry, ".", scale(DIM, 1.15))
        cv.text(base_x + rx, base_y - 1, "%02d" % (rx // 12), scale(WARN, 0.55))
    for ry in range(0, th, 8):
        cv.text(base_x, base_y + ry, "GR%02d" % (ry // 8), scale(WARN, 0.55))

    def P(lon, lat):
        return equirect(lon, lat, base_x, base_y, tw, th, *theater["win"])

    def in_map(x, y):
        return base_x <= x < base_x + tw and base_y <= y < base_y + th

    # ---- 城市/据点标记
    for (lon, lat, name, side) in theater["markers"]:
        x, y = P(lon, lat)
        if not in_map(x, y):
            continue
        col = mix(ALERT, WARN, 0.4) if side else mix(MAIN, BRIGHT, 0.4)
        blink = 0.5 + 0.5 * math.sin(t * 3 + lon)
        cv.set(int(x), int(y), "X", mix(col, BRIGHT, blink * 0.5))
        cv.text(int(x) + 1, int(y), name[:26], scale(col, 0.75))

    # ---- 扩张箭头（红=苏/华约，蓝=美/北约）
    for (a, b, side) in theater["arrows"]:
        _draw_arrow(cv, P, in_map, a, b, side, prog, beat, t)

    # ---- 炮火弹线 + 落点爆炸
    for k, (a, b, side) in enumerate(theater["arrows"][:3]):
        cyc = ((t - 40.0) + k * 1.1) % 3.4
        u = clamp(cyc / 1.5, 0.0, 1.0)
        x0, y0 = P(*a)
        x1, y1 = P(*b)
        gx = lerp(x0, x1, 0.65 + 0.25 * math.sin(t * 0.4 + k))
        gy = lerp(y0, y1, 0.65)
        col = mix(ALERT, WARN, 0.45) if side else mix(MAIN, BRIGHT, 0.45)
        _tracer(cv, x0, y0, gx, gy, u, col, 0.9)
        if u >= 1.0:
            rad = (cyc - 1.5) * 5.5
            if rad < 4.5:
                for a2 in range(12):
                    ang = a2 * math.pi / 6
                    xx = gx + math.cos(ang) * rad * 1.8
                    yy = gy + math.sin(ang) * rad
                    if in_map(xx, yy):
                        cv.set(int(xx), int(yy), "*", mix(ALERT, WARN, 0.5))

    # ---- 目标锁定
    lock = ((t - 42.0) % 9.0)
    if lock < 4.0:
        tx = base_x + 46 + 26 * math.sin(t * 0.53)
        ty = base_y + 16 + 9 * math.sin(t * 0.41)
        blink = math.sin(t * 9) > 0
        col = ALERT if blink else scale(ALERT, 0.55)
        for dx in (-6, 6):
            for dy in (-3, 3):
                cv.set(int(tx) + dx, int(ty) + dy, "+", col)
        for d in range(-5, 6):
            cv.set(int(tx) + d, int(ty) - 3, "-", scale(col, 0.8))
            cv.set(int(tx) + d, int(ty) + 3, "-", scale(col, 0.8))
        cv.text(int(tx) - 7, int(ty) - 4, "TARGET LOCKED", col)

    # ---- 战区说明 + 档案注记
    cv.box(70, 4, 62, 7, theater["name"], scale(mix(WARN, BRIGHT, 0.4), 0.95), fill=" ")
    for i, s in enumerate(theater["notes"]):
        cv.text(72, 5 + i, s[:58], scale(mix(BRIGHT, WARN, 0.2), 0.9))
    cv.text(72, 9, "EXPANSION TRACKS: %d // RED: PACT  BLUE: NATO" % len(theater["arrows"]),
            scale(DATA, 0.85))
    for (t0, life, title, lines) in ARCHIVE_NOTES:
        if not (t0 <= t < t0 + life):
            continue
        u = t - t0
        close = clamp((life - u) / 0.5, 0.0, 1.0)
        cv.box(70, 13, 62, len(lines) + 2, title, scale(mix(WARN, BRIGHT, 0.35), close), fill=" ")
        for i, s in enumerate(lines):
            n = int(u * 52 - i * 10)
            if n > 0:
                cv.text(72, 14 + i, s[:min(n, len(s))][:58],
                        scale(mix(BRIGHT, WARN, 0.25 if i == 2 else 0.0), close))

    # ---- 对抗双方徽标：北约 vs 华约
    cv.rect_fill(17, 21, 19, 11, " ", 0)
    cv.rect_fill(107, 21, 18, 11, " ", 0)
    draw_nato_emblem(cv, 26, 25, 3.5, mix(MAIN, BRIGHT, 0.55 + 0.2 * beat), t)
    draw_pact_emblem(cv, 116, 25, 3.5, mix(ALERT, WARN, 0.55 + 0.2 * beat), t)

    # ---- 左侧战斗序列
    cv.box(0, 2, 14, 37, "OOB", scale(DATA, 0.9))
    for i, (name, a, b) in enumerate(OOB):
        y = 4 + i * 4
        cv.text(1, y, name[:11], scale(DATA, 0.85))
        va = a + int(math.sin(t * 0.7 + i) * 7)
        vb = b + int(math.cos(t * 0.6 + i * 2) * 7)
        cv.text(1, y + 1, "N:%5d" % va, mix(MAIN, BRIGHT, 0.3))
        cv.text(1, y + 2, "W:%5d" % vb, mix(ALERT, WARN, 0.3))
    cv.text(1, 36, "SIM CLOCK", scale(DATA, 0.8))
    cv.text(1, 37, "T+%06.1f" % (t - 40.0), GREEN)

    # ---- 右侧推演日志
    cv.box(134, 2, 26, 37, "EXEC LOG", scale(DATA, 0.9))
    lines = LOG_WARGAME
    for k in range(8):
        i = int((t - 40.0) * 0.62) - k
        if i >= 0:
            s = lines[i % len(lines)]
            chars = len(s) if k > 0 else int(((t - 40.0) * 0.62 - int((t - 40.0) * 0.62)) * len(s) * 1.3)
            col = mix(GREEN, MAIN, 0.3) if k == 0 else scale(DATA, 0.85 - 0.08 * k)
            for j, wl in enumerate(_wrap(s[:min(chars, len(s))], 23)):
                if 4 + k * 4 + j < 37:
                    cv.text(135, 4 + k * 4 + j, wl, col)
    frac = 0.5 + 0.5 * math.sin(t * 0.9)
    cv.text(135, 36, "[" + "#" * int(frac * 22) + "-" * (22 - int(frac * 22)) + "]", scale(WARN, 0.9))
    cv.text(135, 37, "CALC %5.2f%%  STEP %06d" % (frac * 100, int((t - 40) * 24)), scale(DATA, 0.8))

    # ---- 顶部说明 + 战区标识
    cv.text(16, 2, "COMPUTER ASSISTED TACTICAL SIMULATION // THEATER 7224",
            scale(MAIN, 0.85))
    cv.text(16, 3, "MODE: FULL SCALE  RULESET: 1983  SOURCE: DECLASSIFIED ORBAT",
            scale(DATA, 0.8))
    cv.text(80, 3, theater["name"], scale(WARN, 0.85))
    cut_effect(cv, t, cuts)
