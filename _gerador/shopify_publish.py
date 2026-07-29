# -*- coding: utf-8 -*-
"""Publica os artigos como posts no blog do Shopify (headspabrasil.com/blogs/blog).

O token NUNCA fica neste arquivo. Ele e lido de:
    /Users/neygrande/Claude/.shopify_token

Uso:
    python3 shopify_publish.py            # lista os blogs da loja (nao publica nada)
    python3 shopify_publish.py --publicar  # cria/atualiza os posts
"""
import glob, json, os, re, sys, urllib.request, urllib.error

LOJA = "head-spa-brasil"
VERSAO_API = "2025-01"
DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shopify")
AUTOR = "Head Spa Brasil"

# Onde procurar o token, em ordem. Aceita .txt e .rtf (extrai o shpat_ de dentro).
CANDIDATOS = [
    "~/Claude/.shopify_token",
    "~/Desktop/api/api.rtf",
    "~/Desktop/api/api.txt",
    "~/Desktop/api/*",
    "~/Desktop/api.rtf",
    "~/Desktop/api.txt",
    "~/Claude/shopify_token.txt",
]


def ler_token():
    """Le o token sem imprimi-lo. Extrai o padrao shpat_... de texto puro ou RTF."""
    vistos = []
    for padrao in CANDIDATOS:
        for caminho in sorted(glob.glob(os.path.expanduser(padrao))):
            if not os.path.isfile(caminho):
                continue
            vistos.append(caminho)
            try:
                bruto = open(caminho, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            m = re.search(r"shpat_[A-Za-z0-9_]{20,}", bruto)
            if m:
                print("Token localizado em: %s" % caminho)
                return m.group(0)

    print("ERRO: nao encontrei um token valido (padrao shpat_...).")
    if vistos:
        print("Arquivos que eu inspecionei:")
        for v in vistos:
            print("   -", v)
    else:
        print("Nenhum dos caminhos esperados existe.")
    print("\nSalve o token da Admin API do Shopify em ~/Claude/.shopify_token")
    print("(texto puro, apenas o valor que comeca com shpat_)")
    sys.exit(1)


TOKEN = ler_token()
BASE = "https://%s.myshopify.com/admin/api/%s" % (LOJA, VERSAO_API)
HDRS = {"X-Shopify-Access-Token": TOKEN,
        "Content-Type": "application/json",
        "Accept": "application/json"}


def api(caminho, data=None, method="GET"):
    req = urllib.request.Request(BASE + caminho, headers=HDRS,
                                 data=json.dumps(data).encode() if data else None,
                                 method=method)
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        corpo = e.read().decode(errors="replace")[:500]
        sys.exit("ERRO HTTP %s em %s %s\n%s" % (e.code, method, caminho, corpo))


def escolher_blog():
    blogs = api("/blogs.json").get("blogs", [])
    if not blogs:
        sys.exit("ERRO: a loja nao tem nenhum blog criado.")
    print("Blogs encontrados na loja:")
    for b in blogs:
        print("  id=%-12s handle=%-14s titulo=%s" % (b["id"], b.get("handle"), b.get("title")))
    # prefere o handle 'blog', que e o que esta no menu do site
    for b in blogs:
        if b.get("handle") == "blog":
            return b
    return blogs[0]


def main():
    blog = escolher_blog()
    print("\nUsando blog: %s (id=%s)" % (blog.get("title"), blog["id"]))

    if "--publicar" not in sys.argv:
        print("\nModo leitura. Nada foi publicado.")
        print("Para publicar de verdade, rode: python3 shopify_publish.py --publicar")
        return

    posts = json.load(open(os.path.join(DIR, "_posts.json"), encoding="utf-8"))
    existentes = {a.get("handle"): a["id"]
                  for a in api("/blogs/%s/articles.json?limit=250" % blog["id"]).get("articles", [])}

    criados = atualizados = 0
    # publica na ordem inversa para o mais relevante ficar no topo da listagem
    for p in reversed(posts):
        corpo = open(os.path.join(DIR, p["arquivo"]), encoding="utf-8").read()
        payload = {"article": {
            "title": p["titulo"],
            "author": AUTOR,
            "body_html": corpo,
            "summary_html": "<p>%s</p>" % p["resumo"],
            "tags": p["tags"],
            "handle": p["slug"],
            "published": True,
        }}
        if p["slug"] in existentes:
            aid = existentes[p["slug"]]
            payload["article"]["id"] = aid
            api("/blogs/%s/articles/%s.json" % (blog["id"], aid), payload, "PUT")
            print("  atualizado: %s" % p["slug"])
            atualizados += 1
        else:
            r = api("/blogs/%s/articles.json" % blog["id"], payload, "POST")
            print("  criado:     %s  ->  /blogs/%s/%s"
                  % (p["slug"], blog.get("handle"), r["article"].get("handle")))
            criados += 1

    print("\nResumo: %d criados, %d atualizados." % (criados, atualizados))
    print("Confira em: https://headspabrasil.com/blogs/%s" % blog.get("handle"))


if __name__ == "__main__":
    main()
