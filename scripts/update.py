import json
import csv
from datetime import datetime

def parse_moeda(val):
    if not val: return 0
    try:
        val = str(val).replace("R$","").replace(".","").replace(",",".").strip()
        return float(val) if val else 0
    except: return 0

# Process CSV
with open("data/emendas.csv","r",encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

emendas = []
for row in rows:
    if not row.get("Parlamentar/Proponente"): continue
    vp = parse_moeda(row.get("Valor Pago"))
    ve = parse_moeda(row.get("Valor Empenhado"))
    perc = (vp/ve*100) if ve>0 else 0
    emendas.append({
        "parlamentar": row.get("Parlamentar/Proponente","").strip(),
        "ano": int(row.get("Ano","2025")) if row.get("Ano") else 2025,
        "processo": row.get("Processo","").strip(),
        "proposta": row.get("Proposta","").strip(),
        "projeto": row.get("Objeto","").strip(),
        "localExecucao": row.get("Local de Execução","").strip(),
        "tipoExecucao": row.get("Forma de Execução","").strip(),
        "valor": parse_moeda(row.get("Valor da Emenda")),
        "valorEmpenhado": ve,
        "valorPago": vp,
        "percentualPago": round(perc,2),
        "situacao": row.get("Situação","").strip(),
        "observacao": row.get("Observação","").strip()
    })

tot_emp = sum(e["valorEmpenhado"] for e in emendas)
tot_pag = sum(e["valorPago"] for e in emendas)
perc = (tot_pag/tot_emp*100) if tot_emp>0 else 0

print(f"Registros: {len(emendas)}")
print(f"Empenhado: R$ {tot_emp:,.2f}")
print(f"Pago: R$ {tot_pag:,.2f}")
print(f"Percentual: {perc:.2f}%")

with open("data/emendas.json","w",encoding="utf-8") as f:
    json.dump(emendas, f, ensure_ascii=False, indent=2)

# Generate HTML
data_hora = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
emendas_json = json.dumps(emendas, ensure_ascii=False, separators=(",",":"))

html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Dashboard Emendas Federais</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:Arial,sans-serif;background:linear-gradient(135deg,#2c3e50,#3498db);min-height:100vh;padding:20px}}
.container{{max-width:1600px;margin:0 auto}}
header{{background:white;padding:30px;border-radius:10px;margin-bottom:30px;box-shadow:0 4px 6px rgba(0,0,0,0.1)}}
h1{{color:#2c3e50;margin-bottom:10px;font-size:2em}}
.subtitle{{color:#666}}
.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:15px;margin:20px 0}}
.stat-card{{background:white;padding:15px;border-radius:10px;box-shadow:0 4px 6px rgba(0,0,0,0.1);text-align:center}}
.stat-value{{font-size:1.5em;color:#3498db;font-weight:bold;margin:10px 0}}
.stat-label{{color:#666;font-size:0.9em}}
.table-container{{background:white;padding:20px;border-radius:10px;box-shadow:0 4px 6px rgba(0,0,0,0.1);margin:20px 0;overflow-x:auto}}
table{{width:100%;border-collapse:collapse;font-size:0.9em}}
th{{background:#3498db;color:white;padding:12px;text-align:left;font-weight:600}}
td{{padding:12px;border-bottom:1px solid #eee}}
tr:hover{{background:#f5f5f5}}
.footer{{text-align:center;padding:15px;background:#f0f0f0;border-top:1px solid #ddd;margin-top:20px;font-size:0.9em;color:#666}}
</style></head><body>
<div class="container">
<header>
<h1>📊 Dashboard Emendas Federais e Estaduais</h1>
<p class="subtitle">Teresina/PI — 2025 e 2026</p>
</header>

<div id="stats" class="stats"></div>

<div class="table-container">
<h3 style="margin-bottom:15px;color:#333">Listagem de Emendas</h3>
<table>
<thead><tr><th>Parlamentar</th><th>Ano</th><th>Processo</th><th>Proposta</th><th>Objeto</th><th>Local de Execução</th><th>Empenhado</th><th>Pago</th><th>%</th><th>Situação</th></tr></thead>
<tbody id="tableBody"></tbody>
</table>
</div>

<div class="footer">Última atualização: <strong>{data_hora}</strong></div>
</div>

<script>
const emendas = {emendas_json};

function formatMoeda(v){{
  return new Intl.NumberFormat("pt-BR",{{style:"currency",currency:"BRL"}}).format(v);
}}

function renderTable(){{
  let html = "";
  emendas.forEach(e=>{{
    html += `<tr><td>${{e.parlamentar}}</td><td>${{e.ano}}</td><td>${{e.processo}}</td><td>${{e.proposta}}</td><td>${{e.projeto}}</td><td>${{e.localExecucao}}</td><td>${{formatMoeda(e.valorEmpenhado)}}</td><td>${{formatMoeda(e.valorPago)}}</td><td>${{e.percentualPago}}%</td><td>${{e.situacao}}</td></tr>`;
  }});
  document.getElementById("tableBody").innerHTML = html;
}}

function updateStats(){{
  let tot_emp = emendas.reduce((s,e)=>s+e.valorEmpenhado,0);
  let tot_pag = emendas.reduce((s,e)=>s+e.valorPago,0);
  let perc = (tot_emp>0 ? tot_pag/tot_emp*100 : 0).toFixed(2);
  
  document.getElementById("stats").innerHTML = `
    <div class="stat-card">
      <div class="stat-value">${{emendas.length}}</div>
      <div class="stat-label">Total de Emendas</div>
    </div>
    <div class="stat-card">
      <div class="stat-value">${{formatMoeda(tot_emp)}}</div>
      <div class="stat-label">Empenhado</div>
    </div>
    <div class="stat-card">
      <div class="stat-value">${{formatMoeda(tot_pag)}}</div>
      <div class="stat-label">Pago</div>
    </div>
    <div class="stat-card">
      <div class="stat-value">${{perc}}%</div>
      <div class="stat-label">Percentual</div>
    </div>
  `;
}}

window.addEventListener("DOMContentLoaded", ()=>{{
  renderTable();
  updateStats();
}});
</script>
</body></html>"""

with open("index.html","w",encoding="utf-8") as f:
    f.write(html)

print("HTML gerado com sucesso")
