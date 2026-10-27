"""Monta o Radar Noronha independente.
Uso: python3 build_site.py <pagina.html do Radar> <pasta saida/ do pipeline> <pasta destino> <agora 'DD/MM/AA HH:MM'> [--embutir]
Sem --embutir: gera index.html + <dataset>.json na raiz da pasta destino (para hospedar, ex.: GitHub Pages).
Com --embutir: um único radar.html com os dados dentro (para abrir direto no navegador)."""
import json, sys, os, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
page_p, saida, dest, agora = sys.argv[1:5]; emb = "--embutir" in sys.argv
IDS = ['viagens', 'fila_diaria', 'situacao_atual', 'programacao', 'frota', 'registros', 'posicoes_ais']
page = open(page_p).read()
def rep(old, new):
    global page
    if old in page: page = page.replace(old, new)
    else: print("aviso: trecho não encontrado:", old[:60])
# Ajustes para quem não usa o Claude: sem link para a Central e texto de acesso correto.
import re
page = re.sub(r' · <a href="https://claude\.ai/artifact/[^"]+"[^>]*>Central de Operações</a> \(importar WhatsApp e registrar eventos\)', '', page)
page = re.sub(r'<p>Só entra quem foi convidado[^<]*(<[^/][^>]*>[^<]*</[^>]+>[^<]*)*</p>',
              '<p>Esta página é pública para quem tiver o link e não exige login. Mensagens do WhatsApp nunca aparecem aqui, nem nomes de quem enviou boletins ou registrou eventos.</p>', page)
rep("Registre na Central de Operações.", "")
data = {i: json.load(open(f"{saida}/{i}.json")) for i in IDS}
for r in data["situacao_atual"]: r["boletim_por"] = ""  # nunca publicar nomes
data["meta"] = {"gerado_em": agora}
tok = open(f"{HERE}/tokens.css").read(); shim = open(f"{HERE}/shim.js").read(); d3 = open(f"{HERE}/d3.min.js").read()
head = ('<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
        '<meta name="robots" content="noindex"><title>Radar Noronha · Além Mar</title><meta name="theme-color" content="#1a5c2a">')
foot = '<p class="radar-rodape">Página gerada em <span id="radar-gerado">—</span> · atualizada automaticamente a cada 4 horas, das 06:38 às 22:38 (horário de Recife).</p>'
os.makedirs(dest, exist_ok=True)
if emb:
    blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    out = (head + f"<style>{tok}</style><script>{d3}</script><script>window.RADAR_DATA={blob};</script><script>{shim}</script></head><body>"
           f'<div id="dash-root">{page}</div>{foot}</body></html>')
    open(f"{dest}/radar.html", "w").write(out)
else:
    # Tudo na raiz do repositório (o envio pelo site do GitHub achata pastas).
    for k, v in data.items(): json.dump(v, open(f"{dest}/{k}.json", "w"), ensure_ascii=False)
    same = os.path.abspath(dest) == HERE
    if not same:
        shutil.copy(f"{HERE}/d3.min.js", f"{dest}/d3.min.js")
    open(f"{dest}/radar.css", "w").write(tok); open(f"{dest}/radar-shim.js", "w").write(shim)
    open(f"{dest}/index.html", "w").write(head + '<link rel="stylesheet" href="radar.css"><script src="d3.min.js"></script><script src="radar-shim.js"></script></head><body>'
        f'<div id="dash-root">{page}</div>{foot}</body></html>')
    open(f"{dest}/.nojekyll", "w").write("")
print("ok")
