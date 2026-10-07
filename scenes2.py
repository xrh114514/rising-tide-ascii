"""Scenes 4-7: intelligence war, nuclear & space, detente, historical evaluation."""
import math

from engine import (
    W, H, Canvas, rgb, mix, scale, rng, hash2, clamp, lerp, ease_out, ease_in,
    map_cell, equirect, polar, text_auto, width_of, is_wide,
    big_text_cells, big_text_width, shot_index, cut_effect,
    DIM, MAIN, DATA, BRIGHT, ALERT, WARN, GREEN, VIOLET, AMBER, WHITE,
)
import chronicle
from scenes1 import draw_map_grid

# ------------------------------------------------------------------ scene 4
# 情报暗战：整窗解密文本。敏感词先公开显示，随后从左至右逐块打码，
# 转场时整页逐行涂黑，切到下一份档案。敏感词用 `反引号` 标记。
INTEL_PAGES = [
    ("CIA MEMORANDUM // EAST BERLIN UPRISING // 17 JUNE 1953", [
        "CIA INTELLIGENCE MEMORANDUM // 17 JUNE 1953 // EAST BERLIN",
        "SUBJECT: LABOR UNREST, SOVIET ZONE OF GERMANY",
        "CLASSIFICATION: SECRET // RELEASED 1995 // PAGE 1 OF 6",
        "",
        "1. AT 0600 HOURS LOCAL, CONSTRUCTION WORKERS ON STALINALLEE",
        "   DOWNED TOOLS DEMANDING LOWER WORK QUOTAS AND REPRICED",
        "   FOOD. THE MINISTRY HAD RAISED QUOTAS BY `25` PERCENT.",
        "2. BY MIDDAY THE STRIKE HAD SPREAD TO `MAGDEBURG` AND",
        "   `HALLE`, WITH AN ESTIMATED 1,000,000 PERSONS IN THE",
        "   STREETS OF MORE THAN 560 WORKPLACES AND 60 CITIES.",
        "3. BANNERS CARRIED SLOGANS: 'ELECTIONS', 'FREE GERMANY',",
        "   'UNITY'. THE CROWD MOVED TOWARD UNTER DEN LINDEN AND THE",
        "   HOUSE OF MINISTRIES. AT `ALEXANDERPLATZ` POLICE FIRED.",
        "4. SOVIET ARMORED COLUMNS - T-34/85 AND BTR-152 - ENTERED",
        "   LEIPZIG, MAGDEBURG, JENA AND `HALLE` BY 1400 HOURS.",
        "   MARTIAL LAW WAS DECLARED AT 1600. CURFEW AT 2100.",
        "5. THE SOVIET COMMANDER IN `KARLSHORST` REPORTED: 'THE",
        "   SITUATION IS RESTORED.' BY 19 JUNE RESISTANCE HAD CEASED.",
        "6. ESTIMATED LOSSES: 55-120 KILLED, `4,000` WOUNDED,",
        "   APPROXIMATELY 10,000 ARRESTED. WALTER ULBRICHT REMAINED",
        "   IN POWER. NO WESTERN INTERVENTION WAS ORDERED OR OFFERED.",
        "7. ANALYST COMMENT: THE RISING WAS SPONTANEOUS. NO AGENCY",
        "   ORDERED IT, AND NO AGENCY COULD HAVE STOPPED IT. THE",
        "   SOVIET RESPONSE WAS MEASURED IN HOURS, NOT DAYS - THE",
        "   PATTERN OF ALL FUTURE REBELLIONS IN THE SATELLITE STATES.",
        "8. COMPARATIVE NOTE: THE SAME PATTERN REAPPEARED IN BUDAPEST",
        "   1956, IN PRAGUE 1968, AND WAS AVERTED ONLY IN POLAND 1981.",
        "SOURCE: CIA CREST ARCHIVE / RADIO FREE EUROPE FILES",
        "DOCUMENT ID: CREST-1953-06-17-0042 // 26 PAGES // 4 SEALED",
    ]),
    ("INTELLIGENCE SUMMARY // HUNGARIAN REVOLUTION // 1956", [
        "INTELLIGENCE SUMMARY // HUNGARIAN PEOPLE'S REPUBLIC // 1956",
        "SUBJECT: ARMED UPRISING IN BUDAPEST AND THE PROVINCES",
        "CLASSIFICATION: SECRET // RELEASED 1995 // PAGE 1 OF 9",
        "",
        "1. 23 OCTOBER: A STUDENT DEMONSTRATION BEGAN AT THE PETOFI",
        "   STATUE AND MOVED TO THE PARLIAMENT. THE STATUE OF STALIN",
        "   WAS TOPPLED AT 2130. THE RADIO STATION WAS SEIZED AFTER",
        "   THE AVH (STATE SECURITY) OPENED FIRE ON THE CROWD.",
        "2. BY 25 OCTOBER THE GOVERNMENT OF IMRE NAGY PROMISED REFORM.",
        "   SOVIET TROOPS WITHDREW ON 28 OCTOBER - A BRIEF TRUCE.",
        "3. 1 NOVEMBER NAGY DECLARED NEUTRALITY AND WITHDREW FROM THE",
        "   WARSAW PACT. THE SOVIET UNION TREATED THIS AS A BREACH OF",
        "   THE `SOVIET-HUNGARIAN` TREATY AND PREPARED TO INTERVENE.",
        "4. 4 NOVEMBER, 0500 HOURS: OPERATION WHIRLWIND. T-54 TANKS",
        "   ENTERED BUDAPEST FROM `KELENFOLD`, `FERIHEGY` AND",
        "   `KOBANYA` AXES. THE CORVIN THEATER POINT HELD UNTIL 0900.",
        "5. THE FIGHTING LEFT EST. 2,500-20,000 HUNGARIANS DEAD - THE",
        "   FIGURE REMAINS DISPUTED - AND 200,000 CROSSED INTO AUSTRIA.",
        "   REFUGEE CAMPS AT `ANDAU` PROCESSED THEM WITHIN WEEKS.",
        "6. NAGY WAS EXECUTED IN 1958. JANOS KADAR WAS INSTALLED.",
        "7. THE GENERAL ASSEMBLY DEBATED FOR THREE DAYS. RESOLUTIONS",
        "   WERE PASSED. NO FORCE WAS COMMITTED BY ANY MEMBER STATE.",
        "8. RELATED DOCUMENT - 'THE CHANCE FOR PEACE', 16 APRIL 1953:",
        "   'THE WORLD IN ARMS IS NOT SPENDING MONEY ALONE. IT IS",
        "    SPENDING THE SWEAT OF ITS LABORERS, THE GENIUS OF ITS",
        "    SCIENTISTS, THE HOPES OF ITS CHILDREN. EVERY GUN THAT",
        "    IS MADE ... SIGNIFIES A THEFT FROM THOSE WHO HUNGER.'",
        "9. ANALYST COMMENT: THE WEST TALKED. THE TANKS ARRIVED.",
        "   THE LESSON ENTERED DOCTRINE ON BOTH SIDES FOR 30 YEARS.",
        "SOURCE: US STATE DEPT CABLES / NSA DECRYPTS / UN RECORDS",
        "DOCUMENT ID: CREST-1956-11-04-1177 // 41 PAGES // 12 SEALED",
    ]),
    ("DIPLOMATIC NOTE // BERLIN ULTIMATUM // 27 NOVEMBER 1958", [
        "DIPLOMATIC NOTE // 27 NOVEMBER 1958 // THE KREMLIN",
        "SUBJECT: THE STATUS OF WEST BERLIN // SIX-MONTH DEADLINE",
        "CLASSIFICATION: SECRET // RELEASED 1987 // PAGE 1 OF 4",
        "",
        "1. THE SOVIET GOVERNMENT PROPOSES THAT WESTERN POWERS WITHDRAW",
        "   THEIR TROOPS FROM WEST BERLIN AND THAT THE CITY BE ORGANIZED",
        "   AS A DEMILITARIZED 'FREE CITY'. A DEADLINE OF SIX MONTHS WAS",
        "   SET. THE NOTE WAS SIGNED BY N. S. KHRUSHCHEV AND",
        "   `A. A. GROMYKO`, MINISTER OF FOREIGN AFFAIRS.",
        "2. THE WESTERN REPLY OF 16 DECEMBER 1958 REJECTED THE NOTE.",
        "   THE ALLIED POSITION RESTED ON THE FOUR-POWER AGREEMENTS OF",
        "   1945 AND ON THE RIGHT OF ACCESS - THE CORRIDORS FROM",
        "   HELMSTEDT TO BERLIN WERE HELD OPEN BY ROAD, RAIL AND AIR.",
        "3. THE 'BERLIN QUESTION' ENTERED EVERY SUMMIT FROM 1959 ON:",
        "   GENEVA, PARIS, VIENNA. THE AIRLIFT OF 1948 WAS REMEMBERED",
        "   IN EVERY CABLE. NO FORCE WAS USED IN THIS PHASE.",
        "4. RELATED DOCUMENT - NSC-68, 14 APRIL 1950 (DECLASSIFIED 1975):",
        "   'THE ASSAULT UPON FREE INSTITUTIONS IS WORLD-WIDE NOW, AND",
        "    IN THE CONTEXT OF THE PRESENT POLARIZATION OF POWER, A",
        "    DEFEAT OF FREE INSTITUTIONS ANYWHERE IS A DEFEAT EVERYWHERE.'",
        "   THE DOCUMENT CALLED FOR A FOURFOLD RISE IN DEFENSE SPENDING.",
        "5. THE DEADLINE PASSED WITHOUT WAR. THE WALL WOULD COME THREE",
        "   YEARS LATER, AND IT WOULD COME OVERNIGHT, IN ONE NIGHT.",
        "6. ANALYST COMMENT: BRINKMANSHIP WITHOUT BULLETS - A TEST OF",
        "   WHETHER THE ALLIANCE WOULD HOLD ITS GROUND WHILE THE OTHER",
        "   SIDE PULLED ON THE ROPE. THIS TIME IT HELD.",
        "7. FOLLOW-UP: THE VIENNA SUMMIT OF 1961 COLLAPSED OVER THE",
        "   SAME ISSUE. THE NEXT BERLIN CRISIS WAS SET FOR `AUGUST`.",
        "SOURCE: STATE DEPT / KREMLIN CORRESPONDENCE // 0091",
        "DOCUMENT ID: CREST-1958-11-27-0091 // 11 PAGES // 2 SEALED",
    ]),
    ("FLIGHT LOG // U-2 F-0010 // 1 MAY 1960", [
        "FLIGHT LOG // AIRCRAFT F-0010 // 1 MAY 1960 // AQUATONE",
        "SUBJECT: OVERFLIGHT OF SOVIET TERRITORY // LOSS OF AIRCRAFT",
        "CLASSIFICATION: TOP SECRET // RELEASED 2010 // PAGE 1 OF 7",
        "",
        "1. DEPARTED `BADABER` AIRFIELD AT 0600Z. HEADING 032, FL700.",
        "   PILOT: FRANCIS G. POWERS, CIA CIVIL AIR PILOT, AGE `30`.",
        "   AIRCRAFT: LOCKHEED U-2C, SINGLE ENGINE, CAMERA `HYCON B`.",
        "2. ROUTE CROSSED TYURATAM, SVERDLOVSK, ARKHANGELSK, MURMANSK.",
        "   AT 0730Z AN SA-2 GUIDELINE BATTERY NEAR SVERDLOVSK ENGAGED.",
        "   IMPACT AT `SVERDLOVSK-15`. THE PILOT EJECTED AT 70,000 FEET",
        "   AND WAS CAPTURED BY A `KGB PATROL` WITHIN 40 MINUTES.",
        "3. US STATEMENT, 3 MAY: 'A WEATHER RESEARCH AIRCRAFT LOST",
        "   OVER TURKEY.' THE COVER HELD FOR THREE DAYS. ON 7 MAY THE",
        "   CHAIRMAN ANNOUNCED THE CAPTURED PILOT AND THE WRECKAGE.",
        "4. THE PARIS SUMMIT OPENED 16 MAY AND COLLAPSED THE SAME DAY.",
        "   KHRUSHCHEV DEMANDED AN APOLOGY; THE PRESIDENT REFUSED.",
        "5. POWERS WAS TRIED IN MOSCOW, CONVICTED OF ESPIONAGE, AND",
        "   SENTENCED TO TEN YEARS. HE SERVED 21 MONTHS AND WAS",
        "   EXCHANGED ON GLIENICKE BRIDGE, 10 FEBRUARY 1962, FOR",
        "   RUDOLF ABEL. THE EXCHANGE WAS DENIED BY BOTH SIDES.",
        "6. RELATED DOCUMENT - INAUGURAL ADDRESS, 20 JANUARY 1961:",
        "   'LET US NEVER NEGOTIATE OUT OF FEAR. BUT LET US NEVER",
        "    FEAR TO NEGOTIATE. CIVILITY IS NOT A SIGN OF WEAKNESS,",
        "    AND SINCERITY IS ALWAYS SUBJECT TO PROOF.'",
        "7. ANALYST COMMENT: OVERFLIGHTS WERE TO END WHEN SATELLITES",
        "   COULD DO THE WORK. THIS WAS ONE OF THE LAST. THE `CORONA`",
        "   PROGRAM WOULD RETURN ITS FIRST FILM IN AUGUST 1960.",
        "SOURCE: CIA FLIGHT LOGS / SOVIET TRIAL RECORD // 0007",
        "DOCUMENT ID: CREST-1960-05-01-0007 // 33 PAGES // 9 SEALED",
    ]),
    ("WATCH REPORT // BERLIN WALL // 13 AUGUST 1961", [
        "WATCH REPORT // 13 AUGUST 1961 // ALLIED MILITARY MISSION",
        "SUBJECT: CLOSURE OF THE SECTOR BOUNDARY, BERLIN",
        "CLASSIFICATION: SECRET // RELEASED 1990 // PAGE 1 OF 5",
        "",
        "1. AT 0100 HOURS, COMBAT ENGINEERS OF THE GDR NATIONAL",
        "   PEOPLE'S ARMY BEGAN CLOSING THE SECTOR BOUNDARY. STREET",
        "   CARS WERE HALTED, RAILS LIFTED, AND THE FIRST WIRE",
        "   ENTANGLEMENTS LAID BETWEEN `BERNAUER` AND `BRUNNENSTRASSE`.",
        "2. BY 0600 THE BORDER GUARDS HAD SEALED 81 OF 87 CROSSINGS.",
        "   FAMILIES WOKE ON OPPOSITE SIDES OF A LINE THAT HAD NOT",
        "   EXISTED THE NIGHT BEFORE.",
        "3. WITHIN 24 HOURS THE LINE RAN 45 KM THROUGH THE CITY AND",
        "   112 KM AROUND WEST BERLIN. 302 WATCHTOWERS WERE PLANNED.",
        "   THE CONCRETE WALL CAME LATER, IN STAGES, 1962-1975.",
        "4. 15 AUGUST: BORDER GUARD CONRAD SCHUMANN, AGE 19, JUMPED",
        "   THE WIRE AT BERNAUER STRASSE INTO THE FRENCH SECTOR. THE",
        "   PHOTOGRAPH WENT AROUND THE WORLD WITHIN 24 HOURS.",
        "5. 27 OCTOBER 1961: US AND SOVIET TANKS FACED EACH OTHER AT",
        "   CHECKPOINT CHARLIE FOR 16 HOURS, 100 METRES APART. THE",
        "   ORDER TO FIRE WAS NEVER GIVEN. THE TANKS WITHDREW IN",
        "   REVERSE GEAR, ALTERNATING, ONE BY ONE.",
        "6. ESTIMATED ESCAPES IN THE EARLY YEARS: 5,000. AT LEAST",
        "   140 PERSONS ARE RECORDED AS DIED AT THE WALL. THE LIST",
        "   OF NAMES WAS PARTIALLY RELEASED: `SEE APPENDIX C`.",
        "7. RELATED DOCUMENT - WEST BERLIN, 26 JUNE 1963:",
        "   'FREEDOM HAS MANY DIFFICULTIES AND DEMOCRACY IS NOT",
        "    PERFECT. BUT WE HAVE NEVER HAD TO PUT A WALL UP TO KEEP",
        "    OUR PEOPLE IN. I TAKE PRIDE IN THE WORDS: ICH BIN EIN",
        "    BERLINER.'",
        "SOURCE: ALLIED WATCH REPORTS / BERLIN BRIGADE // 0031",
        "DOCUMENT ID: CREST-1961-08-13-0031 // 19 PAGES // 6 SEALED",
    ]),
    ("INTERNAL ASSESSMENT // STATION PRAGUE // EYES ONLY", [
        "INTERNAL ASSESSMENT // STATION PRAGUE // EYES ONLY",
        "SUBJECT: COMPROMISE OF AGENT NETWORK 'RAINBOW'",
        "CLASSIFICATION: TOP SECRET // NOT RELEASABLE // PAGE 12",
        "",
        "1. THE ANALYSIS BEGINS WITH A MISTAKE: A ONE-TIME PAD WAS",
        "   USED TWICE. THE SAME KEY ON TWO MESSAGES TURNS CIPHER",
        "   INTO PLAINTEXT FOR ANYONE WITH ENOUGH PAPER AND PATIENCE.",
        "2. FRAGMENTS RECOVERED FROM THE TRAFFIC:",
        "   '... SHIPMENT MOVED TO WAREHOUSE 7 ...'",
        "   '... MEETING CANCELLED, USE FALLBACK ...'",
        "   '... PAD REUSED // CHANNEL SUSPECT ...'",
        "   THE REST IS `CLASSIFIED UNTIL 2045` BY ORDER OF `MINISTRY`.",
        "3. AGENTS WERE CALLED IN. MEETINGS WERE ABORTED. DEAD DROPS",
        "   AT PARK BENCH 7 AND THE `RAILWAY` STATION WERE CLEARED.",
        "   TRAFFIC STOPPED AT 23:41Z ON 12 AUGUST 1961 - THE LAST",
        "   MESSAGE FROM `AGENT RAINBOW` BEFORE THE NETWORK WENT DARK.",
        "4. ARRESTS FOLLOWED IN `PRAGUE`, `VIENNA` AND `EAST BERLIN`.",
        "   SURVIVING MEMBERS SCATTERED. CHANNELS WERE BURNED. THE",
        "   HANDLER LEFT THE COUNTRY UNDER DIPLOMATIC COVER.",
        "5. ANALYST COMMENT: WE SEE ONLY WHAT WAS ALLOWED TO BE SEEN.",
        "   THE FAILURE WAS HUMAN, NOT MATHEMATICAL. ONE PAD, USED",
        "   TWICE, UNLOCKED MONTHS OF TRAFFIC IN BOTH DIRECTIONS -",
        "   AND NOT ONLY FOR US.",
        "6. THE SECOND CONSEQUENCE IS SLOWER: TRUST. EVERY MESSAGE",
        "   SENT AFTER THE COMPROMISE IS SUSPECT, INCLUDING THE",
        "   MESSAGES THAT WERE NEVER INTERCEPTED AT ALL.",
        "7. MOST OF THIS FILE REMAINS SEALED. THE REST WAS BURNED,",
        "   BURIED, OR NEVER COMMITTED TO PAPER. WHAT YOU ARE",
        "   READING IS WHAT SURVIVED THE SHREDDER AND THE FIRE.",
        "SOURCE: ARCHIVE WITHHELD // [REDACTED] // PAGE 31",
        "DOCUMENT ID: [REDACTED] // 61 PAGES // 58 SEALED",
    ]),
    ("EXCHANGE RECORD // GLIENICKE BRIDGE // 10 FEBRUARY 1962", [
        "EXCHANGE RECORD // GLIENICKE BRIDGE // 10 FEBRUARY 1962",
        "SUBJECT: EXCHANGE OF DETAINED PERSONNEL // POTSDAM",
        "CLASSIFICATION: SECRET // RELEASED 2011 // PAGE 1 OF 3",
        "",
        "1. AT 0845 HOURS ON THE BRIDGE BETWEEN WEST BERLIN AND",
        "   POTSDAM, RUDOLF IVANOVICH ABEL WALKED EAST WHILE FRANCIS",
        "   GARY POWERS WALKED WEST. JAMES B. DONOVAN, THE AMERICAN",
        "   LAWYER WHO DEFENDED ABEL, OBSERVED FROM THE CENTER LINE.",
        "2. ABEL: SOVIET 'ILLEGAL' AGENT, ARRESTED IN `NEW YORK` IN",
        "   1957, CONVICTED OF ESPIONAGE, SENTENCED TO 30 YEARS.",
        "   POWERS: U-2 PILOT, SENTENCED IN `MOSCOW` TO TEN YEARS.",
        "3. THE EXCHANGE WAS NEGOTIATED THROUGH THE BERLIN CHANNEL",
        "   AND DENIED BY BOTH GOVERNMENTS FOR YEARS. THE FIGURES ON",
        "   THE BRIDGE WERE `THE PRISONERS`. NO FLAGS FLEW.",
        "4. ANALYST COMMENT: A RULE OF THE GAME WAS ESTABLISHED.",
        "   SPIES WOULD BE TRADED, NOT LOST. IT HAPPENED AGAIN IN",
        "   1985, ON THE SAME BRIDGE, WITH 23 PERSONS EACH WAY.",
        "5. RELATED DOCUMENT - SOVIET MESSAGE, 26 OCTOBER 1962:",
        "   'MR. PRESIDENT, WE AND YOU OUGHT NOT NOW TO PULL ON THE",
        "    ENDS OF THE ROPE IN WHICH YOU HAVE TIED THE KNOT OF WAR,",
        "    BECAUSE THE MORE THE TWO OF US PULL, THE TIGHTER THE",
        "    KNOT WILL BE TIED.'",
        "6. THE SAME CHANNEL THAT TRADED SPIES IN FEBRUARY WAS",
        "   TRADING MISSILES IN OCTOBER. THE TWO CRISES ARE ONE",
        "   STORY, TOLD IN TWO DOCUMENTS, WITHIN THE SAME YEAR.",
        "7. THE LAST PAGES OF THIS FILE ARE MISSING. THE RECORD",
        "   REMAINS INCOMPLETE, AND IT WILL REMAIN INCOMPLETE.",
        "SOURCE: DOJ / CIA RECORDS / DONOVAN PAPERS // 0055",
        "DOCUMENT ID: CREST-1962-02-10-0055 // 8 PAGES // 0 SEALED",
    ]),
]


def _parse(line):
    """拆分 `标记` 的敏感词 -> [(文本, 是否敏感, 起始列)]"""
    segs, buf, sens, x = [], "", False, 0
    for ch in line:
        if ch == "`":
            if buf:
                segs.append((buf, sens, x))
                x += len(buf)
                buf = ""
            sens = not sens
        else:
            buf += ch
    if buf:
        segs.append((buf, sens, x))
    return segs


# 预解析：每页 -> (标题, [行分段], [(行号, 起始列, 长度) ...敏感块按阅读顺序])
PARSED = []
for _title, _lines in INTEL_PAGES:
    _segs = [_parse(l) for l in _lines]
    _spans = []
    for _li, _sl in enumerate(_segs):
        for (_txt, _sens, _sx) in _sl:
            if _sens:
                _spans.append((_li, _sx, len(_txt)))
    PARSED.append((_title, _segs, _spans))


def scene_intel(cv, t, st):
    cv.clear(" ", 0)
    r = rng(t, 616)
    for i in range(W * H):
        if r.random() < 0.014:
            cv.ch[i] = "0123456789ABCDEF"[r.randrange(16)]
            cv.fg[i] = scale(DATA, 0.13 + 0.09 * r.random())

    # ---- 档案分页：每个时间线事件一份整窗文本
    cuts = [st.snap(x) for x in chronicle.event_times(78.5, 127)]
    ncut = shot_index(t, cuts)
    i0 = max(0, min(ncut, len(PARSED)) - 1)
    seg_t0 = cuts[ncut - 1] if ncut else 78.8
    seg_end = cuts[ncut] if ncut < len(cuts) else 127.2
    dtitle, pagesegs, spans = PARSED[i0]

    dur = max(1.0, seg_end - seg_t0)
    panel_col = scale(mix(DATA, VIOLET, 0.28), 1.0)
    doc_col = mix(AMBER, WARN, 0.3)
    red_col = rgb(24, 24, 26)

    # ============ 大窗口：解密文档整页（敏感词先公开）
    cv.box(1, 2, 76, 36, dtitle, panel_col, fill=" ")
    typed = (t - seg_t0) * 240.0                     # 全页打字进度（列）
    pos = 0
    for i, segs in enumerate(pagesegs):
        y = 3 + i
        if y > 35:
            break
        x = 3
        for (txt, _sens, _sx) in segs:
            for ch in txt:
                if pos < typed and x <= 73:
                    cv.set(x, y, ch, doc_col)
                x += 1
                pos += 1
            pos += 1                                 # 行间空档
        pos += 1

    # ---- 敏感词块：从左至右逐块打码（初版为公开原文）
    red_start = seg_t0 + 0.28 * dur
    red_dur = 0.42 * dur
    n_spans = max(1, len(spans))
    for k, (li, sx, ln) in enumerate(spans):
        t_k = red_start + (k / n_spans) * red_dur
        if t < t_k:
            continue
        fill = clamp((t - t_k) / 0.12, 0.0, 1.0)
        n = int(ln * fill)
        y = 3 + li
        for j in range(n):
            cv.set(3 + sx + j, y, "█", red_col)

    stamp = "PAGE %d/7  //  %d LINES  //  %d ENTRIES BLANKED" % (i0 + 1, len(pagesegs), len(spans))
    cv.text(3, 36, stamp[:70], scale(mix(ALERT, WARN, 0.4), 0.85))

    # ---- 转场：逐行涂黑整页，切到下一份档案
    black_t = seg_end - min(1.5, 0.2 * dur)
    if t > black_t:
        edge = (t - black_t) / 0.042
        for y in range(3, 37):
            if y - 3 <= edge:
                for x in range(2, 75):
                    i = y * W + x
                    cv.ch[i] = "█"
                    cv.fg[i] = rgb(22, 24, 26)
            elif y - 4 <= edge:
                for x in range(2, 75):
                    i = y * W + x
                    if cv.ch[i] not in (" ", "█"):
                        cv.set(x, y, "▒", mix(ALERT, WARN, 0.45))

    # ============ 大窗口 B：监听波形（持续）
    cv.box(79, 2, 80, 17, "INTERCEPT TRAFFIC // FREQ 121.50 MHZ // BEARING 043", panel_col, fill=" ")
    for x in range(81, 157):
        hgt = int(1.6 + 1.6 * math.sin(x * 0.34 + t * 5.2) * math.sin(x * 0.07 + t * 1.3))
        for dy in range(-2, 3):
            if abs(dy) <= abs(hgt):
                cv.set(x, 5 + dy, "|" if dy == 0 else ".", scale(GREEN, 0.6))
    for i, s in enumerate(["1958-04-02  0441Z // SHIPMENT MOVED TO WAREHOUSE 7",
                           "1958-04-02  0517Z // MEETING CANCELLED, USE FALLBACK",
                           "1958-04-03  2203Z // ████████ ████████ ████████",
                           "1959-01-17  0112Z // PAD REUSED // CHANNEL SUSPECT",
                           "1961-08-12  2341Z // ████████ ████████ ████████"]):
        y = 9 + i * 2
        if y > 17:
            break
        for j, ch in enumerate(s[:74]):
            cv.set(81 + j, y, ch, red_col if ch == "█" else mix(GREEN, MAIN, 0.35))

    # ============ 大窗口 C：人员档案字段
    cv.box(79, 21, 80, 17, "PERSONNEL FILE // STATION PRAGUE", panel_col, fill=" ")
    for i, (k, v) in enumerate([
            ("SUBJECT ......", "████████████████"), ("CODENAME .....", "RAINBOW"),
            ("ACCESS .......", "ULTRA / GAMMA"), ("PERIOD .......", "1953 - 1961"),
            ("CIPHER .......", "ONE TIME PAD / 44 CHAR BLOCKS"),
            ("COURIER ......", "DEAD DROP / PARK BENCH 7"),
            ("HANDLER ......", "████████████████"), ("LAST SIGNAL ..", "1961-08-12 23:41Z"),
            ("STATUS .......", "COMPROMISED")]):
        y = 23 + i
        if y > 35:
            break
        s = "%s %s" % (k, v)
        for j, ch in enumerate(s[:74]):
            cv.set(81 + j, y, ch, red_col if ch == "█" else mix(MAIN, BRIGHT, 0.2))

    if t - seg_t0 > 0.3 and seg_end - t > 1.6:
        cv.text(2, 38, ">> ARCHIVE MODE // RAW TEXT FIRST, ENTRIES BLANKED IN SEQUENCE",
                scale(mix(ALERT, DIM, 0.35), 0.9))
    cut_effect(cv, t, cuts)
# ------------------------------------------------------------------ scene 5
LAUNCH_LOG = [
    "> SILO 04 DOORS OPEN // MINUTEMAN III",
    "> T-MINUS 00:00:14 // GUIDANCE INERTIAL",
    "> LAUNCH DETECTED // 61.2N 120.4E",
    "> TRAJECTORY F7 // TIME TO IMPACT 27M",
    "> BMEWS THULE: TRACKING 12 OBJECTS",
    "> WARNING: RE-ENTRY VEHICLES DETECTED",
    "> YIELD EST 1.2MT // AIRBURST",
    "> SUBMARINE PATROL // NORTH ATLANTIC",
    "> STRATEGIC BOMBER WING AIRBORNE",
    "> ORBITAL OBJECTS TRACKED: 4210",
]

ICBM_TABLE = [
    ("R-7 / SS-6", "8 000 KM", 1957),
    ("ATLAS-D", "9 000 KM", 1959),
    ("TITAN II", "15 000 KM", 1963),
    ("MINUTEMAN III", "13 000 KM", 1970),
    ("SS-18 SATAN", "16 000 KM", 1975),
    ("SS-25 SICKLE", "13 000 KM", 1985),
    ("TRIDENT C4", "7 400 KM", 1979),
]

# 时间线事件 -> 地区 / 组织徽标 / 解密工程档案
SPACE_EVENTS = [
    dict(t0=127.9, region="BAIKONUR // KAZAKH SSR", lon=63.3, lat=48.0,
         org="CCCP", file="PROJECT: SPUTNIK-1", lines=[
             "OKB-1 DESIGN BUREAU // KOROLEV",
             "MASS 83.6 KG // 20.005 MHZ",
             "R-7 ICBM AS LAUNCH VEHICLE",
             "SOURCE: DECLASSIFIED OKB-1 REPORT"]),
    dict(t0=133.7, region="BAIKONUR // KAZAKH SSR", lon=63.3, lat=48.0,
         org="CCCP", file="PROJECT: VOSTOK-1", lines=[
             "COSMONAUT: Y. A. GAGARIN",
             "ONE ORBIT // 108 MINUTES",
             "EJECTION SEAT LANDING",
             "SOURCE: DECLASSIFIED VOSTOK LOG"]),
    dict(t0=138.9, region="CAPE KENNEDY / MARE TRANQUIL", lon=-80.6, lat=28.5,
         org="NASA", file="PROJECT: APOLLO 11", lines=[
             "SATURN V / AS-506",
             "EAGLE LANDS 20 JULY 1969",
             "EVA 2H 31M // 21.5 KG SAMPLES",
             "SOURCE: NASA MOCR FLIGHT PLAN"]),
    dict(t0=144.1, region="WASHINGTON / MOSCOW", lon=-77.0, lat=38.9,
         org="TREATY", file="TREATY: ABM 1972", lines=[
             "LIMIT: 2 ABM SITES PER SIDE",
             "15 LAUNCHERS PER SITE",
             "VERIFIED BY TECHNICAL MEANS",
             "SOURCE: DECLASSIFIED TREATY TEXT"]),
    dict(t0=149.3, region="EARTH ORBIT // JOINT DOCKING", lon=0.0, lat=0.0,
         org="NASA", file="PROJECT: ASTP 1975", lines=[
             "SOYUZ-19 / APOLLO CSM-111",
             "DOCKED 17 JULY 1975",
             "JOINT CREW: 5 COSMONAUTS/ASTRONAUTS",
             "SOURCE: NASA / INTERCOSMOS RECORDS"]),
    dict(t0=154.5, region="WASHINGTON D.C. / PENTAGON", lon=-77.0, lat=38.9,
         org="SDI", file="PROJECT: SDI 1983", lines=[
             "PRESIDENTIAL ADDRESS 23 MAR 1983",
             "DIRECTED ENERGY / KINETIC INTERCEPT",
             "PROGRAM COST: 26 BN USD",
             "SOURCE: DECLASSIFIED SDI PROGRAM DOC"]),
]


def draw_org(cv, cx, cy, r, kind, col, t):
    """组织徽标（字符画）：NASA / CCCP / SDI / TREATY。"""
    x_r, y_r = r * 2.0, r * 1.0
    if kind in ("NASA", "SDI", "TREATY"):
        for i in range(64):
            a = i * math.pi / 32
            cv.set(int(cx + math.cos(a) * x_r), int(cy + math.sin(a) * y_r), ".",
                   scale(col, 0.85))
    if kind == "NASA":
        for k in range(int(x_r * 0.75)):
            for s in (-1, 1):
                cv.set(int(cx + s * k), int(cy + k * 0.26 - 1), ">", mix(col, BRIGHT, 0.45))
        for (dx, dy) in ((-0.5, -0.55), (0.55, -0.5), (0.62, 0.3), (-0.66, 0.32)):
            cv.set(int(cx + dx * x_r), int(cy + dy * y_r), "*", mix(col, BRIGHT, 0.55))
        cv.text(int(cx) - 2, int(cy + y_r) + 1, "NASA", scale(col, 1.0))
    elif kind == "CCCP":
        for ry in range(-int(y_r), int(y_r) + 1):
            for rx in range(-int(x_r), int(x_r) + 1):
                dx, dy = rx / x_r, ry / y_r
                d = math.hypot(dx, dy)
                if d > 1.0:
                    continue
                ang = math.atan2(dy, dx)
                std = math.cos(math.pi / 5) / math.cos((ang % (2 * math.pi / 5)) - math.pi / 5)
                bound = 0.42 + (std - 0.809) * 3.04
                if d < bound:
                    cv.set(int(cx + rx), int(cy + ry), "#", mix(col, BRIGHT, 0.2))
        cv.text(int(cx) - 2, int(cy + y_r) + 1, "CCCP", scale(col, 1.0))
    elif kind == "SDI":
        for k in range(int(y_r) + 1):
            w = int(x_r * (1.0 - k / (y_r + 1) * 0.55))
            cv.set(int(cx - w), int(cy - y_r + k * 2), "\\", scale(col, 0.9))
            cv.set(int(cx + w), int(cy - y_r + k * 2), "/", scale(col, 0.9))
        cv.set(int(cx), int(cy), "*", mix(col, BRIGHT, 0.5))
        cv.text(int(cx) - 1, int(cy + y_r) + 1, "SDI", scale(col, 1.0))
    elif kind == "TREATY":
        for s in (-1, 1):
            for k in range(int(y_r)):
                cv.set(int(cx + s * x_r * 0.7), int(cy - y_r + k * 2), "|", scale(col, 0.9))
        cv.text(int(cx) - 2, int(cy), "==", mix(col, BRIGHT, 0.5))
        cv.text(int(cx) - 3, int(cy + y_r) + 1, "ABM 1972", scale(col, 1.0))


def draw_trefoil(cv, cx, cy, r, col, t):
    """ASCII 核辐射三叶标志（3 个扇形 + 中心圆）。"""
    for ry in range(-r, r + 1):
        for rx in range(-r * 2, r * 2 + 1):
            dx = rx / (r * 2.0)
            dy = ry / float(r)
            d = math.hypot(dx, dy)
            x, y = cx + rx, cy + ry
            if not (0 <= x < W and 0 <= y < H):
                continue
            if d <= 0.26:
                cv.set(x, y, "O", mix(col, BRIGHT, 0.55))
            elif 0.34 < d < 1.0:
                ang = math.degrees(math.atan2(dy, dx)) % 360
                for c in (90, 210, 330):
                    if abs((ang - c + 180) % 360 - 180) < 26:
                        cv.set(x, y, "#", scale(col, 0.75 + 0.25 * math.sin(t * 2 + d * 4)))
                        break


def scene_nuclear(cv, t, st):
    u = t - 127.0
    beat = st.pulse(t)
    dens = 0.4 + 0.6 * clamp(u / 26.0, 0, 1)

    # ---- 镜头：跟随时间线事件（剪辑点对齐鼓点）
    cuts = [st.snap(x) for x in chronicle.event_times(127, 158)]
    ncut = shot_index(t, cuts)
    ev = SPACE_EVENTS[max(0, min(ncut, len(SPACE_EVENTS)) - 1)]
    mode = max(0, min(ncut, len(SPACE_EVENTS)) - 1) % 3

    cv.clear(" ", 0)
    r = rng(t, 909)
    for i in range(W * H):
        if r.random() < 0.018 * dens:
            cv.ch[i] = "0123456789ABCDEF./\\|+*"[r.randrange(22)]
            cv.fg[i] = scale(DATA, 0.16 + 0.14 * r.random())

    panel_col = scale(DATA, 0.95)

    # ============ 左上：核力量（三叶标志 + 计数）
    cv.box(0, 1, 34, 17, "NUCLEAR FORCES", panel_col, fill=" ")
    draw_trefoil(cv, 11, 9, 5, mix(ALERT, WARN, 0.55), t)
    arsenal = [("US WARHEADS", 23317), ("USSR WARHEADS", 39197),
               ("ICBM SITES", 1400), ("SLBM BOATS", 96)]
    for i, (name, val) in enumerate(arsenal):
        y = 3 + i * 3
        cv.text(21, y, name[:11], scale(DATA, 0.85))
        shown = int(val * clamp((u - i * 0.8) / 22.0, 0.02, 1.0))
        cv.text_right(33, y + 1, "%d" % shown, mix(AMBER, ALERT, 0.3 + 0.4 * beat))
    cv.text(2, 15, "EST. FIGURES // CIRCA 1986", scale(DIM, 1.2))

    # ============ 左下：地区切换（事件发生地）
    cv.box(0, 19, 34, 19, "REGION // " + ev["region"][:20], panel_col, fill=" ")
    win = (ev["lon"] - 40, ev["lon"] + 40, ev["lat"] + 18, ev["lat"] - 18)
    draw_map_grid(cv, 2, 21, 30, 15, t, jitter=0.2, win=win)
    mx, my = equirect(ev["lon"], ev["lat"], 2, 21, 30, 15, *win)
    blink = math.sin(t * 5) > -0.2
    col = mix(WARN, BRIGHT, 0.5 if blink else 0.1)
    for d in range(-2, 3):
        cv.set(int(mx) + d, int(my), "-", scale(col, 0.8))
        cv.set(int(mx), int(my) + d, "|", scale(col, 0.8))
    cv.set(int(mx), int(my), "X", col)
    cv.text(2, 37, "GRID %05.1f %s / %05.1f %s" % (
        abs(ev["lat"]), "N" if ev["lat"] >= 0 else "S",
        abs(ev["lon"]), "E" if ev["lon"] >= 0 else "W"), scale(DATA, 0.8))

    # ============ 中央主窗口：按事件变换内容（轨道 / 载人 / 登月 / 条约 / 对接 / SDI）
    ecx, ecy, er = 60, 21, 5

    def _earth(cx, cy, rad, t):
        for ry in range(-rad, rad + 1):
            for rx in range(-rad * 2, rad * 2 + 1):
                dx = rx / (rad * 2.0)
                dy = ry / float(rad)
                if dx * dx + dy * dy <= 1.0:
                    ch = "." if int(abs(dx) * 4 + abs(dy) * 3) % 2 else ":"
                    cv.set(cx + rx, cy + ry, ch,
                           mix(MAIN, BRIGHT, 0.25 + 0.3 * math.sin(t + rx)))
        cv.text(cx - 2, cy, "EARTH", scale(BRIGHT, 0.9))

    def _ring(cx, cy, rr, ys, col):
        for i in range(96):
            a = i * math.pi / 48
            cv.set(int(cx + math.cos(a) * rr), int(cy + math.sin(a) * rr * ys),
                   ".", scale(col, 0.32))

    def _moon(mx, my, t):
        for ry in range(-4, 5):
            for rx in range(-8, 9):
                dx = rx / 8.0
                dy = ry / 4.0
                if dx * dx + dy * dy <= 1.0:
                    h = hash2(rx, ry, 77)
                    cv.set(mx + rx, my + ry, "@" if h > 0.72 else "%",
                           scale(mix(WHITE, DATA, 0.35), 0.45 + 0.35 * h))
        cv.text(mx - 3, my + 5, "MOON", scale(WHITE, 0.8))

    ev_i = max(0, min(ncut, len(SPACE_EVENTS)) - 1)
    if ev_i == 0:
        # SPUTNIK：地球 + LEO + 卫星 + R-7 上升轨迹
        _earth(ecx, ecy, er, t)
        _ring(ecx, ecy, 12, 0.62, VIOLET)
        ang = t * 0.9
        sx = ecx + math.cos(ang) * 12
        sy = ecy + math.sin(ang) * 12 * 0.62
        cv.set(int(sx), int(sy), "S", mix(VIOLET, BRIGHT, 0.55))
        cv.text(int(sx) + 1, int(sy), "SPUTNIK-1", scale(VIOLET, 0.75))
        for k in range(16):
            f = k / 15.0
            x = ecx - 14 + f * 20
            y = ecy + 8 - math.sin(f * 2.2) * 14
            cv.set(int(x), int(y), ":" if k % 2 else "+", scale(AMBER, 0.4 + 0.5 * f))
        cv.text(38, 33, "R-7 LAUNCH // 83.6 KG // 20.005 MHZ // 4 OCT 1957",
                scale(WARN, 0.85))
    elif ev_i == 1:
        # VOSTOK：载人轨道一圈
        _earth(ecx, ecy, er, t)
        _ring(ecx, ecy, 12, 0.62, VIOLET)
        u2 = (t * 0.16) % 1.0
        ang = u2 * 2 * math.pi
        sx = ecx + math.cos(ang) * 12
        sy = ecy + math.sin(ang) * 12 * 0.62
        cv.set(int(sx), int(sy), "O", mix(BRIGHT, WARN, 0.4))
        cv.text(int(sx) + 1, int(sy) - 1, "VOSTOK-1", scale(WARN, 0.8))
        cv.text(38, 33, "ONE ORBIT // 108 MIN // GAGARIN // 12 APRIL 1961",
                scale(WARN, 0.85))
    elif ev_i == 2:
        # APOLLO：地月转移 + 登月
        _earth(ecx, ecy, er, t)
        _moon(110, 9, t)
        for k in range(30):
            f = k / 29.0
            x = lerp(ecx + 4, 106, f) + math.sin(f * math.pi) * -5
            y = lerp(ecy - 3, 12, f) + math.sin(f * math.pi) * -8
            cv.set(int(x), int(y), "." if k % 2 else "-", scale(WARN, 0.35 + 0.35 * f))
        u2 = (t * 0.11) % 1.0
        ax = lerp(ecx + 4, 106, u2) + math.sin(u2 * math.pi) * -5
        ay = lerp(ecy - 3, 12, u2) + math.sin(u2 * math.pi) * -8
        cv.set(int(ax), int(ay), "A", mix(BRIGHT, WARN, 0.35))
        cv.text(int(ax) + 1, int(ay) - 1, "EAGLE", scale(WARN, 0.8))
        cv.text(38, 33, "MARE TRANQUILITATIS // 20 JULY 1969 // EVA 2H31M",
                scale(WARN, 0.85))
    elif ev_i == 3:
        # ABM：弹道 + 发射井封顶
        for (x0, side) in ((36, 0), (112, 1)):
            for k in range(3):
                cv.text(x0 + k * 3, 32, "=1=", mix(ALERT if side else MAIN, BRIGHT, 0.4))
            cv.text(x0, 34, "1054 SITES" if side == 0 else "1618 SITES",
                    scale(DATA, 0.85))
        for k in range(3):
            y0 = 12 + k * 2
            for i in range(60):
                f = i / 59.0
                x = 38 + f * 76
                y = y0 + 8 - math.sin(f * math.pi) * (12 + k * 3)
                if i % 2 == 0 and 2 <= y < 36:
                    cv.set(int(x), int(y), "-" if k == 0 else ".", mix(ALERT, WARN, f))
            cv.set(38, y0 + 8, "L", mix(ALERT, BRIGHT, 0.4))
            cv.set(113, y0 + 8, "=", mix(BRIGHT, ALERT, 0.4))
        for i in range(24):
            cv.set(44 + i * 3, 20, "=", scale(GREEN, 0.5))     # 热线
        cv.text(56, 19, "HOTLINE MOSCOW - WASHINGTON", scale(GREEN, 0.85))
        cv.text(38, 36, "ABM TREATY 1972 // LAUNCHERS CAPPED // MAD BALANCE",
                scale(WARN, 0.85))
    elif ev_i == 4:
        # ASTP：两个飞行器对接
        _earth(ecx, ecy, er, t)
        _ring(ecx, ecy, 10, 0.6, VIOLET)
        _ring(ecx, ecy, 14, 0.52, VIOLET)
        u2 = 0.5 + 0.45 * math.sin(t * 0.6)
        x1 = ecx - 14 + u2 * 12
        x2 = ecx + 14 - u2 * 12
        cv.text(int(x1), 20, "==<", mix(BRIGHT, MAIN, 0.4))
        cv.text(int(x2), 20, ">==", mix(BRIGHT, WARN, 0.4))
        if u2 > 0.93:
            cv.text(ecx - 1, 18, "><", mix(BRIGHT, WHITE, 0.5))
        cv.text(38, 33, "SOYUZ-19 >< APOLLO // DOCKED 17 JULY 1975",
                scale(WARN, 0.85))
    else:
        # SDI：光束拦截弹道
        for k in range(3):
            y0 = 14 + k * 3
            for i in range(60):
                f = i / 59.0
                x = 38 + f * 76
                y = y0 + 10 - math.sin(f * math.pi) * (12 + k * 2)
                if i % 2 == 0 and 2 <= y < 36:
                    cv.set(int(x), int(y), "-", mix(ALERT, WARN, f))
            cv.set(38, y0 + 10, "L", mix(ALERT, BRIGHT, 0.4))
            hit = 0.45 + 0.2 * math.sin(t * 1.2 + k)
            hx = 38 + 76 * hit
            hy = y0 + 10 - math.sin(hit * math.pi) * (12 + k * 2)
            for d in range(10):
                cv.set(int(hx), int(hy - d), "|", mix(VIOLET, BRIGHT, 0.5))
            cv.set(int(hx), int(hy), "X", mix(BRIGHT, ALERT, 0.4))
        cv.text(40, 8, "SDI SATELLITE // DIRECTED ENERGY INTERCEPT",
                scale(VIOLET, 0.85))
        cv.set(76, 6, "S", mix(VIOLET, BRIGHT, 0.6))
        cv.text(38, 36, "SDI 1983 // INTERCEPT WINDOW 0.42 // COST 26 BN",
                scale(WARN, 0.85))

    # ============ 右上：导弹参数
    cv.box(124, 1, 36, 21, "ICBM PARAMETERS", panel_col, fill=" ")
    cv.text(126, 3, "MODEL         RANGE     YR", scale(DATA, 0.8))
    for i, (model, rng_km, yr) in enumerate(ICBM_TABLE):
        y = 5 + i * 2
        if y > 19:
            break
        appear = clamp((u - 1.2 - i * 1.5) / 1.2, 0, 1)
        line = "%-13s %-9s %d" % (model, rng_km, yr)
        cv.text(126, y, line[:33], scale(mix(AMBER, WARN, 0.3), 0.35 + 0.65 * appear))

    # ============ 右下：组织徽标 + 解密工程档案
    cv.box(124, 23, 36, 15, ev["file"], panel_col, fill=" ")
    draw_org(cv, 151, 29, 3, ev["org"], mix(VIOLET, WARN, 0.6), t)
    for i, s in enumerate(ev["lines"]):
        y = 25 + i * 2
        if y > 35:
            break
        n = int((t - cuts[ncut - 1] if ncut else t) * 60) - i * 12
        cv.text(126, y, s[:23], scale(mix(AMBER, WARN, 0.35), 0.5 + 0.5 * min(1, max(0, n) / 10)))

    # 底部警戒行
    warn = " !! NUCLEAR DETONATION DETECTED // CIVIL DEFENSE WARNING // "
    if int(t * 1.5) % 3 == 0:
        off = int(t * 22) % len(warn)
        cv.text(0, 38, (warn + warn)[off:off + 156], mix(ALERT, WARN, 0.5 + 0.5 * beat))

    # 核爆闪光（试验/起爆）
    flash = 0.0
    for ft in (133.2, 139.6, 146.2, 152.4):
        if 0 <= t - ft < 1.6:
            flash = max(flash, 1.0 - (t - ft) / 1.6)
            rad = (t - ft) * 30.0
            for i in range(64):
                a = i * math.pi / 32
                x = 62 + math.sin(a) * rad
                y = 22 + math.cos(a) * rad * 0.5
                cv.set(int(x), int(y), "*", mix(WHITE, ALERT, 0.3))
    if flash > 0:
        for i in range(W * H):
            cv.fg[i] = mix(cv.fg[i], WHITE, flash * 0.38)
    cut_effect(cv, t, cuts)
# ------------------------------------------------------------------ scene 6
def scene_detente(cv, t, st):
    u = t - 158.0
    calm = clamp(u / 15.0, 0.0, 1.0)
    beat = st.pulse(t) * (1 - 0.7 * calm)

    cv.clear(" ", 0)
    MX, MY, MW_, MH_ = 10, 6, 140, 28

    # map with dissolving borders
    from scenes1 import draw_map_grid
    draw_map_grid(cv, MX, MY, MW_, MH_, 158.0 + u * (1 - 0.6 * calm), jitter=0.35 * (1 - calm))
    for ry in range(MH_):
        for rx in range(MW_):
            x, y = MX + rx, MY + ry
            i = y * W + x
            if cv.ch[i] == ":" and hash2(rx, ry, 31) < calm * 1.15:
                cv.ch[i] = " " if hash2(rx, ry, 32) < 0.7 else "."
                cv.fg[i] = scale(cv.fg[i], 0.4)

    # curtain line dissolving
    cx, _ = equirect(11.5, 0, MX, MY, MW_, MH_)
    for ry in range(MH_):
        lat = 83.0 + (ry + 0.5) / MH_ * -141.0
        if 36 < lat < 58 and hash2(ry, int(u * 2), 5) > calm * 1.1:
            cv.set(int(cx), MY + ry, "|" if calm < 0.6 else ".", mix(ALERT, WARN, 0.4))

    # merged data streams
    for y in range(4, 40):
        for k in range(10):
            u2 = (t * 0.45 + k * 0.1 + y * 0.13) % 1.0
            if u2 < 0.5:
                x = u2 * 2 * 74
                col = mix(MAIN, BRIGHT, 0.2)
                c = "0123456789ABCDEF"[int(hash2(y, k, int(t * 4)) * 16)]
            else:
                x = W - 1 - (u2 - 0.5) * 2 * 74
                col = mix(ALERT, WARN, 0.3)
                c = "FEDCBA9876543210"[int(hash2(y, k, int(t * 4) + 5) * 16)]
            # converge toward the middle band as the section progresses
            x = lerp(x, 80 + (x - 80) * (1 - 0.55 * calm), calm)
            y2 = lerp(y, 22 + (y - 22) * (1 - 0.5 * calm), calm)
            col = mix(col, mix(GREEN, WHITE, 0.4), calm * 0.8)
            cv.set(int(x), int(y2), c, scale(col, 0.35 + 0.4 * (1 - calm)))

    # quieting radar
    draw_x = 80.0
    rad = 26.0
    for k in range(3):
        r = rad * (0.32 + 0.32 * k)
        for i in range(64):
            a = i * math.pi / 32
            cv.set(int(draw_x + math.cos(a) * r), int(23 + math.sin(a) * r * 0.45),
                   ".", scale(GREEN, (0.35 - 0.08 * k) * (1 - 0.6 * calm)))
    ang = t * 1.4 * (1 - 0.85 * calm)
    for i in range(int(rad * (1 - 0.5 * calm))):
        cv.set(int(draw_x + math.cos(ang) * i), int(23 + math.sin(ang) * i * 0.45),
               "-", scale(GREEN, 0.5 * (1 - 0.7 * calm)))

    # status text
    lines = [
        (0.0, "ALERT STATUS: STANDING DOWN", WARN),
        (1.5, "DEFCON: 5  //  FORCE POSTURE: PEACETIME", GREEN),
        (3.2, "BORDER INTEGRITY: %3d%%" % int(100 * (1 - calm)), mix(MAIN, WARN, calm)),
        (5.0, "CHANNELS MERGED: 1/1", GREEN),
        (6.8, "TRAFFIC CLASS: DIPLOMATIC / CIVIL", DATA),
        (8.6, "RADAR NET: STANDBY", DATA),
        (10.4, "MISSILE TRACKS: 0", GREEN),
        (12.2, "THE SYSTEM IS QUIETING.", mix(GREEN, BRIGHT, 0.4)),
    ]
    # vertical status list on the left edge
    cv.box(0, 6, 38, 20, "STATUS", scale(DATA, 0.75), fill=" ")
    for i, (tt, s, col) in enumerate(lines):
        y = 8 + i * 2
        if u > tt and y < 24:
            n = int((u - tt) * 42)
            text_auto(cv, 2, y, s[:n], scale(col, 0.55 + 0.35 * clamp((u - tt) / 3, 0, 1)))

    if calm > 0.75:
        cv.center(40, "// NO ACTIVE THREATS DETECTED // SYSTEM ARCHIVING //", scale(GREEN, 0.5))


# ------------------------------------------------------------------ scene 7
# 逐句终端查询：英文原文 + 中文翻译 + 出处
CN = mix(GREEN, WHITE, 0.35)

BLOCKS = [
    (175.0, [
        ("> ARCHIVE SESSION 0x0191 // HISTORICAL ASSESSMENT", GREEN, 0.010),
        ('> QUERY --define "COLD WAR"', BRIGHT, 0.010),
        ("COLD WAR (n.)  1947 - 1991", MAIN, 0.004),
        ("一场旷日持久的地缘政治对抗：以代理人、以协议、以备战进行，", CN, 0.004),
        ("而不是两个大国之间的直接战争。", CN, 0.004),
        ("A PROLONGED CONFRONTATION WAGED BY PROXY, BY PROTOCOL", MAIN, 0.004),
        ("AND BY PREPARATION, RATHER THAN BY DIRECT WAR.", MAIN, 0.004),
        ("-- SOURCE: HISTORICAL KNOWLEDGE BASE / SYSTEM SUMMARY", DATA, 0.004),
    ]),
    (177.9, [
        ('> QUERY QUOTATION --topic "IRON CURTAIN"', BRIGHT, 0.010),
        ('"From Stettin in the Baltic to Trieste in the Adriatic,', WARN, 0.004),
        (' an iron curtain has descended across the Continent."', WARN, 0.004),
        ("“从波罗的海的什切青到亚得里亚海的的里雅斯特，", CN, 0.004),
        ("一道铁幕已经横贯欧洲大陆落下。”", CN, 0.004),
        ("-- WINSTON CHURCHILL, FULTON, MISSOURI, 5 MARCH 1946", DATA, 0.004),
    ]),
    (180.2, [
        ("> QUERY QUOTATION --topic COST OF ARMAMENT", BRIGHT, 0.010),
        ('"Every gun that is made, every warship launched, every', WARN, 0.004),
        (' rocket fired signifies, in the final sense, a theft', WARN, 0.004),
        (' from those who hunger and are not fed."', WARN, 0.004),
        ("“每一门制造的大炮、每一艘下水的军舰、每一枚发射的火箭，", CN, 0.004),
        ("归根结底都是对忍饥挨饿者的掠夺。”", CN, 0.004),
        ("-- DWIGHT D. EISENHOWER, 'THE CHANCE FOR PEACE',", DATA, 0.004),
        ("   16 APRIL 1953", DATA, 0.004),
    ]),
    (183.0, [
        ("> QUERY QUOTATION --topic COMMON GROUND", BRIGHT, 0.010),
        ('"For in the final analysis, our most basic common link', WARN, 0.004),
        (' is that we all inhabit this small planet. We all breathe', WARN, 0.004),
        (" the same air. We all cherish our children's futures.", WARN, 0.004),
        (' And we are all mortal."', WARN, 0.004),
        ("“归根结底，我们最基本的共同之处在于：", CN, 0.004),
        ("我们都栖身于这颗小小的星球，呼吸着同样的空气，", CN, 0.004),
        ("都珍视子女的未来，而我们也都是凡人。”", CN, 0.004),
        ("-- JOHN F. KENNEDY, AMERICAN UNIVERSITY, 10 JUNE 1963", DATA, 0.004),
    ]),
    (186.1, [
        ("> QUERY STATEMENT --topic THE WALL", BRIGHT, 0.010),
        ('"Mr. Gorbachev, tear down this wall!"', WARN, 0.004),
        ("“戈尔巴乔夫先生，推倒这堵墙！”", CN, 0.004),
        ("-- RONALD REAGAN, BRANDENBURG GATE, 12 JUNE 1987", DATA, 0.004),
    ]),
    (187.7, [
        ("> QUERY: 冷战结束之后，历史去了哪里", BRIGHT, 0.010),
        ("> ANSWER: 检索全部已解密记录，正在重现 ...", GREEN, 0.010),
    ]),
]


ARCHIVE_INDEX = [
    "COLDWAR/1945/YALTA.LOG",
    "COLDWAR/1946/FULTON.LOG",
    "COLDWAR/1947/CONTAINMENT.DOC",
    "COLDWAR/1948/BERLIN_BLOCKADE.LOG",
    "COLDWAR/1949/NATO_CHARTER.DOC",
    "COLDWAR/1953/CHANCE_FOR_PEACE.TXT",
    "COLDWAR/1955/WARSAW_PACT.DOC",
    "COLDWAR/1957/SPUTNIK.LOG",
    "COLDWAR/1961/BERLIN_WALL.LOG",
    "COLDWAR/1962/CARIBBEAN_CRISIS.LOG",
    "COLDWAR/1963/AMERICAN_UNIVERSITY.TXT",
    "COLDWAR/1972/SALT_I.TREATY",
    "COLDWAR/1975/APOLLO_SOYUZ.LOG",
    "COLDWAR/1987/BRANDENBURG.TXT",
    "COLDWAR/1989/CROSSINGS_OPEN.LOG",
    "COLDWAR/1991/REUNIFICATION.DOC",
    "COLDWAR/1991/START_I.TREATY",
    "COLDWAR/1991/DISSOLUTION.LOG",
    "COLDWAR/INDEX/SEAL_0x0191.DAT",
    "COLDWAR/INDEX/OPEN_QUESTIONS.DAT",
]

# 全片史料语录库（原文 / 中文翻译 / 出处）：铺满全屏时逐条排布、不重复使用
ARCHIVE_QUOTES = [
    ('"Whoever occupies a territory also imposes on it his own social system '
     'as far as his army has the power to do so."',
     "「谁占领了一片领土，谁就在那里推行自己的社会制度，直到他的军队所能到达之处。」",
     "JOSEPH STALIN, YALTA CONFERENCE, FEBRUARY 1945"),
    ('"From Stettin in the Baltic to Trieste in the Adriatic, '
     'an iron curtain has descended across the Continent."',
     "「从波罗的海的什切青到亚得里亚海的的里雅斯特，一道铁幕已经横贯欧洲大陆落下。」",
     "WINSTON CHURCHILL, FULTON, MISSOURI, 5 MARCH 1946"),
    ('"We must build a kind of United States of Europe."',
     "「我们必须建立某种形式的欧洲合众国。」",
     "WINSTON CHURCHILL, ZURICH, 19 SEPTEMBER 1946"),
    ('"I believe that it must be the policy of the United States to support '
     'free peoples who are resisting attempted subjugation by armed minorities '
     'or by outside pressures."',
     "「我相信，美国的政策必须是支持那些正在抵抗少数武装分子或外来压力企图征服的自由人民。」",
     "HARRY S. TRUMAN, ADDRESS TO CONGRESS, 12 MARCH 1947"),
    ('"Soviet power is impervious to the logic of reason, '
     'but it is highly sensitive to the logic of force."',
     "「苏维埃政权对理性的逻辑无动于衷，却对武力的逻辑高度敏感。」",
     "GEORGE F. KENNAN ('X'), FOREIGN AFFAIRS, JULY 1947"),
    ('"It is logical that the United States should do whatever it is able to do '
     'to assist in the return of normal economic health in the world."',
     "「美国理应尽其所能，帮助世界经济恢复正常——这是合乎逻辑的。」",
     "GEORGE C. MARSHALL, HARVARD, 5 JUNE 1947"),
    ('"Every gun that is made, every warship launched, every rocket fired '
     'signifies, in the final sense, a theft from those who hunger and are not fed."',
     "「每一门制造的大炮、每一艘下水的军舰、每一枚发射的火箭，归根结底都是对忍饥挨饿者的掠夺。」",
     "DWIGHT D. EISENHOWER, 'THE CHANCE FOR PEACE', 16 APRIL 1953"),
    ('"Whether you like it or not, history is on our side. We will bury you."',
     "「不管你们喜不喜欢，历史在我们这一边。我们将会埋葬你们。」",
     "NIKITA KHRUSHCHEV, 18 NOVEMBER 1956"),
    ('"In the councils of government, we must guard against the acquisition of '
     'unwarranted influence, whether sought or unsought, by the military-industrial complex."',
     "「在政府的议事机构中，我们必须警惕军工复合体获取不正当的影响力——无论这种影响是主动寻求还是不请自来。」",
     "DWIGHT D. EISENHOWER, FAREWELL ADDRESS, 17 JANUARY 1961"),
    ('"Let us never negotiate out of fear. But let us never fear to negotiate."',
     "「让我们永远不要出于恐惧而谈判；但让我们也永远不要惧怕谈判。」",
     "JOHN F. KENNEDY, INAUGURAL ADDRESS, 20 JANUARY 1961"),
    ('"We choose to go to the moon in this decade and do the other things, '
     'not because they are easy, but because they are hard."',
     "「我们选择在这个十年内登上月球，并完成其他事情——不是因为它们容易，而是因为它们困难。」",
     "JOHN F. KENNEDY, RICE UNIVERSITY, 12 SEPTEMBER 1962"),
    ('"It shall be the policy of this nation to regard any nuclear missile '
     'launched from Cuba against any nation in the Western Hemisphere as an attack '
     'by the Soviet Union on the United States."',
     "「本国的政策是：任何从古巴射向西半球国家的核导弹，都将被视为苏联对美国的攻击。」",
     "JOHN F. KENNEDY, TELEVISION ADDRESS, 22 OCTOBER 1962"),
    ('"I am prepared to wait for my answer until hell freezes over."',
     "「我准备等你的回答，直到地狱冰封。」",
     "ADLAI STEVENSON, UN SECURITY COUNCIL, 25 OCTOBER 1962"),
    ('"For in the final analysis, our most basic common link is that we all '
     'inhabit this small planet. We all breathe the same air. '
     'We all cherish our children\'s futures. And we are all mortal."',
     "「归根结底，我们最基本的共同之处在于：我们都栖身于这颗小小的星球，呼吸着同样的空气，都珍视子女的未来，而我们也都是凡人。」",
     "JOHN F. KENNEDY, AMERICAN UNIVERSITY, 10 JUNE 1963"),
    ('"All free men, wherever they may live, are citizens of Berlin, and, '
     'therefore, as a free man, I take pride in the words \'Ich bin ein Berliner\'."',
     "「一切自由的人，无论身在何处，都是柏林的公民；因此，作为一个自由人，我以『我是一个柏林人』为荣。」",
     "JOHN F. KENNEDY, WEST BERLIN, 26 JUNE 1963"),
    ('"Now I am become Death, the destroyer of worlds."',
     "「现在我成了死神，世界的毁灭者。」",
     "J. R. OPPENHEIMER, ON THE TRINITY TEST, 1945"),
    ('"I know not with what weapons World War III will be fought, '
     'but World War IV will be fought with sticks and stones."',
     "「我不知道第三次世界大战用什么武器，但第四次世界大战一定是用棍棒和石头。」",
     "ATTRIBUTED TO ALBERT EINSTEIN"),
    ('"We must learn to live together as brothers or perish together as fools."',
     "「我们要么学会像兄弟一样共同生活，要么像愚人一样一同灭亡。」",
     "MARTIN LUTHER KING JR."),
    ('"Peace, progress, human rights - these three goals are indissolubly linked."',
     "「和平、进步、人权——这三个目标不可分割地联系在一起。」",
     "ANDREI SAKHAROV, NOBEL LECTURE, 1975"),
    ('"The line separating good and evil passes not through states, nor between '
     'classes, nor between political parties - but right through every human heart."',
     "「善恶的分界线不在国家之间，不在阶级之间，也不在政党之间——它穿过每一个人的心。」",
     "ALEXANDR SOLZHENITSYN, 'THE GULAG ARCHIPELAGO'"),
    ('"Do not be afraid."',
     "「不要害怕。」",
     "POPE JOHN PAUL II, INAUGURAL HOMILY, 22 OCTOBER 1978"),
    ('"We may be heading not for general breakdown but for an age as horribly '
     'stable as the slave empires of antiquity."',
     "「我们走向的也许不是全面崩溃，而是一个像古代奴隶帝国一样可怕的稳定时代。」",
     "GEORGE ORWELL, 'YOU AND THE ATOMIC BOMB', 1945"),
    ('"A nuclear war cannot be won and must never be fought."',
     "「核战争打不赢，也绝不能打。」",
     "RONALD REAGAN, STATE OF THE UNION, 25 JANUARY 1984"),
    ('"I like Mr. Gorbachev - we can do business together."',
     "「我喜欢戈尔巴乔夫先生——我们可以共事。」",
     "MARGARET THATCHER, DECEMBER 1984"),
    ('"Mr. Gorbachev, tear down this wall!"',
     "「戈尔巴乔夫先生，推倒这堵墙！」",
     "RONALD REAGAN, BRANDENBURG GATE, 12 JUNE 1987"),
    ('"As long as this gate is closed, as long as this scar of a wall is permitted '
     'to stand, it is not the German question alone that remains open, '
     'but the question of freedom for all mankind."',
     "「只要这扇大门还关着，只要这道墙的伤疤还被允许立着，悬而未决的就不只是德国问题，而是全人类的自由问题。」",
     "RONALD REAGAN, BRANDENBURG GATE, 12 JUNE 1987"),
    ('"Hope is not the conviction that something will turn out well, but the '
     'certainty that something makes sense regardless of how it turns out."',
     "「希望不是相信事情终将好转，而是相信事情本身有意义，无论结局如何。」",
     "VACL HAVEL"),
]

# 尾声节奏：逐句查询 -> 引文铺满全屏 -> 逐行涂黑 -> 负形标题 -> 高亮填充
T_WALL = 188.6        # 引文开始铺满全屏
T_BLACK = 191.6       # 逐行涂黑开始（较原设计提前 2 秒）
BLACK_DUR = 5.0       # 涂黑持续时间（行 1..38）
T_FILL = T_BLACK + BLACK_DUR   # 负形完成后高亮填充
T_CODA = 198.8        # 收束文字


def _wrap_wide(s, w):
    """按显示宽度折行（CJK 占两格）。"""
    lines, cur, curw = [], [], 0
    for ch in s:
        cw = 2 if is_wide(ch) else 1
        if curw + cw > w and cur:
            lines.append("".join(cur))
            cur, curw = [], 0
        cur.append(ch)
        curw += cw
    if cur:
        lines.append("".join(cur))
    return lines


def _build_wall():
    """把史料语录库拼成连续文本流铺满整屏：单遍排完，不重复使用素材。"""
    colors = [WARN, CN, DATA, mix(MAIN, BRIGHT, 0.3)]
    segs = []
    for (en, cn, src) in ARCHIVE_QUOTES:
        segs.append(en)
        segs.append(cn)
        segs.append("-- " + src)
    stream = "   //   ".join(segs) + "   //   "
    rows = []
    cycle = 0
    while len(rows) < 45:
        off = (cycle * 47) % len(stream)        # 万一需要续排，错位避免折行重复
        pieces = _wrap_wide(stream[off:] + stream[:off], 156)
        for piece in pieces:
            rows.append((piece, colors[len(rows) % len(colors)]))
            if len(rows) >= 45:
                break
        cycle += 1
    return rows


WALL_ROWS = _build_wall()

_LW = big_text_width("COLD WAR", 2)
LETTER_CELLS = set((x, y) for (x, y, _c) in
                   big_text_cells("COLD WAR", (W - _LW) // 2, 15, 2, 2))


def scene_eval(cv, t, st):
    cv.clear(" ", 0)
    fade = 1.0
    if t > 200.4:
        fade = clamp(1.0 - (t - 200.4) / 0.8, 0.08, 1.0)

    if t < T_WALL:
        # ---------- 终端阶段：逐句查询 + 引文 + 中文翻译 ----------
        cv.box(110, 3, 48, 36, "ARCHIVE INDEX", scale(DATA, 0.7), fill=" ")
        for i in range(15):
            s = ARCHIVE_INDEX[(i + int(t * 0.22)) % len(ARCHIVE_INDEX)]
            cv.text(112, 5 + i * 2, s[:44], scale(DATA, 0.4 + 0.25 * ((i + int(t)) % 3 == 0)))
        cv.text(112, 37, "RECORDS: %05d  SEALED: %05d" % (len(ARCHIVE_QUOTES), len(ARCHIVE_QUOTES)),
                scale(DIM, 1.2))

        lines = []
        for (t0, block) in BLOCKS:
            if t < t0:
                break
            tt = t0
            for (s, col, cps) in block:
                if t < tt:
                    break
                n = len(s) if cps <= 0.004 and t > tt + 0.4 else int((t - tt) / max(cps, 0.0008))
                lines.append((s[: n + 1], col))
                tt += len(s) * cps + 0.12

        top, bottom = 3, 38
        avail = bottom - top + 1
        off = max(0, len(lines) - avail)
        shown = lines[off:off + avail]
        for i, (s, col) in enumerate(shown):
            text_auto(cv, 2, top + i, s, scale(col, fade))
        cur_y = min(bottom, top + len(shown))
        blink = math.sin(t * 4.4) > 0
        last = lines[-1][0] if lines else ""
        cv.set(2 + min(width_of(last), W - 6), cur_y, "█" if blink else "_",
               scale(GREEN, 0.9 * fade))
        return

    # ---------- 引文铺满全屏 ----------
    for idx, (s, col) in enumerate(WALL_ROWS[:38]):
        y = idx + 1
        start = T_WALL + idx * 0.025
        if t < start:
            continue
        n = int((t - start) * 320)
        # 字母区域先微微透亮，为负形标题埋下伏笔
        k = 0.82 + 0.18 * math.sin(t * 1.7 + idx)
        line_col = scale(col, k * fade)
        text_auto(cv, 1, y, s[:n], line_col)
        for x in range(1, 157):
            if (x, y) in LETTER_CELLS:
                i = y * W + x
                cv.fg[i] = mix(cv.fg[i], mix(WARN, WHITE, 0.45), 0.32)
                if cv.ch[i] == " ":
                    cv.ch[i] = "·"

    # 缓慢扫描高亮行
    sy = 1 + int((t * 7.0) % 38)
    for x in range(W):
        i = sy * W + x
        cv.fg[i] = mix(cv.fg[i], BRIGHT, 0.22)

    # ---------- 逐行涂黑，负形留下 COLD WAR ----------
    if t >= T_BLACK:
        edge = clamp((t - T_BLACK) / BLACK_DUR, 0.0, 1.0) * 38.0
        full = int(edge)
        frac = edge - full
        letter_col = mix(WARN, WHITE, 0.72)
        for y in range(1, 39):
            if y < full:
                xr = W
            elif y == full:
                xr = int(frac * W)
            else:
                continue
            for x in range(xr):
                i = y * W + x
                if (x, y) in LETTER_CELLS:
                    if cv.ch[i] == " ":
                        cv.ch[i] = "·"
                    cv.fg[i] = scale(mix(letter_col, cv.fg[i], 0.12), fade)
                else:
                    cv.ch[i] = "█"
                    cv.fg[i] = rgb(15, 18, 20)

    # ---------- 负形完成后：高亮度字符填充负形区域，增强对比 ----------
    fill = clamp((t - T_FILL) / 0.9, 0.0, 1.0)
    if fill > 0:
        bright_col = mix(WARN, WHITE, 0.82)
        for (x, y) in LETTER_CELLS:
            if y >= 39:
                continue
            if hash2(x, y, 7) < fill:
                i = y * W + x
                cv.ch[i] = "█" if hash2(x, y, 11) > 0.22 else "▓"
                cv.fg[i] = scale(bright_col, fade)

    # ---------- 收束 ----------
    if t >= T_CODA:
        n1 = int((t - T_CODA) / 0.016)
        text_auto(cv, (W - 42) // 2, 33,
                  "THE COLD WAR IS OVER. THE RECORD REMAINS."[:n1],
                  scale(mix(GREEN, WHITE, 0.35), 0.85 * fade))
        n2 = int((t - T_CODA - 1.0) / 0.03)
        if n2 > 0:
            text_auto(cv, (W - 30) // 2, 35,
                      "冷战已经结束，但历史仍然存在。"[:n2],
                      scale(mix(GREEN, WHITE, 0.55), 0.9 * fade))
