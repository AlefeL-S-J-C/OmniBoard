import pytest
import httpx
from src.main import app

BASE = "http://testserver"

@pytest.mark.skip(reason="requires running Postgres/Redis")
@pytest.mark.asyncio
async def test_full_match_flow():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url=BASE) as ac:
        # register two users
        r1 = await ac.post("/api/auth/register", json={"username":"alice","email":"a@a.com","password":"secret123"})
        r2 = await ac.post("/api/auth/register", json={"username":"bob","email":"b@b.com","password":"secret123"})
        assert r1.status_code == 200
        assert r2.status_code == 200
        t1 = r1.json()["token"]
        t2 = r2.json()["token"]

        # both join queue for chess (PvP)
        async def join(tok):
            return await ac.post("/api/matchmaking/join",
                                 json={"game_type":"chess","with_ai":False},
                                 headers={"Authorization": f"Bearer {tok}"})
        m1 = await join(t1)
        m2 = await join(t2)
        matched = m1.json() if m1.json().get("matched") else m2.json()
        assert matched["matched"]
        match_id = matched["match_id"]

        # open WS for both players
        ws1 = await ac.websocket_connect(f"/ws/{match_id}/{t1}?game_type=chess&with_ai=false")
        ws2 = await ac.websocket_connect(f"/ws/{match_id}/{t2}?game_type=chess&with_ai=false")

        # receive initial state
        init1 = await ws1.receive_json()
        init2 = await ws2.receive_json()
        assert init1["evento"] == "conexao_estabelecida"
        assert init2["evento"] == "conexao_estabelecida"

        # Alice (white) plays e2e4
        await ws1.send_json({"action":"move","payload":{"from":"e2","to":"e4"}})
        resp1 = await ws1.receive_json()
        assert resp1["evento"] == "movimento_confirmado"

        # Bob receives same
        resp2 = await ws2.receive_json()
        assert resp2["evento"] == "movimento_confirmado"

        # clean close
        await ws1.close()
        await ws2.close()