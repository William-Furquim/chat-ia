import pytest
from fastapi.testclient import TestClient

from app.core.exceptions import ModeloIndisponivel
from app.llm.provider import LLMProvider, get_provider


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "teste.db"))
    monkeypatch.setenv("LLM_PROVIDER", "simulado")
    from app.main import app

    app.dependency_overrides.clear()
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def autenticar(client, username="ana", senha="segredo123"):
    client.post("/auth/registrar", json={"username": username, "senha": senha})
    r = client.post("/auth/login", data={"username": username, "password": senha})
    assert r.status_code == 200
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_health_publico(client):
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["provedor"] == "simulado"


def test_rotas_protegidas_exigem_token(client):
    assert client.get("/conversas").status_code == 401
    assert client.post("/conversas", json={}).status_code == 401
    assert client.get("/conversas/1").status_code == 401
    assert client.post("/conversas/1/mensagens", json={"conteudo": "oi"}).status_code == 401
    assert client.get("/conversas", headers={"Authorization": "Bearer lixo"}).status_code == 401


def test_login_invalido_e_usuario_duplicado(client):
    autenticar(client)
    assert client.post("/auth/login", data={"username": "ana", "password": "errada"}).status_code == 401
    assert client.post("/auth/registrar", json={"username": "ana", "senha": "outra123"}).status_code == 409
    assert client.post("/auth/registrar", json={"username": "x", "senha": "123"}).status_code == 422


def test_senha_nao_fica_em_texto_puro(client, tmp_path):
    import sqlite3

    autenticar(client, senha="segredo123")
    h = sqlite3.connect(tmp_path / "teste.db").execute("SELECT senha_hash FROM usuarios").fetchone()[0]
    assert "segredo123" not in h and h.startswith("pbkdf2_sha256$")


def test_fluxo_completo_de_conversa(client):
    h = autenticar(client)
    c = client.post("/conversas", json={}, headers=h)
    assert c.status_code == 201 and c.json()["titulo"] == "Nova conversa"
    cid = c.json()["id"]

    r = client.post(f"/conversas/{cid}/mensagens", json={"conteudo": "Me explique o que é uma API REST"}, headers=h)
    assert r.status_code == 201
    corpo = r.json()
    assert corpo["conversa_id"] == cid
    assert corpo["mensagem_usuario"]["papel"] == "user"
    assert corpo["resposta"]["papel"] == "assistant"
    assert corpo["modelo"] == "simulado"

    detalhe = client.get(f"/conversas/{cid}", headers=h).json()
    assert [m["papel"] for m in detalhe["mensagens"]] == ["user", "assistant"]
    assert detalhe["titulo"].startswith("Me explique")
    assert len(client.get("/conversas", headers=h).json()) == 1


def test_validacao_e_404(client):
    h = autenticar(client)
    cid = client.post("/conversas", json={}, headers=h).json()["id"]
    assert client.post(f"/conversas/{cid}/mensagens", json={"conteudo": ""}, headers=h).status_code == 422
    assert client.post(f"/conversas/{cid}/mensagens", json={}, headers=h).status_code == 422
    assert client.get("/conversas/9999", headers=h).status_code == 404
    assert client.post("/conversas/9999/mensagens", json={"conteudo": "oi"}, headers=h).status_code == 404


def test_isolamento_entre_usuarios(client):
    ha = autenticar(client, "ana")
    hb = autenticar(client, "beto")
    cid = client.post("/conversas", json={}, headers=ha).json()["id"]
    assert client.get(f"/conversas/{cid}", headers=hb).status_code == 404
    assert client.post(f"/conversas/{cid}/mensagens", json={"conteudo": "oi"}, headers=hb).status_code == 404
    assert client.get("/conversas", headers=hb).json() == []


def test_503_quando_modelo_indisponivel_nao_grava_nada(client):
    from app.main import app

    class Quebrado(LLMProvider):
        nome = "quebrado"

        def responder(self, historico):
            raise ModeloIndisponivel("Modelo fora do ar.")

    h = autenticar(client)
    cid = client.post("/conversas", json={}, headers=h).json()["id"]
    app.dependency_overrides[get_provider] = Quebrado
    r = client.post(f"/conversas/{cid}/mensagens", json={"conteudo": "oi"}, headers=h)
    assert r.status_code == 503 and r.json()["detail"] == "Modelo fora do ar."
    app.dependency_overrides.clear()
    assert client.get(f"/conversas/{cid}", headers=h).json()["mensagens"] == []


def test_persistencia_apos_reiniciar_api(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "persist.db"))
    from app.main import app

    with TestClient(app) as c1:
        h = autenticar(c1)
        cid = c1.post("/conversas", json={}, headers=h).json()["id"]
        c1.post(f"/conversas/{cid}/mensagens", json={"conteudo": "fastapi"}, headers=h)
    with TestClient(app) as c2:  # "reinício": novo ciclo de vida da aplicação
        d = c2.get(f"/conversas/{cid}", headers=h).json()
        assert len(d["mensagens"]) == 2
