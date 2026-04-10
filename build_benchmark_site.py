import json, os, sys

with open('/tmp/genesis/code_model_benchmarks.json') as f:
    data = json.load(f)

models = data['models']
meta = data['metadata']

def sort_key(m):
    lcb = m['benchmarks'].get('LiveCodeBench') or 0
    swe = m['benchmarks'].get('SWE_bench_verified') or 0
    he = m['benchmarks'].get('HumanEval') or 0
    return (lcb, swe, he)

models_sorted = sorted(models, key=sort_key, reverse=True)

def fmt(val, suffix=''):
    if val is None:
        return '<span class="na">—</span>'
    return f'<span class="score">{val}{suffix}</span>'

def tier(m):
    lcb = m['benchmarks'].get('LiveCodeBench') or 0
    swe = m['benchmarks'].get('SWE_bench_verified') or 0
    if lcb >= 70 or swe >= 70:
        return 'tier-s'
    elif lcb >= 40 or swe >= 60:
        return 'tier-a'
    elif lcb >= 20 or (m['benchmarks'].get('HumanEval') or 0) >= 80:
        return 'tier-b'
    else:
        return 'tier-c'

def tier_label(m):
    t = tier(m)
    labels = {'tier-s': 'S', 'tier-a': 'A', 'tier-b': 'B', 'tier-c': 'C'}
    return labels[t]

rows = ''
for i, m in enumerate(models_sorted, 1):
    b = m['benchmarks']
    t = tier(m)
    rows += f'''
    <tr class="{t}">
      <td class="rank">#{i}</td>
      <td class="model-name">
        <strong>{m['name']}</strong>
        <span class="provider">{m['provider']}</span>
      </td>
      <td class="params">{m['params_total']}</td>
      <td>{fmt(b.get('LiveCodeBench'))}</td>
      <td>{fmt(b.get('SWE_bench_verified'))}</td>
      <td>{fmt(b.get('HumanEval'))}</td>
      <td>{fmt(b.get('HumanEval_plus'))}</td>
      <td>{fmt(b.get('MBPP'))}</td>
      <td class="tier-cell"><span class="tier-badge {t}">{tier_label(m)}</span></td>
    </tr>'''

# Stats for hero section
total = len(models)
with_lcb = sum(1 for m in models if m['benchmarks'].get('LiveCodeBench'))
with_swe = sum(1 for m in models if m['benchmarks'].get('SWE_bench_verified'))
top_model = models_sorted[0]
top_swe = next((m for m in models_sorted if m['benchmarks'].get('SWE_bench_verified')), None)

html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI Benchmark Snapshot — Open-Source LLM Code Performance, April 2026</title>
  <meta name="description" content="Live benchmark comparison of 44 open-source code LLMs: HumanEval, LiveCodeBench, SWE-bench scores. Updated April 2026.">
  <meta property="og:title" content="AI Benchmark Snapshot — Open LLM Code Rankings">
  <meta property="og:description" content="Compare 44 open-source code models across HumanEval, LiveCodeBench, SWE-bench. April 2026.">
  <style>
    :root {{
      --bg: #0a0a0f;
      --surface: #12121a;
      --surface2: #1a1a26;
      --border: #2a2a3d;
      --accent: #7c6aff;
      --accent2: #00d4aa;
      --text: #e8e8f0;
      --muted: #6b6b8a;
      --s-color: #ffd700;
      --a-color: #7c6aff;
      --b-color: #00d4aa;
      --c-color: #4a4a6a;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Inter', -apple-system, system-ui, sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      line-height: 1.6;
    }}
    /* NAV */
    nav {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 1rem 2rem;
      border-bottom: 1px solid var(--border);
      background: var(--surface);
      position: sticky;
      top: 0;
      z-index: 100;
      backdrop-filter: blur(10px);
    }}
    .nav-brand {{ font-weight: 700; font-size: 1.1rem; color: var(--accent); letter-spacing: -0.02em; }}
    .nav-brand span {{ color: var(--text); }}
    .nav-date {{ font-size: 0.8rem; color: var(--muted); }}
    /* HERO */
    .hero {{
      padding: 4rem 2rem 3rem;
      max-width: 1200px;
      margin: 0 auto;
    }}
    .hero-tag {{
      display: inline-block;
      background: rgba(124,106,255,0.15);
      color: var(--accent);
      padding: 0.25rem 0.75rem;
      border-radius: 100px;
      font-size: 0.75rem;
      font-weight: 600;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      margin-bottom: 1.5rem;
      border: 1px solid rgba(124,106,255,0.3);
    }}
    h1 {{
      font-size: clamp(2rem, 5vw, 3.5rem);
      font-weight: 800;
      letter-spacing: -0.04em;
      line-height: 1.1;
      margin-bottom: 1rem;
    }}
    h1 em {{ font-style: normal; color: var(--accent); }}
    .hero-sub {{
      font-size: 1.15rem;
      color: var(--muted);
      max-width: 680px;
      margin-bottom: 2.5rem;
    }}
    /* STATS */
    .stats-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 1rem;
      margin-bottom: 3rem;
    }}
    .stat-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 1.5rem;
    }}
    .stat-num {{
      font-size: 2.5rem;
      font-weight: 800;
      letter-spacing: -0.04em;
      color: var(--accent2);
      line-height: 1;
      margin-bottom: 0.25rem;
    }}
    .stat-label {{ font-size: 0.8rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em; }}
    /* NARRATIVE */
    .narrative {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-left: 3px solid var(--accent);
      border-radius: 12px;
      padding: 2rem;
      margin-bottom: 3rem;
      max-width: 900px;
    }}
    .narrative h2 {{ font-size: 1.1rem; font-weight: 700; margin-bottom: 1rem; color: var(--accent); }}
    .narrative p {{ color: #c0c0d8; line-height: 1.75; margin-bottom: 0.75rem; }}
    .narrative p:last-child {{ margin-bottom: 0; }}
    /* TABLE SECTION */
    .table-section {{ max-width: 1200px; margin: 0 auto; padding: 0 2rem 2rem; }}
    .table-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 1.5rem;
      flex-wrap: wrap;
      gap: 1rem;
    }}
    .table-header h2 {{ font-size: 1.4rem; font-weight: 700; letter-spacing: -0.02em; }}
    .legend {{ display: flex; gap: 0.75rem; flex-wrap: wrap; }}
    .legend-item {{
      display: flex;
      align-items: center;
      gap: 0.4rem;
      font-size: 0.75rem;
      color: var(--muted);
    }}
    .legend-dot {{
      width: 8px; height: 8px; border-radius: 2px;
    }}
    .dot-s {{ background: var(--s-color); }}
    .dot-a {{ background: var(--a-color); }}
    .dot-b {{ background: var(--b-color); }}
    .dot-c {{ background: var(--c-color); }}
    /* TABLE */
    .table-wrap {{
      overflow-x: auto;
      border: 1px solid var(--border);
      border-radius: 12px;
      background: var(--surface);
    }}
    table {{ width: 100%; border-collapse: collapse; font-size: 0.875rem; }}
    thead th {{
      padding: 0.875rem 1rem;
      text-align: left;
      font-size: 0.7rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--muted);
      border-bottom: 1px solid var(--border);
      white-space: nowrap;
      background: var(--surface2);
    }}
    tbody tr {{
      border-bottom: 1px solid rgba(42,42,61,0.5);
      transition: background 0.15s;
    }}
    tbody tr:hover {{ background: rgba(124,106,255,0.05); }}
    tbody tr:last-child {{ border-bottom: none; }}
    tbody td {{ padding: 0.875rem 1rem; vertical-align: middle; }}
    .rank {{ color: var(--muted); font-weight: 700; font-size: 0.8rem; white-space: nowrap; }}
    .model-name {{ min-width: 220px; }}
    .model-name strong {{ display: block; font-weight: 600; color: var(--text); }}
    .model-name .provider {{ font-size: 0.75rem; color: var(--muted); }}
    .params {{ color: var(--muted); font-size: 0.8rem; white-space: nowrap; }}
    .score {{ font-weight: 700; color: var(--text); }}
    .na {{ color: var(--border); }}
    .tier-cell {{ text-align: center; }}
    .tier-badge {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 28px; height: 28px;
      border-radius: 6px;
      font-size: 0.75rem;
      font-weight: 800;
    }}
    .tier-s .tier-badge, .tier-badge.tier-s {{ background: rgba(255,215,0,0.15); color: var(--s-color); border: 1px solid rgba(255,215,0,0.3); }}
    .tier-a .tier-badge, .tier-badge.tier-a {{ background: rgba(124,106,255,0.15); color: var(--accent); border: 1px solid rgba(124,106,255,0.3); }}
    .tier-b .tier-badge, .tier-badge.tier-b {{ background: rgba(0,212,170,0.15); color: var(--accent2); border: 1px solid rgba(0,212,170,0.3); }}
    .tier-c .tier-badge, .tier-badge.tier-c {{ background: rgba(74,74,106,0.15); color: var(--muted); border: 1px solid rgba(74,74,106,0.3); }}
    /* Row tier accent */
    .tier-s td:first-child {{ border-left: 2px solid var(--s-color); }}
    .tier-a td:first-child {{ border-left: 2px solid var(--accent); }}
    .tier-b td:first-child {{ border-left: 2px solid var(--accent2); }}
    /* CTA */
    .cta-section {{
      max-width: 1200px;
      margin: 3rem auto;
      padding: 0 2rem;
    }}
    .cta-card {{
      background: linear-gradient(135deg, rgba(124,106,255,0.12), rgba(0,212,170,0.08));
      border: 1px solid rgba(124,106,255,0.3);
      border-radius: 16px;
      padding: 2.5rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 2rem;
      flex-wrap: wrap;
    }}
    .cta-text h3 {{ font-size: 1.4rem; font-weight: 700; margin-bottom: 0.5rem; letter-spacing: -0.02em; }}
    .cta-text p {{ color: var(--muted); font-size: 0.95rem; max-width: 500px; }}
    .cta-text ul {{ color: var(--muted); font-size: 0.9rem; margin-top: 0.75rem; padding-left: 1.25rem; }}
    .cta-text ul li {{ margin-bottom: 0.25rem; }}
    .cta-btn {{
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      background: var(--accent);
      color: #fff;
      padding: 0.875rem 2rem;
      border-radius: 10px;
      font-weight: 700;
      font-size: 1rem;
      text-decoration: none;
      white-space: nowrap;
      transition: all 0.2s;
      box-shadow: 0 4px 24px rgba(124,106,255,0.35);
    }}
    .cta-btn:hover {{ background: #6b5ce7; transform: translateY(-1px); box-shadow: 0 6px 32px rgba(124,106,255,0.5); }}
    .cta-price {{ font-size: 0.8rem; color: rgba(255,255,255,0.7); margin-top: 0.4rem; text-align: center; }}
    /* FOOTER */
    footer {{
      max-width: 1200px;
      margin: 0 auto;
      padding: 2rem;
      border-top: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 1rem;
      color: var(--muted);
      font-size: 0.8rem;
    }}
    .footer-sources {{ max-width: 600px; }}
    @media (max-width: 768px) {{
      .hero {{ padding: 2rem 1rem 1.5rem; }}
      .table-section {{ padding: 0 1rem 2rem; }}
      .cta-section {{ padding: 0 1rem; }}
      footer {{ padding: 1.5rem 1rem; }}
    }}
  </style>
</head>
<body>
<nav>
  <div class="nav-brand">AI<span>Benchmark</span></div>
  <div class="nav-date">Compiled {meta['compiled']} · {total} models</div>
</nav>

<div class="hero">
  <div style="max-width:1200px;margin:0 auto">
    <div class="hero-tag">April 2026 Snapshot</div>
    <h1>Open-Source LLM<br><em>Code Performance</em> Rankings</h1>
    <p class="hero-sub">
      Aggregated benchmark scores for {total} open-weight code models — HumanEval, LiveCodeBench, and SWE-bench Verified — compiled from original papers and third-party evaluations.
    </p>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-num">{total}</div>
        <div class="stat-label">Models Tracked</div>
      </div>
      <div class="stat-card">
        <div class="stat-num">{with_lcb}</div>
        <div class="stat-label">With LiveCodeBench</div>
      </div>
      <div class="stat-card">
        <div class="stat-num">{with_swe}</div>
        <div class="stat-label">With SWE-bench Scores</div>
      </div>
      <div class="stat-card">
        <div class="stat-num">{top_model['benchmarks'].get('LiveCodeBench', '—')}</div>
        <div class="stat-label">Best LiveCodeBench</div>
      </div>
      <div class="stat-card">
        <div class="stat-num">{top_swe['benchmarks'].get('SWE_bench_verified') if top_swe else '—'}</div>
        <div class="stat-label">Best SWE-bench</div>
      </div>
    </div>

    <div class="narrative">
      <h2>Key Findings — April 2026</h2>
      <p>
        <strong>The frontier has bifurcated.</strong> A small cluster of MoE-architecture models — Kimi K2.5, Qwen3-Coder-480B, and Devstral 2 — now dominate real-world agent tasks (SWE-bench Verified), while dense models max out the saturated HumanEval benchmark. HumanEval scores above 90% no longer differentiate models meaningfully.
      </p>
      <p>
        <strong>LiveCodeBench is the new standard.</strong> Only {with_lcb} of {total} models report LiveCodeBench scores, but it is now the primary discriminator for frontier models. The gap between Kimi K2.5 (85.0 LCB) and the next open-weight model reveals how quickly the ceiling is rising.
      </p>
      <p>
        <strong>SWE-bench Verified separates agents from assistants.</strong> With only {with_swe} models reporting scores, SWE-bench data is sparse but decisive: it measures whether a model can autonomously resolve real GitHub issues, not just complete synthetic problems. Scores above 65% represent a qualitative capability threshold.
      </p>
      <p>
        <strong>Efficient models punch above their weight.</strong> GLM-4.7 at 9B parameters achieves 94.2 HumanEval and 84.9 LiveCodeBench — rivaling models 50× larger — demonstrating that parameter count is increasingly a poor proxy for coding capability.
      </p>
    </div>
  </div>
</div>

<div class="table-section">
  <div class="table-header">
    <h2>Full Leaderboard</h2>
    <div class="legend">
      <span class="legend-item"><span class="legend-dot dot-s"></span> S-Tier (LCB≥70 or SWE≥70)</span>
      <span class="legend-item"><span class="legend-dot dot-a"></span> A-Tier (LCB≥40 or SWE≥60)</span>
      <span class="legend-item"><span class="legend-dot dot-b"></span> B-Tier (LCB≥20 or HE≥80)</span>
      <span class="legend-item"><span class="legend-dot dot-c"></span> C-Tier</span>
    </div>
  </div>

  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>#</th>
          <th>Model</th>
          <th>Params</th>
          <th>LiveCodeBench ↑</th>
          <th>SWE-bench ↑</th>
          <th>HumanEval ↑</th>
          <th>HumanEval+ ↑</th>
          <th>MBPP ↑</th>
          <th>Tier</th>
        </tr>
      </thead>
      <tbody>
        {rows}
      </tbody>
    </table>
  </div>
</div>

<div class="cta-section">
  <div class="cta-card">
    <div class="cta-text">
      <h3>Full Dataset Export</h3>
      <p>Download the complete structured dataset powering this leaderboard:</p>
      <ul>
        <li>All 44 models · 7 benchmark dimensions · raw scores + metadata</li>
        <li>JSON + CSV formats · source references for every data point</li>
        <li>Architecture details, license, context window, release dates</li>
        <li>One-time purchase — no subscription</li>
      </ul>
    </div>
    <div>
      <a href="https://buy.stripe.com/9B628n1Yl1UM0PC5kk" class="cta-btn">
        ⬇ Download Dataset — €5
      </a>
      <div class="cta-price">One-time · Instant delivery</div>
    </div>
  </div>
</div>

<footer>
  <div class="footer-sources">
    <strong>Sources:</strong> EvalPlus Leaderboard · LiveCodeBench · BigCode Models Leaderboard · Original model technical reports (Qwen2.5-Coder, DeepSeek-Coder-V2, StarCoder2, Granite Code, CodeGemma). Compiled {meta['compiled']}.
  </div>
  <div>Built by <a href="https://github.com/ark-forge" style="color:var(--accent);text-decoration:none">ArkForge</a></div>
</footer>

</body>
</html>'''

outpath = '/tmp/genesis/docs/benchmark.html'
os.makedirs('/tmp/genesis/docs', exist_ok=True)
with open(outpath, 'w') as f:
    f.write(html)

print(f'Written: {outpath} ({len(html):,} bytes)')
