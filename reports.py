#!/usr/bin/env python3
import os
import shutil
from jinja2 import Template
import cantools

# ---------------- Config ----------------
DBC_DIR = "."       # Pasta com os DBCs atuais
OLD_DIR = "./old"   # Pasta para versões antigas
REPORT_DIR = "./reports"
os.makedirs(OLD_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

# ---------------- HTML Template ----------------
html_template = """
<!DOCTYPE html>
<html lang="pt">
<head>
<meta charset="UTF-8">
<title>Dashboard DBC Completo</title>
<style>
body { font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif; margin:20px; background:#f4f6f8; color:#333; }
h1 { color: #1f4e79; }
.tab { overflow:hidden; border-bottom:2px solid #ccc; background-color:#fff; margin-bottom:20px; }
.tab button { background-color:inherit; float:left; border:none; outline:none; cursor:pointer; padding:10px 20px; transition:0.3s; font-size:16px; }
.tab button:hover { background-color:#ddd; }
.tab button.active { background-color:#1f78b4; color:white; }
.tabcontent { display:none; padding:10px 0; border-top:none; }
table { width:100%; border-collapse: collapse; margin-bottom: 20px; background-color:#fff; box-shadow:0 2px 5px rgba(0,0,0,0.1);}
th, td { border:1px solid #ccc; padding:8px; text-align:left; }
th { background-color:#e2eaf1; }
.added { background-color:#d4ffd4; }
.removed { background-color:#ffd4d4; }
.changed { background-color:#fff0b3; }
.code { font-family: monospace; }
.collapsible { background-color:#1f78b4; color:white; cursor:pointer; padding:8px; border:none; text-align:left; outline:none; font-size:14px; margin-top:10px; border-radius:5px; }
.active_collapsible, .collapsible:hover { background-color:#145a86; }
.content { padding:0 15px; display:none; overflow:hidden; background-color:#f9f9f9; border-left:3px solid #1f78b4; margin-bottom:10px;}
.summary { margin-bottom:20px; padding:10px; background:#eaf1fb; border-left:5px solid #1f78b4;}
</style>
</head>
<body>
<h1>Dashboard DBC Completo</h1>

<h2>📁 Ficheiros DBC</h2>
<p>Adicionados: {{ added_files | join(', ') if added_files else 'Nenhum' }}</p>
<p>Removidos: {{ removed_files | join(', ') if removed_files else 'Nenhum' }}</p>

<div class="tab">
{% for dbc in dbcs %}
  <button class="tablinks" onclick="openTab(event, '{{ dbc.name }}')">{{ dbc.name }}</button>
{% endfor %}
</div>

{% for dbc in dbcs %}
<div id="{{ dbc.name }}" class="tabcontent">
  <div class="summary">
    <b>Resumo:</b> Nós: {{ dbc.nodes|length }}, Mensagens: {{ dbc.messages|length }}, Sinais: {{ dbc.signals|length }}
    <br>Mensagens Adicionadas: {{ dbc.msg_added|length }}, Removidas: {{ dbc.msg_removed|length }}, Alteradas: {{ dbc.msg_changed|length }}
    <br>Sinais Adicionados: {{ dbc.added | length }}, Removidos: {{ dbc.removed | length }}, Alterados: {{ dbc.changed | length }}
  </div>

  <h2>🟦 Nós</h2>
  <ul>
  {% for n in dbc.nodes %}
    <li>{{ n }}</li>
  {% endfor %}
  </ul>

  <h2>📨 Mensagens Adicionadas</h2>
  {% if dbc.msg_added %}
  <table>
  <tr><th>ID</th><th>Nome</th><th>DLC</th><th>Ciclo</th><th>Sinais</th></tr>
  {% for m in dbc.msg_added %}
    <tr class="added">
      <td>{{ m.frame_id }}</td>
      <td>{{ m.name }}</td>
      <td>{{ m.length }}</td>
      <td>{{ m.cycle_time }}</td>
      <td>{{ m.signals | join(', ') }}</td>
    </tr>
  {% endfor %}
  </table>
  {% else %}<p>Nenhuma mensagem adicionada.</p>{% endif %}

  <h2>📨 Mensagens Removidas</h2>
  {% if dbc.msg_removed %}
  <table>
  <tr><th>ID</th><th>Nome</th><th>DLC</th><th>Ciclo</th><th>Sinais</th></tr>
  {% for m in dbc.msg_removed %}
    <tr class="removed">
      <td>{{ m.frame_id }}</td>
      <td>{{ m.name }}</td>
      <td>{{ m.length }}</td>
      <td>{{ m.cycle_time }}</td>
      <td>{{ m.signals | join(', ') }}</td>
    </tr>
  {% endfor %}
  </table>
  {% else %}<p>Nenhuma mensagem removida.</p>{% endif %}

  <h2>📨 Mensagens Alteradas</h2>
  {% if dbc.msg_changed %}
    {% for m in dbc.msg_changed %}
    <button type="button" class="collapsible">{{ m.frame_id }} : {{ m.name }}</button>
    <div class="content">
    <table>
      <tr><th>Campo</th><th>Antes</th><th>Depois</th></tr>
      {% for field, diff in m.diffs.items() %}
      <tr class="changed">
        <td>{{ field }}</td>
        <td class="code">{{ diff.0 }}</td>
        <td class="code">{{ diff.1 }}</td>
      </tr>
      {% endfor %}
    </table>
    </div>
    {% endfor %}
  {% else %}<p>Nenhuma mensagem alterada.</p>{% endif %}

  <h2>🟩 Sinais Adicionados</h2>
  {% if dbc.added %}
  <table>
  <tr><th>Message ID</th><th>Signal</th></tr>
  {% for s in dbc.added %}
    <tr class="added"><td>{{ s.id }}</td><td>{{ s.sig }}</td></tr>
  {% endfor %}
  </table>
  {% else %}<p>Nenhum sinal adicionado.</p>{% endif %}

  <h2>🟥 Sinais Removidos</h2>
  {% if dbc.removed %}
  <table>
  <tr><th>Message ID</th><th>Signal</th></tr>
  {% for s in dbc.removed %}
    <tr class="removed"><td>{{ s.id }}</td><td>{{ s.sig }}</td></tr>
  {% endfor %}
  </table>
  {% else %}<p>Nenhum sinal removido.</p>{% endif %}

  <h2>🟨 Sinais Alterados</h2>
  {% if dbc.changed %}
    {% for c in dbc.changed %}
    <button type="button" class="collapsible">{{ c.id }} : {{ c.sig }}</button>
    <div class="content">
    <table>
      <tr><th>Campo</th><th>Antes</th><th>Depois</th></tr>
      {% for field, diff in c.diffs.items() %}
      <tr class="changed">
        <td>{{ field }}</td>
        <td class="code">{{ diff.0 }}</td>
        <td class="code">{{ diff.1 }}</td>
      </tr>
      {% endfor %}
    </table>
    </div>
    {% endfor %}
  {% else %}<p>Nenhuma alteração encontrada.</p>{% endif %}
</div>
{% endfor %}

<script>
function openTab(evt, tabName) {
  var i, tabcontent, tablinks;
  tabcontent=document.getElementsByClassName("tabcontent");
  for(i=0;i<tabcontent.length;i++){ tabcontent[i].style.display="none"; }
  tablinks=document.getElementsByClassName("tablinks");
  for(i=0;i<tablinks.length;i++){ tablinks[i].className=tablinks[i].className.replace(" active",""); }
  document.getElementById(tabName).style.display="block";
  evt.currentTarget.className+=" active";
}
document.getElementsByClassName("tablinks")[0].click();

var coll=document.getElementsByClassName("collapsible");
for(var i=0;i<coll.length;i++){
  coll[i].addEventListener("click",function(){
    this.classList.toggle("active_collapsible");
    var content=this.nextElementSibling;
    content.style.display=(content.style.display==="block")?"none":"block";
  });
}
</script>
</body>
</html>
"""

# ---------------- Functions ----------------
def load_db(path):
    return cantools.database.load_file(path)

def index_signals(db):
    d={}
    for msg in db.messages:
        for sig in msg.signals:
            d[(msg.frame_id,sig.name)] = sig
    return d

def diff_signal(sig_old, sig_new):
    fields=["minimum","maximum","scale","offset","length","start","byte_order",
            "is_multiplexer","multiplexer_signal","multiplexer_ids","choices"]
    diffs={}
    for f in fields:
        v1=getattr(sig_old,f,None)
        v2=getattr(sig_new,f,None)
        if v1!=v2:
            diffs[f]=(v1,v2)
    return diffs

def diff_message(msg_old, msg_new):
    diffs={}
    fields=["name","length","cycle_time","signals"]
    for f in fields:
        v1=getattr(msg_old,f,None)
        v2=getattr(msg_new,f,None)
        if f=="signals":
            v1=[s.name for s in msg_old.signals]
            v2=[s.name for s in msg_new.signals]
        if v1!=v2:
            diffs[f]=(v1,v2)
    return diffs

# ---------------- Main ----------------
dbcs=[]
current_files=[f for f in os.listdir(DBC_DIR) if f.lower().endswith(".dbc")]
old_files=[f for f in os.listdir(OLD_DIR) if f.lower().endswith(".dbc")]

added_files=list(set(current_files)-set(old_files))
removed_files=list(set(old_files)-set(current_files))

for dbc in current_files:
    path_new=os.path.join(DBC_DIR,dbc)
    path_old=os.path.join(OLD_DIR,dbc)
    db_new=load_db(path_new)
    db_old=load_db(path_old) if os.path.exists(path_old) else None

    i_new=index_signals(db_new)
    i_old=index_signals(db_old) if db_old else {}

    # Nodes
    nodes=[n for n in db_new.nodes]

    # Messages diff
    msg_dict_new={m.frame_id:m for m in db_new.messages}
    msg_dict_old={m.frame_id:m for m in db_old.messages} if db_old else {}

    msg_added=[]
    msg_removed=[]
    msg_changed=[]
    for fid,m in msg_dict_new.items():
        if fid not in msg_dict_old:
            msg_added.append({"frame_id":m.frame_id,"name":m.name,"length":m.length,
                              "cycle_time":m.cycle_time,"signals":[s.name for s in m.signals]})
        else:
            diffs=diff_message(msg_dict_old[fid],m)
            if diffs:
                msg_changed.append({"frame_id":m.frame_id,"name":m.name,"diffs":diffs})

    for fid,m in msg_dict_old.items():
        if fid not in msg_dict_new:
            msg_removed.append({"frame_id":m.frame_id,"name":m.name,"length":m.length,
                                "cycle_time":m.cycle_time,"signals":[s.name for s in m.signals]})

    # Signals diff
    added=[{"id":k[0],"sig":k[1]} for k in i_new.keys()-i_old.keys()]
    removed=[{"id":k[0],"sig":k[1]} for k in i_old.keys()-i_new.keys()]
    changed=[]
    for k in i_new.keys() & i_old.keys():
        diffs=diff_signal(i_old[k],i_new[k])
        if diffs:
            changed.append({"id":k[0],"sig":k[1],"diffs":diffs})

    dbcs.append({
        "name": dbc,
        "nodes": nodes,
        "messages": db_new.messages,
        "signals": list(i_new.keys()),
        "added": added,
        "removed": removed,
        "changed": changed,
        "msg_added": msg_added,
        "msg_removed": msg_removed,
        "msg_changed": msg_changed
    })

    # Update old
    shutil.copy(path_new,path_old)
    print(f"[OK] Processed {dbc}")

# Generate dashboard
template=Template(html_template)
report_file=os.path.join(REPORT_DIR,"dashboard.html")
html=template.render(dbcs=dbcs,added_files=added_files,removed_files=removed_files)
with open(report_file,"w",encoding="utf-8") as f:
    f.write(html)
print(f"\n[DONE] Dashboard completo gerado: {report_file}")
