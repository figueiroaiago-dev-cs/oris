"""Guardas do empacotamento Docker e do cookie de sessao em producao (sem precisar do Docker)."""

import importlib
import re
from pathlib import Path


RAIZ = Path(__file__).resolve().parent.parent


def _carregar_config(monkeypatch, valor):
    import config

    if valor is None:
        monkeypatch.delenv("SESSION_COOKIE_SECURE", raising=False)
    else:
        monkeypatch.setenv("SESSION_COOKIE_SECURE", valor)
    return importlib.reload(config)


def test_cookie_secure_e_padrao_em_producao(monkeypatch):
    assert _carregar_config(monkeypatch, None).ProductionConfig.SESSION_COOKIE_SECURE is True
    assert _carregar_config(monkeypatch, "true").ProductionConfig.SESSION_COOKIE_SECURE is True
    assert _carregar_config(monkeypatch, "qualquer").ProductionConfig.SESSION_COOKIE_SECURE is True


def test_cookie_secure_so_desliga_com_false_explicito(monkeypatch):
    assert _carregar_config(monkeypatch, "false").ProductionConfig.SESSION_COOKIE_SECURE is False
    _carregar_config(monkeypatch, None)  # restaura o padrao para os demais testes


def test_compose_nao_expoe_o_banco_e_usa_mysql_8():
    texto = (RAIZ / "docker-compose.yml").read_text(encoding="utf-8")
    bloco_db = texto.split("  app:")[0]
    assert re.search(r"image:\s*mysql:8", bloco_db)
    assert "--log-bin-trust-function-creators=1" in bloco_db
    assert "ports:" not in bloco_db, "o banco nao deve ser publicado no computador"
    assert "FLASK_ENV: production" in texto
    assert '"127.0.0.1:${ORIS_PORT:-5000}:5000"' in texto


def test_dockerfile_nao_roda_como_root_e_dockerignore_protege_segredos():
    dockerfile = (RAIZ / "Dockerfile").read_text(encoding="utf-8")
    assert re.search(r"^USER\s+(?!root)\S+", dockerfile, re.MULTILINE)
    ignorados = (RAIZ / ".dockerignore").read_text(encoding="utf-8").split()
    assert ".env" in ignorados and ".git" in ignorados


def test_senhas_do_compose_sao_sobrescreviveis_por_variavel():
    texto = (RAIZ / "docker-compose.yml").read_text(encoding="utf-8")
    senhas = re.findall(r"PASSWORD:\s*(\S+)", texto)
    assert senhas and all(x.startswith("${") for x in senhas)
