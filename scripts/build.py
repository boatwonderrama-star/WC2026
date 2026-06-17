#!/usr/bin/env python3
"""
ดึงผลบอลโลก 2026 จาก openfootball/worldcup.json (public domain, ไม่ต้องใช้ API key)
คำนวณตารางคะแนนของ 7 ทีมที่เลือก แล้ว generate ไฟล์ docs/index.html
รันโดย GitHub Actions ทุกวัน
"""
import json
import urllib.request
from datetime import datetime, timezone, timedelta

SOURCE_URL = "https://raw.githubusercontent.com/openfootball/worldcup.json/master/2026/worldcup.json"

# 7 ทีมที่เลือก: (ชื่อใน source data, ชื่อไทย, ธง)
TEAMS = [
    ("France",       "ฝรั่งเศส",      "🇫🇷"),
    ("Germany",      "เยอรมัน",       "🇩🇪"),
    ("Japan",        "ญี่ปุ่น",        "🇯🇵"),
    ("Spain",        "สเปน",          "🇪🇸"),
    ("Argentina",    "อาร์เจนติน่า",   "🇦🇷"),
    ("Netherlands",  "เนเธอร์แลนด์",   "🇳🇱"),
    ("Portugal",     "โปรตุเกส",       "🇵🇹"),
]
TEAM_NAMES = {t[0] for t in TEAMS}
TH_NAME = {t[0]: t[1] for t in TEAMS}
FLAG = {t[0]: t[2] for t in TEAMS}


def fetch_data():
    req = urllib.request.Request(SOURCE_URL, headers={"User-Agent": "wc2026-tracker"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def compute_standings(matches):
    stats = {
        name: {"group": None, "played": 0, "won": 0, "drawn": 0, "lost": 0, "gf": 0, "ga": 0, "points": 0}
        for name in TEAM_NAMES
    }
    recent = []

    for m in matches:
        t1, t2 = m.get("team1"), m.get("team2")
        score = m.get("score")
        if not score or "ft" not in score:
            continue  # ยังไม่แข่ง
        s1, s2 = score["ft"]
        group = m.get("group", "").replace("Group ", "")

        for team, opp, gf, ga in ((t1, t2, s1, s2), (t2, t1, s2, s1)):
            if team in stats:
                st = stats[team]
                st["group"] = group
                st["played"] += 1
                st["gf"] += gf
                st["ga"] += ga
                if gf > ga:
                    st["won"] += 1
                    st["points"] += 3
                elif gf == ga:
                    st["drawn"] += 1
                    st["points"] += 1
                else:
                    st["lost"] += 1

        if t1 in TEAM_NAMES or t2 in TEAM_NAMES:
            recent.append({
                "team1": t1, "team2": t2,
                "score1": s1, "score2": s2,
                "date": m.get("date", ""),
                "group": group,
                "ground": m.get("ground", ""),
            })

    recent.sort(key=lambda x: x["date"], reverse=True)

    standings = []
    for name in TEAM_NAMES:
        st = stats[name]
        standings.append({"team": name, **st})
    standings.sort(key=lambda t: (-t["points"], -(t["gf"] - t["ga"]), -t["gf"]))

    return standings, recent[:10]


def render_html(standings, recent_matches, updated_at):
    rows = ""
    for i, t in enumerate(standings, start=1):
        gd = t["gf"] - t["ga"]
        gd_class = "gd-pos" if gd > 0 else ("gd-neg" if gd < 0 else "gd-neu")
        gd_text = (f"+{gd}" if gd > 0 else str(gd)) if t["played"] > 0 else "—"
        group_text = t["group"] or "-"
        rows += f"""
        <tr class="team-row">
          <td class="rank">{i}</td>
          <td class="left"><div class="team-cell"><span class="flag">{FLAG[t['team']]}</span><span class="tname">{TH_NAME[t['team']]}</span></div></td>
          <td><span class="group-pill">{group_text}</span></td>
          <td>{t['played']}</td><td>{t['won']}</td><td>{t['drawn']}</td><td>{t['lost']}</td>
          <td class="{gd_class}">{gd_text}</td>
          <td class="pts">{t['points']}</td>
        </tr>"""

    if not rows:
        rows = '<tr><td colspan="9" class="empty-state">ยังไม่มีทีมที่เลือกลงเล่น</td></tr>'

    match_cards = ""
    for m in recent_matches:
        f1 = FLAG.get(m["team1"], "")
        f2 = FLAG.get(m["team2"], "")
        n1 = TH_NAME.get(m["team1"], m["team1"])
        n2 = TH_NAME.get(m["team2"], m["team2"])
        match_cards += f"""
        <div class="match-card">
          <div class="match-row">
            <div class="match-team">{f1} <span>{n1}</span></div>
            <div class="score-box">{m['score1']} – {m['score2']}</div>
            <div class="match-team right">{n2} <span>{f2}</span></div>
          </div>
          <div class="match-meta">{m['date']} · Group {m['group']} · {m['ground']}</div>
        </div>"""

    if not match_cards:
        match_cards = '<div class="empty-state">ยังไม่มีนัดที่จบ</div>'

    html = f"""<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>World Cup 2026 - ตารางคะแนน 7 ทีมเลือก</title>
<style>
  :root {{
    --bg: #0f0f10; --card: #18181a; --card-hover: #1f1f22;
    --border: rgba(255,255,255,0.08); --text: #f2f2f0; --text-secondary: #9a9a96;
    --gold: #d4af37; --green: #5dcaa5; --red: #e08a7d;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans Thai", sans-serif; padding: 24px 16px 60px; min-height: 100vh; }}
  .wrap {{ max-width: 720px; margin: 0 auto; }}
  .header {{ display: flex; align-items: center; gap: 12px; margin-bottom: 6px; }}
  .trophy {{ font-size: 30px; }}
  h1 {{ font-size: 18px; font-weight: 600; color: var(--gold); letter-spacing: 0.3px; }}
  .sub {{ font-size: 12px; color: var(--text-secondary); margin-top: 4px; }}
  .status-bar {{ font-size: 12px; color: var(--text-secondary); margin: 14px 0 20px; padding-bottom: 16px; border-bottom: 1px solid var(--border); display: flex; align-items: center; gap: 8px; }}
  .status-dot {{ width: 7px; height: 7px; border-radius: 50%; background: var(--green); flex-shrink: 0; }}
  table {{ width: 100%; border-collapse: collapse; }}
  th {{ font-size: 11px; font-weight: 500; color: var(--text-secondary); text-align: center; padding: 8px 6px; border-bottom: 1px solid var(--border); text-transform: uppercase; letter-spacing: 0.04em; }}
  th.left {{ text-align: left; }}
  td {{ padding: 12px 6px; text-align: center; border-bottom: 1px solid var(--border); font-size: 14px; }}
  td.left {{ text-align: left; }}
  tr.team-row:hover td {{ background: var(--card-hover); }}
  .team-cell {{ display: flex; align-items: center; gap: 10px; }}
  .flag {{ font-size: 19px; }}
  .tname {{ font-weight: 500; }}
  .group-pill {{ font-size: 10px; background: var(--card); border: 1px solid var(--border); color: var(--text-secondary); padding: 2px 7px; border-radius: 999px; }}
  .pts {{ font-weight: 700; color: var(--gold); font-size: 15px; }}
  .gd-pos {{ color: var(--green); }}
  .gd-neg {{ color: var(--red); }}
  .gd-neu {{ color: var(--text-secondary); }}
  .rank {{ font-weight: 600; color: var(--text-secondary); width: 26px; }}
  .matches-section {{ margin-top: 32px; }}
  .section-title {{ font-size: 12px; font-weight: 600; color: var(--gold); text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 12px; }}
  .match-card {{ background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 14px 16px; margin-bottom: 8px; }}
  .match-row {{ display: flex; align-items: center; justify-content: space-between; gap: 10px; }}
  .match-team {{ display: flex; align-items: center; gap: 8px; font-size: 14px; font-weight: 500; flex: 1; min-width: 0; }}
  .match-team.right {{ flex-direction: row-reverse; text-align: right; }}
  .score-box {{ background: var(--bg); border: 1px solid var(--border); border-radius: 8px; padding: 5px 14px; font-size: 15px; font-weight: 600; color: var(--gold); min-width: 56px; text-align: center; flex-shrink: 0; }}
  .match-meta {{ font-size: 11px; color: var(--text-secondary); margin-top: 8px; text-align: center; }}
  .empty-state {{ text-align: center; padding: 40px 20px; color: var(--text-secondary); font-size: 13px; }}
  .footer-note {{ margin-top: 28px; font-size: 11px; color: var(--text-secondary); text-align: center; line-height: 1.6; }}
  .footer-note a {{ color: var(--gold); text-decoration: none; }}
</style>
</head>
<body>
<div class="wrap">
  <div class="header">
    <div class="trophy">🏆</div>
    <div>
      <h1>WORLD CUP 2026 — ตารางคะแนน</h1>
      <div class="sub">7 ทีมที่เลือก: ฝรั่งเศส เยอรมัน ญี่ปุ่น สเปน อาร์เจนติน่า เนเธอร์แลนด์ โปรตุเกส</div>
    </div>
  </div>

  <div class="status-bar">
    <span class="status-dot"></span>
    <span>อัปเดตล่าสุด: {updated_at} (เวลาไทย) · ข้อมูลอัปเดตอัตโนมัติทุกวันผ่าน GitHub Actions</span>
  </div>

  <table>
    <thead>
      <tr>
        <th class="left" style="width:26px;">#</th>
        <th class="left">ทีม</th>
        <th>กลุ่ม</th><th>แข่ง</th><th>ชนะ</th><th>เสมอ</th><th>แพ้</th><th>GD</th><th>คะแนน</th>
      </tr>
    </thead>
    <tbody>{rows}
    </tbody>
  </table>

  <div class="matches-section">
    <div class="section-title">ผลการแข่งขันล่าสุด</div>
    {match_cards}
  </div>

  <div class="footer-note">
    ข้อมูลจาก <a href="https://github.com/openfootball/worldcup.json" target="_blank">openfootball/worldcup.json</a> (public domain)<br>
    Build อัตโนมัติทุกวันผ่าน GitHub Actions · โฮสต์ฟรีบน GitHub Pages
  </div>
</div>
</body>
</html>
"""
    return html


def main():
    data = fetch_data()
    matches = data.get("matches", [])
    standings, recent = compute_standings(matches)
    now_thai = datetime.now(timezone.utc).astimezone(
        timezone(timedelta(hours=7))
    ).strftime("%d %b %Y, %H:%M")
    html = render_html(standings, recent, now_thai)

    with open("docs/index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Built docs/index.html — {len(standings)} teams, {len(recent)} recent matches")


if __name__ == "__main__":
    main()
