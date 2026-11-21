#!/usr/bin/env python3
"""Generates every SVG in ../assets. Run from repo root:
   cd tools && npm i simple-icons devicon && cd .. && python3 tools/build_assets.py
Edit the data dictionaries below, re-run, commit the SVGs."""
import json, os, re, subprocess, math
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NM = os.path.join(ROOT, "tools", "node_modules")
OUT = os.path.join(ROOT, "assets"); PRJ = os.path.join(OUT, "projects"); BTN = os.path.join(OUT, "buttons")
for d in (OUT, PRJ, BTN): os.makedirs(d, exist_ok=True)

# ---------- palette ----------
SLATE_D, SLATE, DUSTY, SAGE, LAV, GREIGE = "#4E6076", "#64748B", "#748BA3", "#8FAEA3", "#A49BBE", "#B4ACA4"
CHAR, PEARL, PEARL2 = "#25313D", "#E5E7E5", "#F4F5F2"
ICON = "#4A5D70"

CSS = """text{font-family:'Manrope','Plus Jakarta Sans','Inter','Segoe UI',Helvetica,Arial,sans-serif}
@keyframes flow{to{stroke-dashoffset:-96}}
@keyframes pulse{0%,100%{opacity:.3;transform:scale(1)}50%{opacity:.85;transform:scale(1.5)}}
@keyframes drift{0%,100%{transform:translate(0,0)}50%{transform:translate(22px,-14px)}}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes twinkle{0%,100%{opacity:.15}50%{opacity:.7}}
.flow{stroke-dasharray:5 9;animation:flow 7s linear infinite}
.pulse{transform-box:fill-box;transform-origin:center;animation:pulse 5s ease-in-out infinite}
.drift{animation:drift 16s ease-in-out infinite}
.spin{transform-box:fill-box;transform-origin:center;animation:spin 120s linear infinite}
.tw{animation:twinkle 6s ease-in-out infinite}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}"""

def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
def svg(w, h, body, title, desc=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-labelledby="t d">'
            f'<title id="t">{esc(title)}</title><desc id="d">{esc(desc or title)}</desc><style>{CSS}</style>{body}</svg>')
def write(path, s):
    with open(path, "w", encoding="utf-8") as f: f.write(s)

def bg(w, h, stops, blobs, rx=0, gid="g"):
    st = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
    bl = "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}" opacity="{o}"/>' for x, y, r, c, o in blobs)
    return (f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="0.55">{st}</linearGradient>'
            f'<filter id="bl" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="55"/></filter>'
            f'<clipPath id="cp"><rect width="{w}" height="{h}" rx="{rx}"/></clipPath></defs>'
            f'<g clip-path="url(#cp)"><rect width="{w}" height="{h}" fill="url(#{gid})"/>'
            f'<g class="drift" filter="url(#bl)">{bl}</g>'
            f'<g stroke="{PEARL}" stroke-opacity=".07" stroke-width="1">'
            + "".join(f'<path d="M{x} 0V{h}"/>' for x in range(0, w + 1, 50))
            + "".join(f'<path d="M0 {y}H{w}"/>' for y in range(0, h + 1, 50)) + '</g>')
def endbg(): return "</g>"

# ---------- icons ----------
SI = None
def si_all():
    global SI
    if SI is None:
        js = "const s=require('simple-icons');const o={};for(const k in s){if(k.startsWith('si'))o[k.slice(2).toLowerCase()]=s[k].path;}console.log(JSON.stringify(o))"
        SI = json.loads(subprocess.check_output(["node", "-e", js], cwd=os.path.join(ROOT, "tools")))
    return SI
def dev(name):
    raw = open(os.path.join(NM, "devicon", "icons", name, f"{name}-plain.svg"), encoding="utf-8").read()
    inner = re.sub(r"^.*?<svg[^>]*>", "", raw, flags=re.S); inner = re.sub(r"</svg>\s*$", "", inner)
    return re.sub(r'\s(fill|class|style)="[^"]*"', "", inner)
DEVICON = {"java": "java", "aws": "amazonwebservices", "css3": "css3"}
def icon(key, x, y, size, color=ICON):
    if key in DEVICON:
        return f'<g transform="translate({x},{y}) scale({size/128:.4f})" fill="{color}">{dev(DEVICON[key])}</g>'
    p = si_all()[key]
    return f'<g transform="translate({x},{y}) scale({size/24:.4f})"><path d="{p}" fill="{color}"/></g>'
def glyph(txt, x, y, size, color=ICON):
    fs = 10 if len(txt) <= 3 else 8
    return (f'<rect x="{x+1}" y="{y+size*0.16:.1f}" width="{size-2}" height="{size*0.68:.1f}" rx="7" fill="none" stroke="{color}" stroke-width="1.8"/>'
            f'<text x="{x+size/2}" y="{y+size/2+fs*0.36:.1f}" font-size="{fs}" font-weight="800" fill="{color}" text-anchor="middle">{esc(txt)}</text>')

# ---------- KS monogram ----------
KS = ('<path d="M66 64V176M66 122L112 64M82 111L116 176" />'
      '<path d="M182 84C170 64 134 66 132 92C130 116 182 120 180 152C178 182 140 184 124 160" />')
def monogram(x, y, s, stroke=PEARL2, w=14):
    return f'<g transform="translate({x},{y}) scale({s/240:.4f})" fill="none" stroke="{stroke}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round">{KS}</g>'

def build_monogram():
    b = (f'<defs><linearGradient id="m" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{SLATE_D}"/><stop offset=".5" stop-color="{DUSTY}"/>'
         f'<stop offset=".8" stop-color="{SAGE}"/><stop offset="1" stop-color="{LAV}"/></linearGradient></defs>'
         f'<rect width="240" height="240" rx="58" fill="url(#m)"/><rect x="10" y="10" width="220" height="220" rx="50" fill="none" stroke="{PEARL}" stroke-opacity=".35"/>'
         f'<g fill="none" stroke="{PEARL2}" stroke-width="14" stroke-linecap="round" stroke-linejoin="round">{KS}</g>'
         f'<circle cx="112" cy="64" r="6" fill="{PEARL2}"/><circle cx="124" cy="160" r="6" fill="{PEARL2}"/>')
    write(f"{OUT}/ks-monogram.svg", svg(240, 240, b, "KS monogram", "Monogram of the initials K and S in fine line strokes"))

# ---------- HERO ----------
def build_hero():
    W, H = 1000, 520
    b = bg(W, H, [(0, "#51647A"), (.5, "#6A8097"), (.8, "#7E9E9A"), (1, "#8D88AD")],
           [(820, 110, 220, SAGE, .6), (950, 470, 240, LAV, .55), (130, 40, 150, PEARL, .14), (520, 540, 160, "#7FA3A8", .4)], rx=22)
    C = (790, 262)
    b += f'<g fill="none" stroke="{PEARL}">'
    for r, o in ((78, .28), (140, .2), (202, .14)): b += f'<circle cx="{C[0]}" cy="{C[1]}" r="{r}" stroke-opacity="{o}"/>'
    b += f'<circle class="spin" cx="{C[0]}" cy="{C[1]}" r="170" stroke-opacity=".3" stroke-dasharray="2 12" stroke-linecap="round"/></g>'
    nodes = [("REST API", 700, 112), ("Database", 895, 100), ("CI/CD", 930, 262), ("Docker", 880, 420), ("Linux", 690, 424), ("Cloud", 636, 262)]
    # edges
    for i, (n, x, y) in enumerate(nodes):
        mx, my = (C[0] + x) / 2 + (y - C[1]) * 0.12, (C[1] + y) / 2 - (x - C[0]) * 0.12
        b += f'<path d="M{C[0]} {C[1]}Q{mx:.0f} {my:.0f} {x} {y}" fill="none" stroke="{PEARL}" stroke-opacity=".3"/>'
    for i in range(len(nodes)):
        a, c = nodes[i], nodes[(i + 1) % len(nodes)]
        b += f'<path class="flow" d="M{a[1]} {a[2]}L{c[1]} {c[2]}" fill="none" stroke="{PEARL2}" stroke-opacity=".55" stroke-width="1.4" style="animation-delay:{-i*1.1}s"/>'
    # particles
    for i, (x, y) in enumerate([(610, 90), (760, 40), (990, 170), (990, 400), (780, 500), (600, 470), (850, 190), (730, 330)]):
        b += f'<circle class="tw" cx="{x}" cy="{y}" r="2.2" fill="{PEARL2}" style="animation-delay:{-i*.8}s"/>'
    # center
    b += (f'<circle class="pulse" cx="{C[0]}" cy="{C[1]}" r="58" fill="{PEARL2}" opacity=".25"/>'
          f'<circle cx="{C[0]}" cy="{C[1]}" r="46" fill="{SLATE_D}" stroke="{PEARL2}" stroke-opacity=".7" stroke-width="1.5"/>'
          + monogram(C[0] - 26, C[1] - 26, 52, PEARL2, 15))
    for n, x, y in nodes:
        w = len(n) * 7.4 + 28
        b += (f'<circle class="pulse" cx="{x}" cy="{y}" r="5" fill="{PEARL2}" style="animation-delay:{-(x%5)}s"/>'
              f'<rect x="{x-w/2:.0f}" y="{y-14}" width="{w:.0f}" height="28" rx="14" fill="{PEARL}" fill-opacity=".92"/>'
              f'<text x="{x}" y="{y+4.5}" font-size="12.5" font-weight="700" fill="{CHAR}" text-anchor="middle">{esc(n)}</text>')
    # typography
    b += monogram(56, 40, 44, PEARL2, 15) + f'<text x="112" y="68" font-size="15" font-weight="600" fill="{PEARL2}" fill-opacity=".92">New Delhi, India</text>'
    b += (f'<text x="56" y="196" font-size="84" font-weight="800" fill="{PEARL2}" textLength="392" lengthAdjust="spacingAndGlyphs">KHUSHAL</text>'
          f'<text x="104" y="284" font-size="84" font-weight="800" fill="none" stroke="{PEARL2}" stroke-width="1.8" textLength="452" lengthAdjust="spacingAndGlyphs">SEHRAWAT</text>'
          f'<text x="58" y="338" font-size="19" font-weight="600" fill="{PEARL2}">Software Developer  /  Backend Engineer  /  DevOps &amp; Cloud</text>'
          f'<path d="M58 358H330" stroke="{PEARL2}" stroke-opacity=".55"/>'
          f'<text x="58" y="402" font-size="29" font-weight="500" fill="{PEARL2}" font-style="italic">From architecture to deployment.</text>'
          f'<text x="58" y="436" font-size="15.5" font-weight="500" fill="{PEARL2}">I build software systems, engineer backend platforms,</text>'
          f'<text x="58" y="458" font-size="15.5" font-weight="500" fill="{PEARL2}">and make applications deployment-ready.</text>'
          f'<text x="58" y="494" font-size="13.5" font-weight="600" fill="{PEARL2}" fill-opacity=".9">Open to Backend, DevOps and Cloud roles  ·  Freelance via TheBenzzCreations</text>')
    b += endbg()
    write(f"{OUT}/hero.svg", svg(W, H, b, "Khushal Sehrawat, Software Developer, Backend Engineer, DevOps and Cloud",
          "Hero banner: From architecture to deployment. Abstract infrastructure diagram connecting REST API, database, CI/CD, Docker, Linux and cloud."))

# ---------- SKILLS ----------
PRO, LAB = "pro", "lab"
GROUPS = [  # (title, subtitle, width, [(icon|None, label, glyph, status)])
 [("Backend", "Services, APIs and persistence", 470, [("openjdk", "Java", None, PRO), ("springboot", "Spring|Boot", None, PRO), ("springsecurity", "Spring|Security", None, LAB), ("hibernate", "Hibernate", None, PRO), ("apachemaven", "Maven", None, PRO), ("nodedotjs", "Node.js", None, PRO), ("express", "Express.js", None, PRO), (None, "REST APIs", "API", PRO)]),
  ("Frontend & mobile", "Web and cross-platform apps", 454, [("react", "React", None, PRO), ("nextdotjs", "Next.js", None, PRO), ("javascript", "JavaScript", None, PRO), ("html5", "HTML5", None, PRO), ("css3", "CSS3", None, PRO), ("react", "React|Native", None, PRO), ("expo", "Expo", None, PRO)])],
 [("DevOps & automation", "Build, test, publish, deploy", 470, [("docker", "Docker", None, PRO), ("docker", "Docker|Compose", None, PRO), ("githubactions", "GitHub|Actions", None, PRO), ("jenkins", "Jenkins", None, LAB), ("ansible", "Ansible", None, LAB), ("git", "Git", None, PRO), ("github", "GitHub", None, PRO)]),
  ("Cloud & infrastructure", "Linux hosts and AWS", 454, [("aws", "AWS", None, LAB), (None, "EC2", "EC2", LAB), (None, "S3", "S3", LAB), (None, "IAM", "IAM", LAB), (None, "CloudWatch", "CW", LAB), ("linux", "Linux", None, PRO), ("ubuntu", "Ubuntu", None, PRO), ("nginx", "Nginx", None, PRO)])],
 [("Databases", "Relational and vector storage", 462, [("mysql", "MySQL", None, PRO), ("postgresql", "PostgreSQL", None, PRO), ("mariadb", "MariaDB", None, PRO), (None, "PGVector", "pgv", LAB)]),
  ("AI & intelligent apps", "LLM features in Java backends", 462, [("spring", "Spring AI", None, LAB), (None, "LLM|integration", "LLM", LAB), (None, "RAG", "RAG", LAB), (None, "Vector|retrieval", "vec", LAB)])],
 [("Languages & scripting", "Day-to-day tools", 467, [("openjdk", "Java", None, PRO), ("javascript", "JavaScript", None, PRO), ("python", "Python", None, LAB), ("gnubash", "Bash", None, PRO), ("yaml", "YAML", None, PRO)]),
  ("Currently learning", "Next on the roadmap", 457, [("kubernetes", "Kubernetes", None, LAB), ("grafana", "Grafana", None, LAB), (None, "Infra|automation", "IaC", LAB), (None, "Container|orchestration", "K8s", LAB)])],
]
def build_skills():
    W, TW, TH = 1000, 87, 92
    y = 150; body = ""
    for row in GROUPS:
        rows_n = max(-(-len(g[3]) // int((g[2] - 32) // TW)) for g in row)
        ch = 62 + rows_n * TH + 18; x = 30
        for title, sub, w, items in row:
            cols = int((w - 32) // TW)
            body += (f'<rect x="{x}" y="{y}" width="{w}" height="{ch}" rx="18" fill="{PEARL}" fill-opacity=".9"/>'
                     f'<text x="{x+20}" y="{y+30}" font-size="16" font-weight="800" fill="{CHAR}">{esc(title)}</text>'
                     f'<text x="{x+20}" y="{y+49}" font-size="11.5" font-weight="600" fill="#53657A">{esc(sub)}</text>')
            for i, (ic, label, gl, stt) in enumerate(items):
                tx, ty = x + 16 + (i % cols) * TW, y + 60 + (i // cols) * TH
                body += f'<rect x="{tx+3}" y="{ty}" width="{TW-6}" height="{TH-8}" rx="12" fill="#FFFFFF" fill-opacity=".42" stroke="{CHAR}" stroke-opacity=".08"/>'
                body += icon(ic, tx + TW / 2 - 15, ty + 14, 30) if ic else glyph(gl, tx + TW / 2 - 15, ty + 12, 30)
                mk = (f'<circle cx="{tx+TW-14}" cy="{ty+13}" r="3.6" fill="{SLATE_D}"/>' if stt == PRO else
                      f'<circle cx="{tx+TW-14}" cy="{ty+13}" r="3.2" fill="none" stroke="{SLATE_D}" stroke-width="1.4"/>')
                body += mk
                parts = label.split("|")
                for j, p in enumerate(parts):
                    ly = ty + 62 + j * 13 if len(parts) > 1 else ty + 68
                    body += f'<text x="{tx+TW/2}" y="{ly}" font-size="11.5" font-weight="700" fill="{CHAR}" text-anchor="middle">{esc(p)}</text>'
            x += w + 16
        y += ch + 16
    H = y + 40
    head = bg(W, H, [(0, "#52657B"), (.45, "#6F869D"), (.8, "#7FA09A"), (1, "#948EB4")],
              [(850, 80, 200, SAGE, .6), (120, H - 60, 220, LAV, .45), (500, 40, 140, PEARL, .12)], rx=22)
    head += (f'<text x="30" y="62" font-size="34" font-weight="800" fill="{PEARL2}">Toolkit</text>'
             f'<text x="30" y="92" font-size="15.5" font-weight="500" fill="{PEARL2}">The technologies behind my work, grouped by what they do.</text>'
             f'<circle cx="38" cy="124" r="4.4" fill="{PEARL2}"/><text x="50" y="128.5" font-size="13" font-weight="600" fill="{PEARL2}">Used in professional or client work</text>'
             f'<circle cx="352" cy="124" r="4" fill="none" stroke="{PEARL2}" stroke-width="1.6"/><text x="364" y="128.5" font-size="13" font-weight="600" fill="{PEARL2}">Personal projects and hands-on labs</text>')
    write(f"{OUT}/skills.svg", svg(W, H, head + body + endbg(), "Technology toolkit",
          "Logos of Java, Spring Boot, Node.js, React, Docker, GitHub Actions, AWS, Linux, PostgreSQL and more, grouped into backend, frontend, DevOps, cloud, databases, AI, languages and learning."))

# ---------- EXPERIENCE ----------
EXP = [("Sep 2026 – Present", "Software Developer", "INOX Decor", "Current",
        ["Developing a React Native / Expo mobile app, Node.js / Express APIs and a Next.js website on MySQL / MariaDB.",
         "Owning delivery too: Docker environments on Linux, GitHub Actions builds, tests and image publishing, plus DNS, SSL and deployment troubleshooting."],
        ["React Native", "Expo", "Node.js", "Next.js", "MySQL / MariaDB", "Docker", "GitHub Actions"]),
       ("Jul 2025 – Aug 2026", "Freelance Software / Web Developer", "TheBenzzCreations", "Studio",
        ["Built and deployed client websites and backend APIs with Java / Spring Boot, Node.js and relational databases.",
         "Ran the hosting stack: Linux, Docker, Nginx, DNS and SSL/HTTPS, with CI/CD workflows and production issue resolution."],
        ["Spring Boot", "Node.js", "React / Next.js", "Docker", "Nginx", "DNS / SSL", "CI/CD"]),
       ("May 2024 – Jun 2025", "Software Developer", "Hurlad By The Eaglets", "",
        ["Developed Java / Spring Boot REST APIs and full-stack functionality for client applications.",
         "Worked across relational databases, Git / GitHub, testing, debugging and issue resolution."],
        ["Java", "Spring Boot", "REST APIs", "SQL databases", "Git"])]
def wrap(s, n):
    out, cur = [], ""
    for w in s.split():
        if len(cur) + len(w) + 1 > n: out.append(cur); cur = w
        else: cur = (cur + " " + w).strip()
    return out + [cur]
def build_experience():
    W = 1000; y0 = 170; step = 215; H = y0 + step * 3 - 20
    b = bg(W, H, [(0, "#4B5D73"), (.55, "#5C7189"), (1, "#6B7F98")], [(900, H - 80, 230, LAV, .4), (80, 60, 170, SAGE, .35)], rx=22)
    b += (f'<text x="40" y="70" font-size="34" font-weight="800" fill="{PEARL2}">Experience</text>'
          f'<text x="40" y="100" font-size="15.5" font-weight="500" fill="{PEARL2}">Professional and freelance engineering. Personal labs are listed with the projects.</text>')
    lx = 250
    b += f'<path d="M{lx} {y0-30}V{H-40}" stroke="{PEARL2}" stroke-opacity=".5" stroke-width="1.5"/>'
    for i, (date, role, co, tag, lines, chips) in enumerate(EXP):
        y = y0 + i * step
        b += f'<text x="40" y="{y+5}" font-size="15" font-weight="700" fill="{PEARL2}">{date}</text>'
        if i == 0: b += f'<circle class="pulse" cx="{lx}" cy="{y}" r="11" fill="{SAGE}"/>'
        b += f'<circle cx="{lx}" cy="{y}" r="7" fill="{PEARL2}" stroke="{SLATE_D}" stroke-width="2.5"/>'
        b += f'<text x="286" y="{y+6}" font-size="25" font-weight="800" fill="{PEARL2}">{esc(role)}</text>'
        rw = len(role) * 14.4 + 296
        b += f'<text x="286" y="{y+30}" font-size="16" font-weight="700" fill="#CFE0D9">{esc(co)}</text>'
        if tag:
            tw = len(tag) * 7.6 + 22; tx = 286 + len(co) * 9 + 14
            b += f'<rect x="{tx:.0f}" y="{y+15}" width="{tw:.0f}" height="22" rx="11" fill="{PEARL2}" fill-opacity=".18" stroke="{PEARL2}" stroke-opacity=".5"/><text x="{tx+tw/2:.0f}" y="{y+30.5}" font-size="11.5" font-weight="700" fill="{PEARL2}" text-anchor="middle">{tag}</text>'
        ty = y + 58
        for ln in lines:
            for w in wrap(ln, 82):
                b += f'<text x="286" y="{ty}" font-size="14.5" font-weight="500" fill="{PEARL2}">{esc(w)}</text>'; ty += 21
            ty += 5
        cx = 286; ty += 2
        for c in chips:
            cw = len(c) * 6.9 + 24
            b += (f'<rect x="{cx}" y="{ty-14}" width="{cw:.0f}" height="24" rx="12" fill="{PEARL2}" fill-opacity=".13" stroke="{PEARL2}" stroke-opacity=".38"/>'
                  f'<text x="{cx+cw/2:.0f}" y="{ty+2.5}" font-size="12" font-weight="600" fill="{PEARL2}" text-anchor="middle">{esc(c)}</text>')
            cx += cw + 8
    write(f"{OUT}/experience.svg", svg(W, H, b + endbg(), "Experience timeline",
          "INOX Decor (Sep 2026 to present), TheBenzzCreations freelance (Jul 2025 to Aug 2026), Hurlad By The Eaglets (May 2024 to Jun 2025)."))

# ---------- BENZZ ----------
SERVICES = ["Custom software development", "Full-stack web development", "Backend and API development", "E-commerce development", "Mobile applications", "AI integrations and automation", "Hosting, DevOps and deployment"]
def build_benzz():
    W, H = 1000, 420
    b = bg(W, H, [(0, "#BAB1A6"), (.4, "#A9A1C2"), (.75, "#88A8A2"), (1, "#748BA3")],
           [(120, 380, 200, PEARL, .3), (700, 60, 200, LAV, .5), (980, 400, 200, DUSTY, .5)], rx=22)
    b += f'<g fill="none" stroke="{CHAR}" stroke-opacity=".12">' + "".join(f'<circle cx="40" cy="430" r="{r}"/>' for r in (120, 180, 240, 300)) + '</g>'
    b += (f'<text x="44" y="90" font-size="40" font-weight="800" fill="{CHAR}" textLength="470" lengthAdjust="spacingAndGlyphs">THEBENZZCREATIONS</text>'
          f'<text x="46" y="122" font-size="17" font-weight="600" fill="{CHAR}">A digital engineering and development studio</text>'
          f'<path d="M46 146H200" stroke="{CHAR}" stroke-opacity=".55"/>'
          f'<text x="46" y="206" font-size="27" font-weight="500" fill="{CHAR}">Have a product idea?</text>'
          f'<text x="46" y="246" font-size="34" font-weight="800" fill="{CHAR}">Let’s engineer it.</text>'
          f'<rect x="46" y="282" width="300" height="52" rx="26" fill="{CHAR}"/>'
          f'<text x="196" y="314" font-size="15.5" font-weight="700" fill="{PEARL2}" text-anchor="middle">Explore TheBenzzCreations</text>'
          f'<text x="48" y="372" font-size="14" font-weight="600" fill="{CHAR}">thebenzzcreations.com</text>')
    b += f'<rect x="590" y="36" width="372" height="348" rx="22" fill="{PEARL}" fill-opacity=".55" stroke="{PEARL2}" stroke-opacity=".7"/>'
    b += f'<text x="616" y="76" font-size="15" font-weight="800" fill="{CHAR}">What the studio builds</text>'
    for i, s in enumerate(SERVICES):
        y = 112 + i * 38
        if i: b += f'<path d="M616 {y-22}H936" stroke="{CHAR}" stroke-opacity=".14"/>'
        b += (f'<rect x="616" y="{y-9}" width="9" height="9" rx="2.5" fill="{SLATE_D}"/><circle class="pulse" cx="620.5" cy="{y-4.5}" r="6" fill="{SLATE_D}" opacity=".3" style="animation-delay:{-i*.7}s"/>'
              f'<text x="638" y="{y+1}" font-size="15.5" font-weight="600" fill="{CHAR}">{esc(s)}</text>')
    write(f"{OUT}/thebenzzcreations.svg", svg(W, H, b + endbg(), "TheBenzzCreations, a digital engineering and development studio",
          "Services: custom software, full-stack web, backend and APIs, e-commerce, mobile apps, AI integrations, hosting and DevOps. Have a product idea? Let's engineer it."))

# ---------- PROJECT CARDS ----------
def motif_sentinel(c):
    s = ""
    for i in range(7):
        y = 28 + i * 16; x = 28 + (i * 37) % 70; L = 60 + (i * 53) % 90
        s += f'<path class="flow" d="M{x} {y}H{x+L}" stroke="{c}" stroke-width="2" stroke-linecap="round" style="animation-delay:{-i}s" fill="none"/>'
    s += f'<path d="M210 30L270 75L210 120" fill="none" stroke="{c}" stroke-opacity=".5"/><circle class="pulse" cx="285" cy="75" r="16" fill="{c}" opacity=".4"/><circle cx="285" cy="75" r="9" fill="{c}"/>'
    for i, (lab, w) in enumerate((("Low", 40), ("Medium", 70), ("High", 105))):
        y = 38 + i * 30
        s += f'<rect x="340" y="{y}" width="130" height="14" rx="7" fill="{c}" fill-opacity=".18"/><rect x="340" y="{y}" width="{w}" height="14" rx="7" fill="{c}" fill-opacity=".8"/>'
    return s
def motif_shrawn(c):
    import random; random.seed(7); s = ""
    for cx, cy, r in ((120, 70, 42), (255, 95, 38), (385, 55, 44)):
        s += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{c}" fill-opacity=".08" stroke="{c}" stroke-opacity=".55" stroke-dasharray="3 5"/>'
        for k in range(11):
            a = random.random() * 6.28; d = random.random() * (r - 8)
            s += f'<circle class="tw" cx="{cx+math.cos(a)*d:.0f}" cy="{cy+math.sin(a)*d:.0f}" r="{2+random.random()*2.4:.1f}" fill="{c}" style="animation-delay:{-random.random()*5:.1f}s"/>'
    s += f'<path d="M165 78Q210 120 220 98M295 90Q340 110 350 70" fill="none" stroke="{c}" stroke-opacity=".5"/>'
    return s
def motif_loan(c):
    s = ""
    for i, lab in enumerate(("Secure API", "Business logic", "Database")):
        y = 24 + i * 38; x = 110 + i * 22
        s += f'<rect x="{x}" y="{y}" width="230" height="30" rx="9" fill="{c}" fill-opacity="{.12+i*.08}" stroke="{c}" stroke-opacity=".6"/><text x="{x+115}" y="{y+19.5}" font-size="12.5" font-weight="700" fill="{c}" text-anchor="middle">{lab}</text>'
    s += f'<path class="flow" d="M72 40H110M72 78H132M72 116H154" stroke="{c}" stroke-width="1.8" fill="none"/><circle cx="64" cy="40" r="4" fill="{c}"/><circle cx="64" cy="78" r="4" fill="{c}"/><circle cx="64" cy="116" r="4" fill="{c}"/>'
    s += f'<rect x="402" y="52" width="46" height="38" rx="8" fill="none" stroke="{c}" stroke-width="2"/><path d="M413 52V44a12 12 0 0 1 24 0v8" fill="none" stroke="{c}" stroke-width="2"/><circle cx="425" cy="70" r="4" fill="{c}"/>'
    return s
def motif_dusky(c):
    s = f'<circle cx="250" cy="38" r="22" fill="none" stroke="{c}" stroke-width="2"/><text x="250" y="42" font-size="11.5" font-weight="800" fill="{c}" text-anchor="middle">RBAC</text>'
    for i, x in enumerate((120, 250, 380)):
        s += f'<path class="flow" d="M250 60Q{x} 70 {x} 98" stroke="{c}" fill="none" stroke-width="1.6" style="animation-delay:{-i}s"/><circle cx="{x}" cy="110" r="13" fill="{c}" fill-opacity=".22" stroke="{c}"/><circle cx="{x}" cy="106" r="4" fill="{c}"/><path d="M{x-7} 117a7 5 0 0 1 14 0" fill="{c}"/>'
    s += f'<path d="M60 140H440" stroke="{c}" stroke-opacity=".35" stroke-dasharray="2 6"/>'
    return s
def motif_suems(c):
    s = "".join(f'<path d="M30 {30+i*28}H470" stroke="{c}" stroke-opacity=".2"/>' for i in range(4))
    s += f'<path d="M30 112C80 112 90 60 140 70S210 118 260 84 340 30 390 52 450 80 470 60V122H30Z" fill="{c}" fill-opacity=".16"/>'
    s += f'<path d="M30 112C80 112 90 60 140 70S210 118 260 84 340 30 390 52 450 80 470 60" fill="none" stroke="{c}" stroke-width="2.4" stroke-linecap="round"/>'
    for x, y in ((140, 70), (260, 84), (390, 52)): s += f'<circle class="pulse" cx="{x}" cy="{y}" r="6" fill="{c}" opacity=".4"/><circle cx="{x}" cy="{y}" r="4" fill="{c}"/>'
    return s
def motif_labs(c):
    s = ""
    for i, lab in enumerate(("Build", "Test", "Image", "Publish")):
        x = 28 + i * 118
        s += f'<rect x="{x}" y="52" width="92" height="40" rx="10" fill="{c}" fill-opacity=".15" stroke="{c}" stroke-opacity=".7"/><text x="{x+46}" y="77" font-size="13" font-weight="700" fill="{c}" text-anchor="middle">{lab}</text>'
        if i < 3: s += f'<path class="flow" d="M{x+94} 72H{x+116}" stroke="{c}" stroke-width="2" fill="none"/>'
    s += f'<path d="M74 52C74 20 250 20 250 52" fill="none" stroke="{c}" stroke-opacity=".45" stroke-dasharray="3 5"/><text x="162" y="30" font-size="11.5" font-weight="600" fill="{c}" text-anchor="middle">GitHub webhook</text>'
    s += f'<text x="28" y="124" font-size="12" font-weight="600" fill="{c}" fill-opacity=".9">Jenkinsfile pipelines and Ansible playbooks</text>'
    return s
def motif_aws(c):
    s = f'<rect x="60" y="24" width="250" height="100" rx="16" fill="none" stroke="{c}" stroke-width="1.6" stroke-dasharray="6 6"/><text x="76" y="44" font-size="11.5" font-weight="700" fill="{c}">Security group</text>'
    for x in (84, 170): s += f'<rect x="{x}" y="62" width="64" height="44" rx="8" fill="{c}" fill-opacity=".18" stroke="{c}"/><text x="{x+32}" y="89" font-size="12.5" font-weight="800" fill="{c}" text-anchor="middle">EC2</text>'
    s += f'<path class="flow" d="M234 84H350" stroke="{c}" stroke-width="1.8" fill="none"/><ellipse cx="385" cy="60" rx="28" ry="9" fill="{c}" fill-opacity=".2" stroke="{c}"/><path d="M357 60v38c0 5 12 9 28 9s28-4 28-9V60" fill="{c}" fill-opacity=".12" stroke="{c}"/><text x="385" y="86" font-size="12" font-weight="800" fill="{c}" text-anchor="middle">S3</text>'
    s += f'<path d="M340 124l22-14 18 8 24-16 22 10" fill="none" stroke="{c}" stroke-width="1.8" stroke-linecap="round"/>'
    return s
def motif_all(c):
    s = ""
    for i in range(40):
        x = 70 + (i % 10) * 36; y = 28 + (i // 10) * 28
        s += f'<rect class="tw" x="{x}" y="{y}" width="24" height="18" rx="5" fill="{c}" fill-opacity=".25" stroke="{c}" stroke-opacity=".6" style="animation-delay:{-(i*0.37)%6:.1f}s"/>'
    return s
CARDS = [
 ("sentinelai", "SentinelAI", "AI-assisted security incident analysis", "Personal project", ["Containerized backend for security-log incident analysis:", "severity classification, contextual RAG analysis, JWT-protected", "APIs and incident history."], ["openjdk", "springboot", "docker", "mysql"], ["Java", "Spring Boot", "Docker", "MySQL"], motif_sentinel, "dark", [SLATE_D, "#6A8097", "#7B8FB0"]),
 ("shrawn", "SHRAWN", "SpendWise AI assistant", "Personal project", ["LLM-powered expense categorization with RAG-based financial", "insights, spending trends and monthly summaries, built on", "Spring AI with PostgreSQL and PGVector."], ["spring", "postgresql", "docker"], ["Spring AI", "PostgreSQL", "Docker"], motif_shrawn, "light", ["#86A69F", "#9CB5AE", "#A9A6C4"]),
 ("beneloan", "BeneLoan", "Secure backend and workflow management", "Personal project", ["Secure backend development and business workflow", "management built on Spring Boot with a relational database."], ["openjdk", "springboot"], ["Java", "Spring Boot"], motif_loan, "light", ["#B7AEA4", "#B1A8BD", "#A49BBE"]),
 ("duskyhospital", "DuskyHospital", "Healthcare backend with role-based access", "Personal project", ["Healthcare backend secured with Spring Security and", "role-based access control (RBAC) over its endpoints."], ["openjdk", "springboot", "springsecurity"], ["Java", "Spring Boot", "Spring Security"], motif_dusky, "dark", ["#6C6A93", "#6F7F9E", SLATE_D]),
 ("suems", "SUEMS", "Energy management and analytics", "Personal project", ["Energy management and analytics project focused on", "monitoring and understanding energy usage."], ["html5"], ["HTML5"], motif_suems, "light", ["#8FAEA3", "#A8B5AB", "#B4ACA4"]),
 ("cicd-labs", "Jenkins and Ansible labs", "CI/CD and configuration automation", "Hands-on lab", ["Jenkinsfile pipelines with GitHub webhooks for builds, tests and", "Docker image publishing, plus Ansible playbooks for Linux,", "Docker, Nginx and application deployment."], ["jenkins", "ansible", "docker", "nginx"], ["Jenkins", "Ansible", "Docker", "Nginx"], motif_labs, "dark", [SLATE_D, "#5E7A8E", "#6F9391"]),
 ("aws-labs", "AWS infrastructure labs", "Cloud fundamentals, hands-on", "Hands-on lab", ["EC2 with Linux SSH access, IAM users, roles and policies, S3 and", "security groups; apps deployed to EC2 with CloudWatch logs,", "metrics and alarms explored."], ["aws", "linux"], ["AWS", "Linux"], motif_aws, "light", ["#A6A0C2", "#93A9B3", "#86A69F"]),
 ("all-repos", "40 public repositories", "Everything else lives on GitHub", "Open archive", ["Smaller experiments and learning repositories.", "Browse the full list and judge the code directly."], ["github"], ["GitHub"], motif_all, "dark", ["#5D6F86", "#6E7F9D", "#7F82A6"]),
]
def build_cards():
    W, H = 500, 340
    for slug, name, sub, tag, lines, ics, labs, motif, mode, cols in CARDS:
        fg = PEARL2 if mode == "dark" else CHAR
        b = bg(W, H, [(0, cols[0]), (.55, cols[1]), (1, cols[2])], [(430, 40, 120, PEARL, .22 if mode == "light" else .14), (60, 330, 120, cols[2], .5)], rx=20)
        b += f'<g transform="translate(0,12)" color="{fg}">{motif(fg)}</g>'
        b += f'<path d="M24 168H476" stroke="{fg}" stroke-opacity=".28"/>'
        tw = len(tag) * 6.9 + 22
        b += (f'<rect x="{476-tw:.0f}" y="182" width="{tw:.0f}" height="22" rx="11" fill="{fg}" fill-opacity=".12" stroke="{fg}" stroke-opacity=".45"/>'
              f'<text x="{476-tw/2:.0f}" y="197" font-size="11.5" font-weight="700" fill="{fg}" text-anchor="middle">{tag}</text>'
              f'<text x="24" y="200" font-size="25" font-weight="800" fill="{fg}">{esc(name)}</text>'
              f'<text x="24" y="223" font-size="14" font-weight="600" fill="{fg}" fill-opacity=".92">{esc(sub)}</text>')
        for i, ln in enumerate(lines):
            b += f'<text x="24" y="{252+i*19}" font-size="13" font-weight="500" fill="{fg}">{esc(ln)}</text>'
        x = 24
        for ic, lab in zip(ics, labs):
            b += icon(ic, x, 303, 20, fg) + f'<text x="{x+26}" y="318" font-size="12" font-weight="700" fill="{fg}">{esc(lab)}</text>'
            x += 26 + len(lab) * 7 + 18
        write(f"{PRJ}/{slug}.svg", svg(W, H, b + endbg(), f"{name}: {sub}", " ".join(lines)))

def build_showcase():
    W, H = 1000, 190
    b = bg(W, H, [(0, "#52657B"), (.55, "#6F869D"), (1, "#8A8DB0")], [(880, 40, 160, SAGE, .5), (60, 180, 140, LAV, .35)], rx=22)
    b += (f'<text x="40" y="76" font-size="34" font-weight="800" fill="{PEARL2}">Selected work</text>'
          f'<text x="40" y="108" font-size="15.5" font-weight="500" fill="{PEARL2}">Public repositories and hands-on labs. Click any panel to open the source.</text>'
          f'<text x="40" y="136" font-size="13.5" font-weight="600" fill="{PEARL2}" fill-opacity=".92">Employer and client source code is private, so it is described in Experience rather than linked here.</text>')
    b += f'<g fill="none" stroke="{PEARL2}" stroke-opacity=".4">' + "".join(f'<circle cx="900" cy="95" r="{r}"/>' for r in (30, 60, 90)) + f'</g><path class="flow" d="M780 150Q840 60 900 95T1000 40" stroke="{PEARL2}" fill="none" stroke-width="1.6"/><circle cx="900" cy="95" r="6" fill="{PEARL2}"/>'
    write(f"{OUT}/project-showcase.svg", svg(W, H, b + endbg(), "Selected work", "Header for the projects section"))

# ---------- CONTACT + BUTTONS ----------
def build_contact():
    W, H = 1000, 330
    b = bg(W, H, [(0, "#52657B"), (.5, "#6B8299"), (.85, "#8A8DB0"), (1, "#9A95BA")], [(850, 300, 220, LAV, .5), (700, 30, 160, SAGE, .5)], rx=22)
    b += f'<g fill="none" stroke="{PEARL2}" stroke-opacity=".3">' + "".join(f'<circle cx="840" cy="165" r="{r}"/>' for r in (50, 100, 150)) + '</g>'
    b += f'<path class="flow" d="M840 165L700 70M840 165L960 60M840 165L930 280M840 165L690 270" stroke="{PEARL2}" stroke-opacity=".7" fill="none"/>'
    for x, y in ((700, 70), (960, 60), (930, 280), (690, 270)): b += f'<circle class="pulse" cx="{x}" cy="{y}" r="8" fill="{PEARL2}" opacity=".4"/><circle cx="{x}" cy="{y}" r="4.5" fill="{PEARL2}"/>'
    b += f'<circle cx="840" cy="165" r="36" fill="{SLATE_D}" stroke="{PEARL2}" stroke-opacity=".7"/>' + monogram(820, 145, 40, PEARL2, 15)
    b += (f'<text x="44" y="112" font-size="40" font-weight="800" fill="{PEARL2}">Great software deserves</text>'
          f'<text x="44" y="160" font-size="40" font-weight="800" fill="{PEARL2}">thoughtful engineering.</text>'
          f'<text x="46" y="212" font-size="22" font-weight="500" font-style="italic" fill="{PEARL2}">Let’s build something meaningful.</text>'
          f'<text x="46" y="272" font-size="14.5" font-weight="600" fill="{PEARL2}">khushalsehrawat2003@gmail.com  ·  New Delhi, India</text>')
    write(f"{OUT}/contact.svg", svg(W, H, b + endbg(), "Great software deserves thoughtful engineering. Let's build something meaningful."))
BUTTONS = [("hire", "Hire me for a role", True), ("freelance", "Start a freelance project", False), ("studio", "Visit TheBenzzCreations", False),
           ("linkedin", "LinkedIn", False), ("repos", "GitHub repositories", False), ("email", "Send an email", False)]
def build_buttons():
    for slug, label, primary in BUTTONS:
        w = int(len(label) * 8.6 + 48); h = 48
        fill = CHAR if primary else "url(#b)"; fg = PEARL2 if primary else CHAR
        b = (f'<defs><linearGradient id="b" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#C9C3D9"/><stop offset=".5" stop-color="#B9CCC6"/><stop offset="1" stop-color="#A9B9C9"/></linearGradient></defs>'
             f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="{h/2-1}" fill="{fill}" stroke="{CHAR}" stroke-opacity=".35"/>'
             f'<text x="{w/2}" y="{h/2+5.5}" font-size="15" font-weight="700" fill="{fg}" text-anchor="middle">{esc(label)}</text>')
        write(f"{BTN}/{slug}.svg", svg(w, h, b, label))

if __name__ == "__main__":
    for f in (build_monogram, build_hero, build_skills, build_experience, build_benzz, build_cards, build_showcase, build_contact, build_buttons): f()
    print("assets written to", OUT)
