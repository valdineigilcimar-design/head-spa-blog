# -*- coding: utf-8 -*-
"""Publica os artigos como posts no blog do Shopify (headspabrasil.com/blogs/blog).

O token NUNCA fica neste arquivo. Ele e lido de:
    /Users/neygrande/Claude/.shopify_token

Uso:
    python3 shopify_publish.py            # lista os blogs da loja (nao publica nada)
    python3 shopify_publish.py --publicar  # cria/atualiza os posts
"""
import glob, json, os, re, sys, zipfile, urllib.request, urllib.error

LOJA = "head-spa-brasil"
VERSAO_API = "2025-01"
DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shopify")
AUTOR = "Head Spa Brasil"

# Onde procurar o token. Aceita .txt, .rtf, .docx e qualquer arquivo solto na pasta.
CANDIDATOS = [
    "~/Claude/.shopify_token",
    "~/Desktop/api/*",
    "~/Desktop/api.*",
    "~/Documents/api/*",
    "~/Claude/shopify_token.txt",
    "~/Downloads/api.*",
]

IGNORAR = {".DS_Store", "Thumbs.db"}


def _texto_de(caminho):
    """Devolve o texto de um arquivo, lidando com .docx (zip) e texto/RTF."""
    if caminho.lower().endswith((".docx", ".dotx")):
        try:
            with zipfile.ZipFile(caminho) as z:
                xml = z.read("word/document.xml").decode("utf-8", errors="replace")
            # junta os <w:t> e remove as tags; assim um token quebrado
            # em varios "runs" pelo Word volta a ficar inteiro
            partes = re.findall(r"<w:t[^>]*>(.*?)</w:t>", xml, re.S)
            return "".join(partes) if partes else re.sub(r"<[^>]+>", "", xml)
        except (zipfile.BadZipFile, KeyError, OSError):
            return ""
    try:
        return open(caminho, encoding="utf-8", errors="replace").read()
    except OSError:
        return ""


def _limpar(texto):
    """Remove marcacao RTF e espacos que possam ter sido inseridos no meio do token."""
    t = re.sub(r"\\'[0-9a-fA-F]{2}", "", texto)   # escapes RTF
    t = re.sub(r"\\[a-zA-Z]+-?\d* ?", "", t)      # control words RTF
    return t


def ler_token():
    """Le o token sem nunca imprimi-lo. Suporta texto puro, RTF e Word (.docx)."""
    inspecionados = []
    for padrao in CANDIDATOS:
        for caminho in sorted(glob.glob(os.path.expanduser(padrao))):
            if not os.path.isfile(caminho) or os.path.basename(caminho) in IGNORAR:
                continue
            bruto = _texto_de(caminho)
            if not bruto:
                inspecionados.append((caminho, "nao consegui ler", None))
                continue
            for candidato in (bruto, _limpar(bruto), re.sub(r"\s+", "", bruto)):
                m = re.search(r"shpat_[A-Za-z0-9]{20,}", candidato)
                if m:
                    print("Token localizado em: %s" % caminho)
                    return m.group(0)
            # nao achou: guarda um diagnostico que NAO revela o conteudo
            longas = sorted(set(re.findall(r"[A-Za-z0-9_]{16,}", re.sub(r"\s+", "", bruto))),
                            key=len, reverse=True)[:3]
            diag = []
            for r in longas:
                if r.startswith("shp"):
                    tipo = "comeca com shp mas formato inesperado"
                elif re.fullmatch(r"[0-9a-f]+", r):
                    tipo = "hex puro -> parece a Chave da API, nao o token"
                else:
                    tipo = "outro"
                diag.append("len=%d (%s)" % (len(r), tipo))
            inspecionados.append((caminho, "sem padrao shpat_", diag))

    print("ERRO: nao encontrei um token de acesso valido (padrao shpat_...).\n")
    if inspecionados:
        print("Arquivos inspecionados:")
        for caminho, motivo, diag in inspecionados:
            print("   - %s  [%s]" % (caminho, motivo))
            for d in (diag or []):
                print("       sequencia longa: %s" % d)
    else:
        print("Nenhum dos caminhos esperados existe.")
    print("""
O valor certo e o "Token de acesso da Admin API", que comeca com shpat_.
Ele so aparece DEPOIS de clicar em "Instalar app" no Shopify.
Nao confundir com "Chave da API" nem "Chave secreta da API" (ambas hex).

Salve apenas esse valor, em texto puro, em:
   ~/Claude/.shopify_token

No Terminal da para criar assim, colando o token quando pedir:
   mkdir -p ~/Claude && read -s -p "cole o token: " T && printf '%s' "$T" > ~/Claude/.shopify_token && echo OK
""")
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
