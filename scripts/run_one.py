"""
Execute um único cenário de ponta a ponta para validar as saídas por cenário.

Uso (PowerShell):
  python scripts/run_one.py --v 5000 --p 0.02 --seed 42
"""
from __future__ import annotations
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

BASE_CONFIG = Path("configs/config.json")


def load_cfg() -> dict:
    with BASE_CONFIG.open("r", encoding="utf-8") as f:
        return json.load(f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--v", type=int, required=True, help="Total de veículos")
    ap.add_argument("--p", type=float, required=True, help="Percentual de clones, ex.: 0.02")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--steps", type=str, default="1,2,3", help="Etapas para rodar, ex.: 1,2,3")
    args = ap.parse_args()

    sid = f"V{args.v//1000}k_P{int(args.p*100)}_S{args.seed}"
    out_root = Path("runs") / (sid + "_TEST")
    pasta_csvs = out_root / "csvs"
    pasta_alertas = out_root / "alertas_gerados"
    pasta_cfg = out_root / "config"
    pasta_csvs.mkdir(parents=True, exist_ok=True)
    pasta_alertas.mkdir(parents=True, exist_ok=True)
    pasta_cfg.mkdir(parents=True, exist_ok=True)

    cfg = load_cfg()
    cfg["seed"] = args.seed
    cfg["total_veiculos"] = args.v
    cfg["percentual_veiculos_clonados"] = args.p
    cfg["pasta_csvs"] = str(pasta_csvs).replace("\\", "/")
    cfg["pasta_alertas"] = str(pasta_alertas).replace("\\", "/")
    cfg["csv_veiculos_path"] = str(pasta_csvs / "veiculos_gerados_com_clones.csv").replace("\\", "/")

    cfg_path = pasta_cfg / "config.json"
    with cfg_path.open("w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

    env = dict(**os.environ)
    env["MOPRED_CONFIG"] = str(cfg_path)

    cmd = [sys.executable, "main.py", "--config", str(cfg_path), "--steps", args.steps]
    print(f"Rodando {sid} (steps={args.steps})...")
    subprocess.run(cmd, check=True, env=env)


if __name__ == "__main__":
    main()
