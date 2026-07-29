# -*- coding: utf-8 -*-
"""Converte os artigos para HTML pronto para o editor de blog do Shopify.

Diferencas em relacao ao build do GitHub Pages:
  - nao gera <html>/<head>/<body>: o tema do Shopify cuida disso
  - o script do AdSense JA esta no theme.liquid, entao aqui so entram os blocos <ins>
  - inclui 1 anuncio no meio do texto e 1 no fim
  - inclui bloco de fontes e aviso medico
"""
import os, re, json, shutil
from articles import ARTICLES, PUB

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shopify")
if os.path.isdir(OUT):
    shutil.rmtree(OUT)
os.makedirs(OUT, exist_ok=True)

LABELS = {"noticias": "Noticias", "dicas": "Dicas", "beneficios": "Saude Capilar", "produtos": "Produtos"}
TAGS = {"noticias": "noticias, head spa, mercado",
        "dicas": "dicas, tutorial, head spa",
        "beneficios": "saude capilar, couro cabeludo, bem-estar",
        "produtos": "produtos, equipamentos, head spa"}


def ad_block(slot, style, fmt="auto", extra=""):
    return ('\n<div style="margin:32px 0;text-align:center">'
            '<ins class="adsbygoogle" style="%s" data-ad-client="%s" data-ad-slot="%s" data-ad-format="%s"%s></ins>'
            '<script>(adsbygoogle=window.adsbygoogle||[]).push({});</script>'
            '</div>\n' % (style, PUB, slot, fmt, extra))


AD_MEIO = ad_block("3333333333", "display:block;min-height:250px")
AD_FIM = ad_block("4444444444", "display:block", extra=' data-full-width-responsive="true"')

CSS_INLINE = """<style>
.hsb-post h2{font-family:Georgia,'Playfair Display',serif;font-size:1.35rem;line-height:1.3;margin:34px 0 12px;color:#2c2420}
.hsb-post p{margin-bottom:17px;font-size:16px;line-height:1.85;color:#3d332c}
.hsb-post ul{padding-left:22px;margin-bottom:17px}
.hsb-post li{margin-bottom:9px;font-size:16px;line-height:1.8;color:#3d332c}
.hsb-post strong{color:#2c2420}
.hsb-fontes{margin-top:40px;padding-top:22px;border-top:1px solid #e2ddd6;font-size:14px;color:#666}
.hsb-fontes h3{font-family:Georgia,serif;font-size:1rem;margin-bottom:10px;color:#2c2420}
.hsb-fontes ul{list-style:none;padding-left:0}
.hsb-fontes li{margin-bottom:6px;font-size:14px}
.hsb-fontes a{color:#6b4f3a}
.hsb-aviso{margin-top:16px;font-size:13px;color:#888;font-style:italic}
</style>
"""

resumo = []

for a in ARTICLES:
    # divide o corpo em duas metades por <h2>, para inserir o anuncio no meio
    partes = re.split(r'(?=<h2>)', a["body"].strip())
    meio = max(1, len(partes) // 2)
    corpo = "".join(partes[:meio]) + AD_MEIO + "".join(partes[meio:])

    fontes = "".join('<li><a href="%s" target="_blank" rel="noopener nofollow">%s</a></li>' % (u, t)
                     for t, u in a["sources"])

    html = (CSS_INLINE
            + '<div class="hsb-post">\n'
            + corpo
            + AD_FIM
            + '<div class="hsb-fontes"><h3>Fontes consultadas</h3><ul>' + fontes + '</ul>'
            + '<p class="hsb-aviso">Este conteudo tem caracter informativo e nao substitui '
              'avaliacao medica ou dermatologica. Em caso de queda acentuada, feridas, dor ou '
              'descamacao persistente no couro cabeludo, procure um dermatologista.</p></div>\n'
            + '</div>')

    fn = os.path.join(OUT, a["slug"] + ".html")
    open(fn, "w", encoding="utf-8").write(html)

    palavras = len(re.sub(r"<[^>]+>", " ", a["body"]).split())
    resumo.append({
        "slug": a["slug"],
        "titulo": a["title"],
        "resumo": a["excerpt"],
        "tags": TAGS[a["cat"]],
        "categoria": LABELS[a["cat"]],
        "arquivo": a["slug"] + ".html",
        "palavras": palavras,
        "anuncios": html.count('class="adsbygoogle"'),
    })

open(os.path.join(OUT, "_posts.json"), "w", encoding="utf-8").write(
    json.dumps(resumo, ensure_ascii=False, indent=2))

print("%-46s %8s %5s" % ("ARTIGO", "PALAVRAS", "ADS"))
print("-" * 62)
for r in resumo:
    print("%-46s %8d %5d" % (r["slug"][:46], r["palavras"], r["anuncios"]))
print("-" * 62)
print("Total: %d artigos, %d palavras" % (len(resumo), sum(r["palavras"] for r in resumo)))
print("\nArquivos em shopify/:")
for f in sorted(os.listdir(OUT)):
    print("  %-46s %6d bytes" % (f, os.path.getsize(os.path.join(OUT, f))))
