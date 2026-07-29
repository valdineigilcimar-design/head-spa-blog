# -*- coding: utf-8 -*-
"""Publica os artigos no blog do Shopify (headspabrasil.com/blogs/blog).

Fluxo novo (2026): apps do Dev Dashboard nao exibem mais token na interface.
Usamos "client credentials grant": trocamos Client ID + Chave secreta por um
token de curta duracao, na hora. O token nunca fica gravado em disco.

A CHAVE SECRETA nunca aparece neste arquivo. Ela e lida de:
    ~/Claude/.shopify_secret

Uso:
    python3 shopify_publish.py             # testa conexao e lista os blogs
    python3 shopify_publish.py --publicar  # cria/atualiza os posts
"""
import glob, json, os, re, sys, zipfile, urllib.request, urllib.error

LOJA = "head-spa-brasil"
CLIENT_ID = "37281659f580462f940ef95ff76d44fa"   # publico, visivel no Dev Dashboard
VERSAO_API = "2025-07"
DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shopify")
AUTOR = "Head Spa Brasil"

CANDIDATOS_SEGREDO = [
    "~/Claude/.shopify_secret",
    "~/Desktop/api/*",
    "~/Desktop/segredo.*",
    "~/Claude/.shopify_token",
]
IGNORAR = {".DS_Store", "Thumbs.db"}


def _texto_de(caminho):
    if caminho.lower().endswith((".docx", ".dotx")):
        try:
            with zipfile.ZipFile(caminho) as z:
                xml = z.read("word/document.xml").decode("utf-8", errors="replace")
            partes = re.findall(r"<w:t[^>]*>(.*?)</w:t>", xml, re.S)
            return "".join(partes) if partes else re.sub(r"<[^>]+>", "", xml)
        except (zipfile.BadZipFile, KeyError, OSError):
            return ""
    try:
        return open(caminho, encoding="utf-8", errors="replace").read()
    except OSError:
        return ""


def _limpar(t):
    t = re.sub(r"\\'[0-9a-fA-F]{2}", "", t)
    t = re.sub(r"\\[a-zA-Z]+-?\d* ?", "", t)
    return t


def ler_segredo():
    """Le a chave secreta do app sem nunca imprimi-la."""
    inspecionados = []
    for padrao in CANDIDATOS_SEGREDO:
        for caminho in sorted(glob.glob(os.path.expanduser(padrao))):
            if not os.path.isfile(caminho) or os.path.basename(caminho) in IGNORAR:
                continue
            bruto = _texto_de(caminho)
            if not bruto:
                continue
            for variante in (bruto, _limpar(bruto), re.sub(r"\s+", "", bruto)):
                # chave secreta de app do Dev Dashboard: prefixo shpss_ ou hex de 32+
                m = re.search(r"shpss_[A-Za-z0-9]{20,}", variante)
                if m:
                    print("Chave secreta lida de: %s" % caminho)
                    return m.group(0)
                m = re.search(r"\b[0-9a-f]{32,}\b", variante)
                if m:
                    print("Chave secreta lida de: %s" % caminho)
                    return m.group(0)
            inspecionados.append(caminho)

    print("ERRO: nao encontrei a chave secreta do app.\n")
    if inspecionados:
        print("Arquivos inspecionados sem sucesso:")
        for c in inspecionados:
            print("   -", c)
    print("""
Pegue a chave secreta em:
  dev.shopify.com -> Apps -> Blog Automatico -> Configuracoes -> Credenciais
  campo "Chave secreta" (clique no olho para revelar, ou no botao de copiar)

Salve com este comando (nao aparece na tela enquanto voce cola):

  mkdir -p ~/Claude
  printf 'cole a chave secreta e de Enter: '
  IFS= read -rs S
  printf '%s' "$S" > ~/Claude/.shopify_secret
  echo; echo "salvo"
""")
    sys.exit(1)


def obter_token():
    """Troca client_id + chave secreta por um access token de curta duracao."""
    segredo = ler_segredo()
    url = "https://%s.myshopify.com/admin/oauth/access_token" % LOJA
    corpo = json.dumps({
        "client_id": CLIENT_ID,
        "client_secret": segredo,
        "grant_type": "client_credentials",
    }).encode()
    req = urllib.request.Request(url, data=corpo, method="POST",
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            dados = json.loads(r.read())
    except urllib.error.HTTPError as e:
        detalhe = e.read().decode(errors="replace")[:400]
        print("\nERRO %s ao trocar credenciais por token." % e.code)
        print(detalhe)
        if e.code in (400, 401):
            print("\nCausas mais comuns:")
            print("  - a chave secreta esta errada ou incompleta;")
            print("  - o app 'Blog Automatico' NAO esta instalado na loja.")
            print("    Instale em: dev.shopify.com -> Blog Automatico -> Instalar app")
        sys.exit(1)
    tok = dados.get("access_token")
    if not tok:
        sys.exit("ERRO: resposta sem access_token: %s" % list(dados))
    print("Token obtido (valido por %s segundos)." % dados.get("expires_in", "?"))
    return tok


TOKEN = obter_token()
GQL = "https://%s.myshopify.com/admin/api/%s/graphql.json" % (LOJA, VERSAO_API)
HDRS = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}


def gql(query, variables=None):
    corpo = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(GQL, data=corpo, headers=HDRS, method="POST")
    try:
        with urllib.request.urlopen(req) as r:
            resp = json.loads(r.read())
    except urllib.error.HTTPError as e:
        sys.exit("ERRO HTTP %s\n%s" % (e.code, e.read().decode(errors="replace")[:400]))
    if resp.get("errors"):
        sys.exit("ERRO GraphQL: %s" % json.dumps(resp["errors"], ensure_ascii=False)[:600])
    return resp["data"]


Q_BLOGS = "{ blogs(first: 20) { nodes { id handle title } } }"

Q_ARTIGOS = """
query($id: ID!) {
  blog(id: $id) { articles(first: 100) { nodes { id handle } } }
}"""

M_CRIAR = """
mutation($article: ArticleCreateInput!) {
  articleCreate(article: $article) {
    article { id handle }
    userErrors { field message }
  }
}"""

M_ATUALIZAR = """
mutation($id: ID!, $article: ArticleUpdateInput!) {
  articleUpdate(id: $id, article: $article) {
    article { id handle }
    userErrors { field message }
  }
}"""


def main():
    blogs = gql(Q_BLOGS)["blogs"]["nodes"]
    if not blogs:
        sys.exit("ERRO: a loja nao tem nenhum blog.")
    print("\nBlogs na loja:")
    for b in blogs:
        print("   %-16s %s" % (b["handle"], b["title"]))
    blog = next((b for b in blogs if b["handle"] == "blog"), blogs[0])
    print("\nUsando: %s (%s)" % (blog["title"], blog["handle"]))

    if "--publicar" not in sys.argv:
        print("\nModo leitura, nada foi publicado.")
        print("Para publicar: python3 shopify_publish.py --publicar")
        return

    posts = json.load(open(os.path.join(DIR, "_posts.json"), encoding="utf-8"))
    existentes = {a["handle"]: a["id"]
                  for a in gql(Q_ARTIGOS, {"id": blog["id"]})["blog"]["articles"]["nodes"]}

    criados = atualizados = 0
    for p in reversed(posts):
        corpo = open(os.path.join(DIR, p["arquivo"]), encoding="utf-8").read()
        campos = {
            "title": p["titulo"],
            "handle": p["slug"],
            "body": corpo,
            "summary": p["resumo"],
            "tags": [t.strip() for t in p["tags"].split(",")],
            "author": {"name": AUTOR},
            "isPublished": True,
        }
        if p["slug"] in existentes:
            d = gql(M_ATUALIZAR, {"id": existentes[p["slug"]], "article": campos})["articleUpdate"]
            acao, atualizados = "atualizado", atualizados + 1
        else:
            campos["blogId"] = blog["id"]
            d = gql(M_CRIAR, {"article": campos})["articleCreate"]
            acao, criados = "criado   ", criados + 1
        erros = d.get("userErrors") or []
        if erros:
            print("  FALHA em %s: %s" % (p["slug"], erros))
        else:
            print("  %s: %s" % (acao, p["slug"]))

    print("\nResumo: %d criados, %d atualizados." % (criados, atualizados))
    print("Confira: https://headspabrasil.com/blogs/%s" % blog["handle"])


if __name__ == "__main__":
    main()
