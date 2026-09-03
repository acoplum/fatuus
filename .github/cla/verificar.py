#!/usr/bin/env python3
"""Verificação de CLA — sem depender de ação de terceiro.

Duas funções, escolhidas pelo argumento:

  verificar <login>   sai 1 se o login não assinou
  registrar <login> <url-do-comentario>

O `AGENTS.md` do HQ lista publicar repo sem CLA ativo entre os *nunca*:
um pull request externo aceito sem assinatura torna aquele código
impossível de sublicenciar, e corrigir depois exige achar a pessoa.
"""

from __future__ import annotations

import json
import pathlib
import sys
from datetime import datetime, timezone

ARQUIVO = pathlib.Path(__file__).parent / "assinaturas.json"


def _ler() -> dict:
    return json.loads(ARQUIVO.read_text(encoding="utf-8"))


def assinou(login: str) -> bool:
    return any(a["login"].lower() == login.lower() for a in _ler()["assinaturas"])


def registrar(login: str, referencia: str) -> None:
    d = _ler()
    if assinou(login):
        print(f"{login} já constava")
        return
    d["assinaturas"].append({
        "login": login,
        "em": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "referencia": referencia,
        "versao_cla": d["versao"],
    })
    ARQUIVO.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{login} registrado")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise SystemExit("uso: verificar.py <verificar|registrar> <login> [referencia]")
    acao, login = sys.argv[1], sys.argv[2]
    if acao == "verificar":
        if assinou(login):
            print(f"✓ {login} assinou o CLA")
            raise SystemExit(0)
        print(f"✗ {login} ainda não assinou o CLA")
        raise SystemExit(1)
    if acao == "registrar":
        registrar(login, sys.argv[3] if len(sys.argv) > 3 else "")
        raise SystemExit(0)
    raise SystemExit(f"ação desconhecida: {acao}")
