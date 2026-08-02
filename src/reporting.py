from __future__ import annotations
from datetime import date
import html
import pandas as pd

LABELS={
"population_2021":"Population (2021)","growth_2010_2021_percent":"Population growth, 2010–2021",
"density_2021":"Population density","urban_share_percent":"Urban population share","literacy_percent":"Literacy",
"school_attendance_percent":"School attendance","employed_share_percent":"Employed share","unemployment_rate_percent":"Unemployment",
"improved_water_percent":"Improved water","basic_sanitation_percent":"Basic sanitation","electricity_access_percent":"Electricity access",
"internet_use_percent":"Internet use","health_insurance_percent":"Health insurance","multidimensional_poverty_percent":"Multidimensional poverty"
}

def regional_report_html(row: pd.Series, score_row: pd.Series|None=None, source_label=""):
    r={k:row.get(k) for k in row.index}
    score="Not calculated" if score_row is None else f"{score_row.get('development_score',float('nan')):.1f}/100 (rank {int(score_row.get('rank'))})"
    metrics=[]
    for key in LABELS:
        if key in row and pd.notna(row[key]):
            val=row[key]
            if key=="population_2021": text=f"{int(val):,}"
            elif key=="density_2021": text=f"{val:,.1f} persons/km²"
            else:text=f"{val:.1f}%"
            metrics.append(f"<tr><td>{html.escape(LABELS[key])}</td><td>{text}</td></tr>")
    return f'''<!doctype html><html><head><meta charset="utf-8"><title>{html.escape(str(r['region']))} regional profile</title>
<style>body{{font-family:Arial,sans-serif;max-width:900px;margin:40px auto;color:#17231c}}h1{{color:#0b6b50}}.hero{{background:#edf8f2;padding:28px;border-radius:20px}}table{{border-collapse:collapse;width:100%;margin-top:20px}}td{{padding:10px;border-bottom:1px solid #ddd}}td:last-child{{font-weight:700;text-align:right}}.note{{margin-top:24px;padding:14px;background:#fff7df;border-left:4px solid #d59b1e}}</style></head>
<body><div class="hero"><small>GHANA REGIONAL DEVELOPMENT & CENSUS EXPLORER</small><h1>{html.escape(str(r['region']))}</h1><p>Capital: {html.escape(str(r.get('capital','')))} · Development index: {score}</p></div>
<table>{''.join(metrics)}</table><div class="note"><b>Interpretation:</b> The composite score is a comparative analytical tool, not an official government ranking. Population fields reproduce the 2021 PHC baseline; bundled development indicators are calibrated demonstration values unless replaced by an official upload.</div>
<p><small>Generated {date.today().isoformat()} · Source label: {html.escape(source_label)}</small></p></body></html>'''
