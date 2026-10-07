"""底部 chronicle 条：双语字幕 + 历史时间线（lower third）。

字幕风格：年份-事件-历史影响（如 1947-杜鲁门主义-冷战正式开始）。
年份跟随当前画面内容所属的档案年代；各段落读取不同档案时游标跳转（ARCHIVE SEEK）。
每个事件同时是画面的"剪辑点"：场景按事件聚焦事发地区 / 展示真实史料。
空标签条目为档案跳转锚点，只驱动时间轴、不显示字幕。
本区域在 CRT 后处理之后绘制，不受噪点/闪烁/撕裂影响。
"""
import math

from engine import (
    W, H, rgb, mix, scale, clamp, text_auto, width_of,
    MAIN, DATA, BRIGHT, DIM, GREEN, WARN, WHITE, ALERT,
)

# (时间, 年份, 英文, 中文)；空标签 = 档案跳转锚点
EVENTS = [
    # ---- 0:00-0:33 局势监控：1945-1961
    (2.0, 1945, "1945 - YALTA - POSTWAR ORDER DIVIDED", "1945-雅尔塔会议-战后秩序被划分"),
    (6.3, 1946, "1946 - IRON CURTAIN - DIVISION MADE PUBLIC", "1946-铁幕演说-分裂公开化"),
    (10.6, 1947, "1947 - TRUMAN DOCTRINE - THE COLD WAR BEGINS", "1947-杜鲁门主义-冷战正式开始"),
    (14.9, 1948, "1948 - BERLIN BLOCKADE - FIRST CONFRONTATION", "1948-柏林封锁-第一次正面交锋"),
    (19.2, 1949, "1949 - NATO FOUNDED - WESTERN ALLIANCE FORMED", "1949-北约成立-西方军事同盟成形"),
    (23.5, 1950, "1950 - KOREAN WAR - THE COLD WAR TURNS HOT", "1950-朝鲜战争-冷战转为热战"),
    (27.8, 1955, "1955 - WARSAW PACT - TWO ARMED CAMPS", "1955-华约成立-两极武装对峙"),
    (31.5, 1961, "1961 - BERLIN WALL - CURTAIN BECOMES CONCRETE", "1961-柏林墙-铁幕变成混凝土"),
    # ---- 0:40-1:19 兵棋推演：真实军事扩张 1962-1979
    (41.5, 1962, "1962 - CUBAN MISSILE CRISIS - ON THE BRINK", "1962-古巴导弹危机-人类最接近核战"),
    (50.0, 1965, "1965 - VIETNAM WAR - PROXY WAR ESCALATES", "1965-越南战争-代理人战争升级"),
    (58.5, 1968, "1968 - PRAGUE SPRING - BREZHNEV DOCTRINE", "1968-布拉格之春-有限主权论出笼"),
    (66.0, 1972, "1972 - ABM TREATY - NUCLEAR PARITY LOCKED", "1972-反导条约-核均衡被锁定"),
    (73.0, 1979, "1979 - SOVIET INVASION OF AFGHANISTAN", "1979-苏联入侵阿富汗-最后一场征服"),
    (78.3, 1979, "", ""),
    # ---- 1:19-2:07 情报暗战：1953-1962（档案回溯）
    (78.8, 1953, "1953 - EAST BERLIN UPRISING - CRUSHED", "1953-东柏林起义-三日内被镇压"),
    (88.5, 1956, "1956 - HUNGARIAN REVOLUTION - SATELLITE REVOLTS", "1956-匈牙利事件-卫星国的反抗"),
    (96.0, 1958, "1958 - BERLIN ULTIMATUM - BRINKMANSHIP", "1958-柏林最后通牒-核边缘政策"),
    (103.5, 1960, "1960 - U-2 INCIDENT - SUMMIT COLLAPSES", "1960-U2事件-最高层会晤破裂"),
    (111.0, 1961, "1961 - BERLIN WALL - ESCAPE ROUTE CLOSED", "1961-柏林墙-逃亡通道被封死"),
    (118.5, 1961, "1961 - NETWORK COMPROMISED - FILES SEALED", "1961-情报网瓦解-档案永久封存"),
    (125.0, 1962, "1962 - SPY EXCHANGE - THE BRIDGE OF SPIES", "1962-间谍交换-格利尼克桥"),
    (127.4, 1962, "", ""),
    # ---- 2:07-2:38 核与太空：1957-1983
    (127.9, 1957, "1957 - SPUTNIK - THE SPACE AGE BEGINS", "1957-人造卫星-太空时代开启"),
    (133.7, 1961, "1961 - GAGARIN - FIRST HUMAN IN ORBIT", "1961-加加林-人类首次进入太空"),
    (138.9, 1969, "1969 - APOLLO 11 - THE MOON IS REACHED", "1969-阿波罗11号-人类登上月球"),
    (144.1, 1972, "1972 - ABM TREATY - STABILITY THROUGH MAD", "1972-反导条约-相互确保毁灭的平衡"),
    (149.3, 1975, "1975 - ASTP - DETENTE IN ORBIT", "1975-阿波罗联盟对接-轨道上的缓和"),
    (154.5, 1983, "1983 - SDI - THE ARMS RACE RESTARTS", "1983-星球大战计划-军备竞赛再加速"),
    # ---- 2:38-2:55 尾声：1985-1987
    (159.5, 1985, "1985 - REYKJAVIK - DISARMAMENT ON THE TABLE", "1985-雷克雅未克会晤-裁军重回谈判桌"),
    (165.0, 1986, "1986 - CHERNOBYL - DISASTER IGNORES BORDERS", "1986-切尔诺贝利-灾难不认国界"),
    (170.0, 1987, "1987 - INF TREATY - MISSILES ACTUALLY DESTROYED", "1987-中导条约-导弹真的被销毁"),
    # ---- 2:55-结尾 评价：1989-1991
    (176.5, 1989, "1989 - FALL OF THE WALL - THE END IN SIGHT", "1989-柏林墙倒塌-终点在望"),
    (183.0, 1990, "1990 - REUNIFICATION - A NATION REJOINED", "1990-德国统一-分裂国家重归一体"),
    (189.0, 1991, "1991 - SOVIET UNION DISSOLVES", "1991-苏联解体-两极世界终结"),
    (195.5, 1991, "1991 - END OF THE COLD WAR - THE RECORD REMAINS", "1991-冷战结束-历史仍然存在"),
]

ROW_EN, ROW_CN, ROW_AXIS, ROW_TAG = 40, 41, 42, 43
X0, X1 = 8, 152
YEAR0, YEAR1 = 1945.0, 1991.0


def event_times(t0, t1):
    """区间内的字幕事件时刻——也是画面的内容剪辑点。"""
    return [e[0] for e in EVENTS if t0 <= e[0] < t1 and e[2]]


def event_index(t):
    """当前事件序号（跳过档案跳转锚点）。"""
    idx = -1
    for i, (t0, _y, en, _cn) in enumerate(EVENTS):
        if t >= t0:
            if en:
                idx = i
        else:
            break
    return idx


def year_at(t):
    """按事件锚点线性插值出当前年份（含档案跳转）。"""
    if t <= EVENTS[0][0]:
        return float(EVENTS[0][1])
    if t >= EVENTS[-1][0]:
        return float(EVENTS[-1][1])
    for i in range(len(EVENTS) - 1):
        t0, y0 = EVENTS[i][0], EVENTS[i][1]
        t1, y1 = EVENTS[i + 1][0], EVENTS[i + 1][1]
        if t0 <= t <= t1:
            f = (t - t0) / max(1e-6, t1 - t0)
            return y0 + (y1 - y0) * f
    return float(EVENTS[-1][1])


def _year_x(year, x0=X0, x1=X1):
    return x0 + (year - YEAR0) / (YEAR1 - YEAR0) * (x1 - x0)


def draw(cv, t):
    """在画布底部 40-43 行绘制字幕与时间线（干净区域，无噪点无闪烁）。"""
    for y in range(ROW_EN, ROW_TAG + 1):
        for x in range(W):
            cv.set(x, y, " ", 0)

    for x in range(W):
        cv.set(x, ROW_EN - 1, "-" if x % 4 else "+", scale(DIM, 1.1))

    idx = event_index(t)

    if idx >= 0:
        t0, _year, en, cn = EVENTS[idx]
        n_en = int((t - t0) * 34)
        n_cn = int((t - t0) * 26)
        text_auto(cv, 2, ROW_EN, en[:n_en], scale(mix(BRIGHT, WARN, 0.25), 0.95))
        text_auto(cv, 2, ROW_CN, cn[:n_cn], scale(mix(GREEN, WHITE, 0.5), 0.92))

    # ---- 时间轴
    yr = year_at(t)
    yr_prev = year_at(max(0.0, t - 0.7))
    rate = abs(yr - yr_prev) / 0.7
    x_now = _year_x(yr)
    for x in range(X0, X1 + 1):
        cv.set(x, ROW_AXIS, "-", scale(DATA, 0.65))
    for (t0, ey, _en, _cn) in EVENTS:
        x = int(round(_year_x(ey)))
        passed = t >= t0
        cv.set(x, ROW_AXIS, "|" if passed else ".", scale(WARN if passed else DIM, 0.9))
    for y in range(1945, 1992, 5):
        x = int(round(_year_x(y)))
        cv.set(x, ROW_AXIS, "+", scale(DATA, 1.0))
        if y in (1945, 1960, 1975, 1991):
            cv.text(max(X0 - 2, x - 2), ROW_TAG, str(y), scale(DATA, 0.8))
    xi = int(round(x_now))
    for d in range(-1, 2):
        if 0 <= xi + d < W:
            cv.set(xi + d, ROW_AXIS, ">" if d == 1 else ("=" if d == 0 else "<"),
                   mix(WARN, BRIGHT, 0.4))

    text_auto(cv, 2, ROW_TAG, "YEAR %d" % int(yr), scale(mix(WARN, BRIGHT, 0.4), 1.0))
    if rate > 4.0:
        tag = ">> ARCHIVE SEEK  %d -> %d" % (int(yr_prev), int(yr))
        cv.text_right(W - 2, ROW_TAG, tag, scale(mix(ALERT, WARN, 0.4), 1.0))
    elif idx >= 0:
        tag = "ARCHIVE %02d/%02d" % (idx + 1, sum(1 for e in EVENTS if e[2]))
        cv.text_right(W - 2, ROW_TAG, tag, scale(DATA, 0.8))
