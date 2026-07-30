# -*- coding: utf-8 -*-
"""Converte os artigos para HTML aceito pelo editor de blog do Shopify.

IMPORTANTE — por que este arquivo nao tem <style>, <script> nem <ins>:
O Shopify sanitiza o corpo dos posts e remove essas tags por seguranca.
Quando elas estao presentes, o restante do HTML e truncado e o artigo
aparece cortado (foi exatamente o que aconteceu na primeira tentativa).

Os anuncios NAO vao no corpo do artigo. O script do AdSense ja esta no
theme.liquid do tema, e o posicionamento fica por conta dos Anuncios
Automaticos do AdSense, que inserem os blocos sozinhos na pagina.

Saida: apenas <h2>, <p>, <strong>, <em>, <ul>, <li> e <a>.
"""
import os, re, json, shutil
from articles import ARTICLES, PUB

OUT = os.environ.get("HSB_OUT") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "shopify")
if os.path.isdir(OUT):
    shutil.rmtree(OUT)
os.makedirs(OUT, exist_ok=True)

LABELS = {"noticias": "Noticias", "dicas": "Dicas", "beneficios": "Saude Capilar", "produtos": "Produtos"}
TAGS = {"noticias": "noticias, head spa, mercado",
        "dicas": "dicas, tutorial, head spa",
        "beneficios": "saude capilar, couro cabeludo, bem-estar",
        "produtos": "produtos, equipamentos, head spa"}

# tags que o Shopify aceita no corpo de um post
PERMITIDAS = {"h2", "h3", "p", "strong", "em", "ul", "ol", "li", "a", "br", "blockquote"}

AVISO = ("<p><em>Este conteudo tem carater informativo e nao substitui avaliacao "
         "medica ou dermatologica. Em caso de queda acentuada, feridas, dor ou "
         "descamacao persistente no couro cabeludo, procure um dermatologista.</em></p>")


def higienizar(html):
    """Remove qualquer tag que o Shopify iria descartar, preservando o texto."""
    # fora blocos inteiros de style/script, com conteudo
    html = re.sub(r"<(style|script)\b[^>]*>.*?</\1>", "", html, flags=re.S | re.I)
    # remove atributos de classe/id/style que nao servem para nada aqui
    html = re.sub(r'\s+(class|id|style)="[^"]*"', "", html)

    def _tag(m):
        fecha, nome = m.group(1), m.group(2).lower()
        if nome in PERMITIDAS:
            return m.group(0)
        return ""  # descarta a tag, mantem o texto interno

    return re.sub(r"</?([a-zA-Z][a-zA-Z0-9]*)\b[^>]*>",
                  lambda m: _tag(re.match(r"</?()([a-zA-Z][a-zA-Z0-9]*)", m.group(0))) or "",
                  html)


def limpar(html):
    html = re.sub(r"<(style|script)\b[^>]*>.*?</\1>", "", html, flags=re.S | re.I)
    html = re.sub(r'\s+(class|id|style)="[^"]*"', "", html)
    partes = []
    for pedaco in re.split(r"(<[^>]+>)", html):
        if pedaco.startswith("<"):
            m = re.match(r"</?\s*([a-zA-Z][a-zA-Z0-9]*)", pedaco)
            if m and m.group(1).lower() in PERMITIDAS:
                partes.append(pedaco)
            # senao: descarta a tag mas mantem o texto que vier depois
        else:
            partes.append(pedaco)
    saida = "".join(partes)
    saida = re.sub(r"\n{3,}", "\n\n", saida)
    return saida.strip()


resumo = []

for a in ARTICLES:
    corpo = limpar(a["body"])

    fontes = "".join(
        '<li><a href="%s" rel="nofollow">%s</a></li>' % (u, t) for t, u in a["sources"])
    bloco_fontes = "<h2>Fontes consultadas</h2><ul>%s</ul>%s" % (fontes, AVISO)

    html = corpo + "\n" + bloco_fontes

    fn = os.path.join(OUT, a["slug"] + ".html")
    open(fn, "w", encoding="utf-8").write(html)

    texto = re.sub(r"<[^>]+>", " ", corpo)
    resumo.append({
        "slug": a["slug"],
        "titulo": a["title"],
        "resumo": a["excerpt"],
        "tags": TAGS[a["cat"]],
        "categoria": LABELS[a["cat"]],
        "arquivo": a["slug"] + ".html",
        "palavras": len(texto.split()),
        "h2": html.count("<h2>"),
    })

open(os.path.join(OUT, "_posts.json"), "w", encoding="utf-8").write(
    json.dumps(resumo, ensure_ascii=False, indent=2))

# verificacao: nenhuma tag proibida pode ter sobrado
proibidas = []
for r in resumo:
    s = open(os.path.join(OUT, r["arquivo"]), encoding="utf-8").read()
    for t in ("<style", "<script", "<ins", "<div", "class="):
        if t in s:
            proibidas.append((r["slug"], t))

print("%-46s %8s %4s" % ("ARTIGO", "PALAVRAS", "H2"))
print("-" * 62)
for r in resumo:
    print("%-46s %8d %4d" % (r["slug"][:46], r["palavras"], r["h2"]))
print("-" * 62)
print("Total: %d artigos, %d palavras" % (len(resumo), sum(r["palavras"] for r in resumo)))

if proibidas:
    print("\nERRO: sobraram tags que o Shopify remove:")
    for slug, t in proibidas:
        print("   %s -> %s" % (slug, t))
    raise SystemExit(1)
print("\nOK: nenhuma tag proibida. HTML pronto para o Shopify.")
print("Anuncios: ficam por conta dos Anuncios Automaticos do AdSense (%s)," % PUB)
print("cujo script ja esta no theme.liquid. Nao vao no corpo do post.")
