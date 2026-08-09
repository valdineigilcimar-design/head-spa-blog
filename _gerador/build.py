# -*- coding: utf-8 -*-
"""Gera o site completo do Blog Head Spa Brasil."""
import os, json, datetime, shutil
from articles import ARTICLES, PUB

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "site")
if os.path.isdir(OUT):
    try:
        shutil.rmtree(OUT)
    except OSError:
        # Em ambientes que nao permitem apagar arquivos na pasta montada
        # (o sandbox das tarefas agendadas do Cowork, por exemplo), apaga o
        # que der e segue: o build reescreve todos os arquivos por cima.
        # Efeito colateral: paginas de artigos removidos da lista podem
        # sobrar na pasta. Rodar o build no Mac limpa tudo de novo.
        shutil.rmtree(OUT, ignore_errors=True)
os.makedirs(os.path.join(OUT, "artigos"), exist_ok=True)

LABELS = {"noticias": "Noticias", "dicas": "Dicas", "beneficios": "Saude Capilar", "produtos": "Produtos"}
EMOJIS = {"noticias": "\U0001F4F0", "dicas": "\U0001F486", "beneficios": "\U0001F33F", "produtos": "✨"}

CSS = """*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--cream:#f7f5f0;--light-cream:#faf9f6;--dark:#2c2420;--brown:#6b4f3a;--gold:#a8896c;--border:#e2ddd6;--ticker-bg:#1a1310}
body{background:var(--cream);color:var(--dark);font-family:'Inter',sans-serif;line-height:1.6}
.ticker{background:var(--ticker-bg);color:#fff;font-size:12px;overflow:hidden;white-space:nowrap;padding:8px 0}
.ticker-inner{display:inline-block;animation:ticker 28s linear infinite}
.ticker-inner span{margin:0 48px}
@keyframes ticker{from{transform:translateX(0)}to{transform:translateX(-50%)}}
header{background:#fff;border-bottom:1px solid var(--border);padding:0 48px;display:flex;align-items:center;justify-content:space-between;height:80px;position:sticky;top:0;z-index:100}
nav a{font-size:13px;color:var(--dark);text-decoration:none;margin:0 14px;text-transform:uppercase}
nav a:hover,nav a.active{color:var(--brown)}
.hero{background:var(--light-cream);border-bottom:1px solid var(--border);text-align:center;padding:48px 24px 36px}
.hero h1{font-family:'Playfair Display',serif;font-size:clamp(2rem,4vw,3rem);color:var(--dark);margin-bottom:12px;line-height:1.2}
.hero p{color:var(--brown);font-size:15px}
.last-updated{font-size:12px;color:#999;margin-top:8px}
.categories{display:flex;justify-content:center;gap:8px;padding:24px;flex-wrap:wrap;border-bottom:1px solid var(--border);background:#fff}
.cat-btn{border:1px solid var(--border);background:transparent;color:var(--dark);font-family:'Inter',sans-serif;font-size:12px;text-transform:uppercase;padding:7px 18px;border-radius:2px;cursor:pointer;transition:all .2s}
.cat-btn:hover,.cat-btn.active{background:var(--dark);color:#fff;border-color:var(--dark)}
.page-body{max-width:1280px;margin:0 auto;padding:48px 32px;display:grid;grid-template-columns:1fr 300px;gap:48px}
.section-label{font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--gold);margin-bottom:28px;display:flex;align-items:center;gap:12px}
.section-label::after{content:'';flex:1;height:1px;background:var(--border)}
.articles-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:32px}
.card{background:#fff;border:1px solid var(--border);overflow:hidden;transition:transform .2s,box-shadow .2s}
.card:hover{transform:translateY(-4px);box-shadow:0 12px 32px rgba(0,0,0,.07)}
.card-img{width:100%;height:200px;display:flex;align-items:center;justify-content:center;font-size:56px;background:var(--cream)}
.card-body{padding:22px}
.card-category{font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:var(--gold);margin-bottom:8px}
.card-title{font-family:'Playfair Display',serif;font-size:1.15rem;line-height:1.45;margin-bottom:10px;color:var(--dark)}
.card-title a{color:inherit;text-decoration:none}
.card-title a:hover{color:var(--brown)}
.card-excerpt{font-size:13.5px;color:#666;line-height:1.7;margin-bottom:18px}
.card-meta{display:flex;align-items:center;justify-content:space-between;font-size:12px;color:#999;border-top:1px solid var(--border);padding-top:14px}
.read-more{font-size:11px;text-transform:uppercase;color:var(--brown);text-decoration:none;font-weight:500}
.card.featured{grid-column:1/-1;display:grid;grid-template-columns:1fr 1fr}
.card.featured .card-img{height:340px}
.card.featured .card-body{padding:36px;display:flex;flex-direction:column;justify-content:center}
.card.featured .card-title{font-size:1.7rem}
.sidebar{display:flex;flex-direction:column;gap:32px}
.sidebar-ad{position:sticky;top:96px}
.sidebar-widget{background:#fff;border:1px solid var(--border);padding:24px}
.sidebar-widget h3{font-family:'Playfair Display',serif;font-size:1rem;color:var(--dark);margin-bottom:16px;padding-bottom:12px;border-bottom:1px solid var(--border)}
.sidebar-widget ul{list-style:none}
.sidebar-widget li{padding:10px 0;border-bottom:1px solid var(--border);font-size:13px;color:#555;line-height:1.5}
.sidebar-widget li:last-child{border:none}
.sidebar-widget li a{color:var(--brown);text-decoration:none}
.ad-footer-wrap{background:#fff;padding:24px;border-top:1px solid var(--border)}
footer{background:var(--ticker-bg);color:#ccc;text-align:center;padding:40px 24px;font-size:13px;line-height:2}
footer a{color:var(--gold);text-decoration:none}
.footer-logo{font-family:'Playfair Display',serif;color:#fff;font-size:1.1rem;margin-bottom:12px}
.footer-nav{margin:14px 0;font-size:12px}
.footer-nav a{margin:0 10px}
article.post{background:#fff;border:1px solid var(--border);padding:48px}
article.post h2{font-family:'Playfair Display',serif;font-size:1.4rem;margin:32px 0 14px;color:var(--dark);line-height:1.3}
article.post p{margin-bottom:18px;font-size:15.5px;color:#3d332c;line-height:1.85}
article.post p strong{color:var(--dark)}
.post-meta{font-size:12px;color:#999;border-bottom:1px solid var(--border);padding-bottom:20px;margin-bottom:28px;text-transform:uppercase;letter-spacing:.06em}
.post-sources{margin-top:40px;padding-top:24px;border-top:1px solid var(--border);font-size:13px;color:#666}
.post-sources h3{font-family:'Playfair Display',serif;font-size:1rem;margin-bottom:12px;color:var(--dark)}
.post-sources a{color:var(--brown)}
.post-sources li{margin-bottom:6px;list-style:none}
.back-link{display:inline-block;margin-bottom:24px;font-size:12px;text-transform:uppercase;color:var(--brown);text-decoration:none;letter-spacing:.06em}
.static-page{background:#fff;border:1px solid var(--border);padding:48px}
.static-page h2{font-family:'Playfair Display',serif;font-size:1.3rem;margin:30px 0 12px;color:var(--dark)}
.static-page p,.static-page li{margin-bottom:14px;font-size:15px;color:#3d332c;line-height:1.8}
.static-page ul{padding-left:22px}
.static-page a{color:var(--brown)}
@media(max-width:900px){.page-body{grid-template-columns:1fr}aside.sidebar{display:none}}
@media(max-width:700px){header{flex-wrap:wrap;height:auto;padding:12px 16px;justify-content:center;gap:4px}nav{width:100%;text-align:center;padding-bottom:6px}nav a{margin:0 7px;font-size:11px}.page-body{padding:32px 16px}article.post,.static-page{padding:28px 20px}}"""

LOGO = ('<svg width="54" height="54" viewBox="0 0 100 110"><polygon points="50,4 96,28 96,82 50,106 4,82 4,28" fill="none" stroke="#6b4f3a" stroke-width="3"/>'
        '<polygon points="50,10 90,32 90,78 50,100 10,78 10,32" fill="none" stroke="#6b4f3a" stroke-width="1"/>'
        '<text x="50" y="48" text-anchor="middle" font-family="Georgia,serif" font-size="11" fill="#2c2420" font-weight="bold">Head Spa</text>'
        '<text x="50" y="62" text-anchor="middle" font-family="Georgia,serif" font-size="9" fill="#6b4f3a">BRASIL</text></svg>')

TICKER = ('<div class="ticker"><div class="ticker-inner">'
          + ('<span>O tratamento que esta conquistando o mundo.</span><span>Head Spa Brasil - Pioneiros no Brasil.</span><span>Conteudo atualizado 2x por dia.</span>' * 2)
          + '</div></div>')


def ad(slot, style, fmt="auto", extra=""):
    return ('<ins class="adsbygoogle" style="%s" data-ad-client="%s" data-ad-slot="%s" data-ad-format="%s"%s></ins>'
            '<script>(adsbygoogle=window.adsbygoogle||[]).push({});</script>' % (style, PUB, slot, fmt, extra))


def head(title, desc, base=""):
    return """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>%s</title>
<meta name="description" content="%s"/>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600&family=Inter:wght@300;400;500&display=swap" rel="stylesheet"/>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=%s" crossorigin="anonymous"></script>
<style>
%s
</style>
</head>
<body>
%s
<header>
<a href="%sindex.html" style="display:flex;align-items:center;gap:12px;text-decoration:none">%s</a>
<nav><a href="%sindex.html">Blog</a><a href="%ssobre.html">Sobre</a><a href="%scontato.html">Contato</a><a href="%sprivacidade.html">Privacidade</a></nav>
</header>
""" % (title, desc, PUB, CSS, TICKER, base, LOGO, base, base, base, base)


def footer(base=""):
    return """<div class="ad-footer-wrap" style="text-align:center">%s</div>
<footer><div class="footer-logo">Head Spa Brasil</div>
<p>Conteudo original em Portugues do Brasil sobre saude capilar e bem-estar.</p>
<div class="footer-nav"><a href="%sindex.html">Blog</a><a href="%ssobre.html">Sobre</a><a href="%scontato.html">Contato</a><a href="%sprivacidade.html">Politica de Privacidade</a></div>
<p style="margin-top:8px"><a href="https://headspabrasil.com" target="_blank" rel="noopener">headspabrasil.com</a></p></footer>
</body>
</html>""" % (ad("4444444444", "display:block", extra=' data-full-width-responsive="true"'), base, base, base, base)


SIDEBAR = """<aside class="sidebar">
<div class="sidebar-ad">%s</div>
<div class="sidebar-widget"><h3>Categorias</h3><ul>%s</ul></div>
<div class="sidebar-widget"><h3>Sobre o blog</h3><ul>
<li>Artigos originais sobre Head Spa, saude do couro cabeludo e bem-estar, escritos em Portugues do Brasil.</li>
<li><a href="sobre.html">Conheca o projeto</a></li>
<li><a href="https://headspabrasil.com" target="_blank" rel="noopener">headspabrasil.com</a></li>
</ul></div>
</aside>""" % (
    ad("2222222222", "display:block;width:300px;min-height:600px"),
    "".join('<li><a href="index.html?cat=%s">%s</a></li>' % (c, LABELS[c]) for c in LABELS),
)

# ---------- index ----------
cards = []
for i, a in enumerate(ARTICLES):
    url = "artigos/%s.html" % a["slug"]
    cards.append(
        '<article class="card%s" data-cat="%s">'
        '<div class="card-img">%s</div>'
        '<div class="card-body"><div class="card-category">%s</div>'
        '<h2 class="card-title"><a href="%s">%s</a></h2>'
        '<p class="card-excerpt">%s</p>'
        '<div class="card-meta"><span>%s</span><a class="read-more" href="%s">Ler artigo</a></div>'
        '</div></article>' % (
            " featured" if i == 0 else "", a["cat"], EMOJIS[a["cat"]], LABELS[a["cat"]], url, a["title"], a["excerpt"], a["date"], url)
    )
    if (i + 1) % 3 == 0 and i < len(ARTICLES) - 1:
        cards.append('<div style="grid-column:1/-1">%s</div>' % ad("3333333333", "display:block;min-height:250px"))

catbtns = '<button class="cat-btn active" data-c="todos">Todos</button>' + "".join(
    '<button class="cat-btn" data-c="%s">%s</button>' % (c, LABELS[c]) for c in LABELS)

index = head("Blog Head Spa Brasil - Saude do couro cabeludo e bem-estar",
             "Artigos originais sobre Head Spa, saude do couro cabeludo, tecnicas de massagem capilar e bem-estar. Conteudo em Portugues do Brasil.")
index += '<div style="background:#fff;padding:12px 0;text-align:center;border-bottom:1px solid #e2ddd6">%s</div>' % ad(
    "1111111111", "display:block", extra=' data-full-width-responsive="true"')
index += """<div class="hero"><h1>Blog Head Spa Brasil</h1>
<p>Artigos originais sobre saude do couro cabeludo, tecnicas e bem-estar</p>
<div class="last-updated" id="last-updated"></div></div>
<div class="categories" id="cats">%s</div>
<div class="page-body">
<main><div class="section-label">Artigos Recentes</div><div class="articles-grid">%s</div></main>
%s
</div>
<script>
document.getElementById('last-updated').textContent='Atualizado em: '+new Date().toLocaleDateString('pt-BR',{day:'2-digit',month:'long',year:'numeric'});
function applyCat(c){
  document.querySelectorAll('.cat-btn').forEach(function(b){b.classList.toggle('active',b.dataset.c===c);});
  document.querySelectorAll('.card[data-cat]').forEach(function(el){
    el.style.display=(c==='todos'||el.dataset.cat===c)?'':'none';
  });
}
document.querySelectorAll('.cat-btn').forEach(function(b){
  b.addEventListener('click',function(){applyCat(b.dataset.c);});
});
var q=new URLSearchParams(location.search).get('cat');
if(q)applyCat(q);
</script>
""" % (catbtns, "".join(cards), SIDEBAR)
index += footer()
open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(index)

# ---------- artigos ----------
for i, a in enumerate(ARTICLES):
    rel = [x for x in ARTICLES if x["slug"] != a["slug"]][:3]
    srcs = "".join('<li><a href="%s" target="_blank" rel="noopener nofollow">%s</a></li>' % (u, t) for t, u in a["sources"])
    relhtml = "".join('<li><a href="%s.html">%s</a></li>' % (r["slug"], r["title"]) for r in rel)
    p = head(a["title"] + " | Head Spa Brasil", a["excerpt"], base="../")
    p += '<div style="background:#fff;padding:12px 0;text-align:center;border-bottom:1px solid #e2ddd6">%s</div>' % ad(
        "1111111111", "display:block", extra=' data-full-width-responsive="true"')
    p += """<div class="page-body">
<main>
<a class="back-link" href="../index.html">&larr; Voltar para o blog</a>
<article class="post">
<h1 style="font-family:'Playfair Display',serif;font-size:2rem;line-height:1.25;margin-bottom:18px">%s</h1>
<div class="post-meta">%s &middot; %s</div>
%s
<div style="margin:36px 0">%s</div>
<div class="post-sources"><h3>Fontes consultadas</h3><ul>%s</ul>
<p style="margin-top:16px;font-size:12.5px;color:#888">Este conteudo tem caracter informativo e nao substitui avaliacao medica ou dermatologica.</p></div>
</article>
</main>
<aside class="sidebar">
<div class="sidebar-ad">%s</div>
<div class="sidebar-widget"><h3>Leia tambem</h3><ul>%s</ul></div>
</aside>
</div>
""" % (a["title"], LABELS[a["cat"]], a["date"], a["body"], ad("3333333333", "display:block;min-height:250px"), srcs,
       ad("2222222222", "display:block;width:300px;min-height:600px"), relhtml)
    p += footer(base="../")
    open(os.path.join(OUT, "artigos", a["slug"] + ".html"), "w", encoding="utf-8").write(p)

# ---------- paginas estaticas ----------
def static_page(fname, title, desc, h1, body):
    s = head(title, desc)
    s += '<div class="hero"><h1>%s</h1></div><div class="page-body"><main><div class="static-page">%s</div></main>%s</div>' % (
        h1, body, SIDEBAR)
    s += footer()
    open(os.path.join(OUT, fname), "w", encoding="utf-8").write(s)


PRIV = """
<p><strong>Ultima atualizacao:</strong> 29 de julho de 2026</p>
<p>Esta Politica de Privacidade descreve como o Blog Head Spa Brasil trata informacoes dos visitantes deste site. Ao navegar por estas paginas, voce concorda com as praticas descritas abaixo.</p>

<h2>1. Informacoes que coletamos</h2>
<p>Este site nao exige cadastro e nao coleta diretamente nome, e-mail, telefone ou dados de pagamento. As informacoes obtidas de forma automatica sao as tipicas de navegacao na internet, como:</p>
<ul>
<li>endereco IP e localizacao aproximada;</li>
<li>tipo de navegador, dispositivo e sistema operacional;</li>
<li>paginas visitadas, tempo de permanencia e site de origem;</li>
<li>data e hora do acesso.</li>
</ul>

<h2>2. Cookies</h2>
<p>Cookies sao pequenos arquivos de texto gravados no seu navegador. Utilizamos cookies para entender como o site e usado e para permitir a exibicao de anuncios. Voce pode bloquear ou apagar cookies nas configuracoes do seu navegador; algumas funcionalidades podem deixar de operar corretamente.</p>

<h2>3. Google AdSense e cookies de terceiros</h2>
<p>Este site exibe anuncios por meio do Google AdSense. A respeito disso, informamos que:</p>
<ul>
<li>o Google, como fornecedor terceirizado, utiliza cookies para exibir anuncios neste site;</li>
<li>o uso do cookie DART pelo Google permite exibir anuncios com base nas visitas dos usuarios a este e a outros sites da internet;</li>
<li>terceiros que anunciam neste site tambem podem utilizar cookies e tecnologias semelhantes para coletar informacoes sobre sua atividade;</li>
<li>voce pode desativar a publicidade personalizada visitando as <a href="https://www.google.com/settings/ads" target="_blank" rel="noopener">Configuracoes de anuncios do Google</a>;</li>
<li>para saber mais, consulte a <a href="https://policies.google.com/technologies/ads" target="_blank" rel="noopener">politica de privacidade e termos do Google para anuncios</a>.</li>
</ul>

<h2>4. Como usamos as informacoes</h2>
<p>Os dados de navegacao sao usados exclusivamente para medir audiencia, entender quais conteudos sao mais uteis, melhorar a experiencia de leitura e viabilizar a exibicao de anuncios que sustentam o site. Nao vendemos, alugamos nem compartilhamos dados de visitantes com terceiros para finalidades alheias a estas.</p>

<h2>5. Links para outros sites</h2>
<p>Nossos artigos citam fontes externas. Nao temos controle sobre o conteudo ou as praticas de privacidade desses sites e recomendamos a leitura das respectivas politicas antes de fornecer qualquer informacao a eles.</p>

<h2>6. Seus direitos (LGPD)</h2>
<p>Nos termos da Lei Geral de Protecao de Dados (Lei 13.709/2018), voce pode solicitar confirmacao de tratamento, acesso, correcao, anonimizacao, portabilidade ou eliminacao de dados pessoais, bem como revogar consentimento. Para exercer esses direitos, utilize a nossa <a href="contato.html">pagina de contato</a>.</p>

<h2>7. Publico infantil</h2>
<p>Este site nao se destina a criancas menores de 13 anos e nao coletamos intencionalmente dados desse publico. Caso identifique tal situacao, entre em contato para que possamos remover as informacoes.</p>

<h2>8. Conteudo informativo</h2>
<p>Os textos publicados aqui tratam de estetica, cuidados capilares e bem-estar com finalidade informativa. Nao constituem orientacao medica, diagnostico ou tratamento. Procure um dermatologista ou profissional de saude qualificado para avaliar o seu caso.</p>

<h2>9. Alteracoes desta politica</h2>
<p>Podemos atualizar este documento a qualquer momento. A data no topo da pagina indica a ultima revisao. Recomendamos releitura periodica.</p>

<h2>10. Contato</h2>
<p>Duvidas sobre esta politica podem ser enviadas pela <a href="contato.html">pagina de contato</a>.</p>
"""

SOBRE = """
<p>O <strong>Blog Head Spa Brasil</strong> e um projeto editorial dedicado a um assunto especifico e frequentemente negligenciado: a saude do couro cabeludo.</p>

<h2>Por que este blog existe</h2>
<p>O mercado brasileiro de beleza produz muito conteudo sobre o fio de cabelo — hidratacao, coloracao, finalizacao — e muito pouco sobre a pele de onde esse fio nasce. Quando o Head Spa, tratamento de origem japonesa focado justamente no couro cabeludo, comecou a ganhar espaco no Brasil, percebemos que faltava informacao confiavel e em portugues sobre o tema.</p>
<p>Este blog nasceu para preencher essa lacuna: explicar o que o tratamento e, o que ele faz, o que ele nao faz e como identificar um servico bem executado.</p>

<h2>Como produzimos o conteudo</h2>
<p>Nossos artigos sao escritos originalmente em Portugues do Brasil. Partimos de pesquisa em fontes do setor, publicacoes especializadas e materiais tecnicos, e as fontes consultadas ficam sempre listadas ao final de cada texto para que o leitor possa verificar e aprofundar.</p>
<p>Adotamos duas regras editoriais que consideramos importantes. A primeira: quando a evidencia de um beneficio e fraca ou indireta, dizemos isso com clareza em vez de apresentar tudo com o mesmo grau de certeza. A segunda: deixamos explicito o limite entre cuidado estetico e questao medica — sempre que um sintoma pede dermatologista, o texto aponta isso.</p>

<h2>O que voce encontra aqui</h2>
<ul>
<li><strong>Saude Capilar</strong> — como o couro cabeludo funciona e o que de fato afeta a saude dele.</li>
<li><strong>Dicas</strong> — tecnicas, rotinas e passo a passo aplicaveis no dia a dia.</li>
<li><strong>Noticias</strong> — o que acontece no mercado de Head Spa e bem-estar no Brasil e no mundo.</li>
<li><strong>Produtos</strong> — equipamentos e insumos, com foco em criterios de avaliacao em vez de indicacao de marca.</li>
</ul>

<h2>Aviso importante</h2>
<p>Este e um veiculo de informacao, nao um servico de saude. Nenhum conteudo publicado aqui substitui consulta com dermatologista ou outro profissional habilitado. Queda de cabelo acentuada, feridas, dor ou descamacao persistente no couro cabeludo pedem avaliacao clinica.</p>

<h2>Transparencia</h2>
<p>O site e mantido com receita de publicidade exibida por meio do Google AdSense. Isso nao interfere na linha editorial: nao publicamos conteudo pago disfarcado de materia e nao recebemos para recomendar marcas especificas.</p>
<p>Para entender como tratamos dados de navegacao, consulte a <a href="privacidade.html">Politica de Privacidade</a>.</p>

<h2>Fale com a gente</h2>
<p>Sugestoes de tema, correcoes e duvidas sao bem-vindas pela <a href="contato.html">pagina de contato</a>.</p>
"""

CONTATO = """
<p>Queremos ouvir voce. Use os canais abaixo para falar com a equipe do Blog Head Spa Brasil.</p>

<h2>E-mail</h2>
<p>O canal principal de contato e o e-mail:</p>
<p style="font-size:17px"><strong><a href="mailto:contato@headspabrasil.com">contato@headspabrasil.com</a></strong></p>
<p>Respondemos em ate 5 dias uteis.</p>

<h2>Site institucional</h2>
<p>Informacoes sobre servicos e atendimento presencial estao em <a href="https://headspabrasil.com" target="_blank" rel="noopener">headspabrasil.com</a>.</p>

<h2>Sobre o que podemos falar</h2>
<ul>
<li><strong>Sugestoes de pauta</strong> — temas que voce gostaria de ver abordados.</li>
<li><strong>Correcoes</strong> — se encontrou um erro factual em algum artigo, avise. Corrigimos e registramos a correcao.</li>
<li><strong>Duvidas sobre privacidade e dados</strong> — solicitacoes previstas na LGPD, conforme a <a href="privacidade.html">Politica de Privacidade</a>.</li>
<li><strong>Imprensa e parcerias editoriais</strong>.</li>
</ul>

<h2>Sobre o que nao podemos falar</h2>
<p>Nao prestamos orientacao medica, diagnostico ou recomendacao de tratamento por e-mail. Nao conseguimos avaliar casos individuais de queda de cabelo, coceira, descamacao ou qualquer sintoma. Para isso, procure um dermatologista — e um conselho que damos com sinceridade, nao por formalidade.</p>

<h2>Publicidade</h2>
<p>Os anuncios exibidos neste site sao servidos automaticamente pelo Google AdSense. Nao negociamos espacos publicitarios diretamente. Se um anuncio especifico apresentar problema, voce pode reportar pelo proprio Google ou nos avisar por e-mail.</p>
"""

static_page("privacidade.html", "Politica de Privacidade | Head Spa Brasil",
            "Politica de Privacidade do Blog Head Spa Brasil: cookies, Google AdSense, LGPD e direitos do usuario.",
            "Politica de Privacidade", PRIV)
static_page("sobre.html", "Sobre o Blog | Head Spa Brasil",
            "Conheca o Blog Head Spa Brasil, nossa linha editorial e como produzimos conteudo sobre saude do couro cabeludo.",
            "Sobre o Blog", SOBRE)
static_page("contato.html", "Contato | Head Spa Brasil",
            "Fale com a equipe do Blog Head Spa Brasil: sugestoes de pauta, correcoes, imprensa e questoes de privacidade.",
            "Contato", CONTATO)

# ---------- ads.txt, robots, sitemap ----------
open(os.path.join(OUT, "ads.txt"), "w").write("google.com, pub-1513334089874704, DIRECT, f08c47fec0942fa0\n")

BASE = "https://valdineigilcimar-design.github.io/head-spa-blog/"
urls = ["", "sobre.html", "contato.html", "privacidade.html"] + ["artigos/%s.html" % a["slug"] for a in ARTICLES]
today = datetime.date.today().isoformat()
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
for u in urls:
    sm += "<url><loc>%s%s</loc><lastmod>%s</lastmod></url>\n" % (BASE, u, today)
sm += "</urlset>\n"
open(os.path.join(OUT, "sitemap.xml"), "w").write(sm)
open(os.path.join(OUT, "robots.txt"), "w").write("User-agent: *\nAllow: /\n\nSitemap: %ssitemap.xml\n" % BASE)

# ---------- relatorio ----------
import re
tot = 0
for a in ARTICLES:
    w = len(re.sub("<[^>]+>", " ", a["body"]).split())
    tot += w
    print("  %-45s %4d palavras" % (a["slug"][:45], w))
print("\nTotal de palavras nos artigos: %d" % tot)
print("Arquivos gerados:")
for root, _, files in os.walk(OUT):
    for f in sorted(files):
        p = os.path.join(root, f)
        print("  %-52s %6d bytes" % (os.path.relpath(p, OUT), os.path.getsize(p)))
