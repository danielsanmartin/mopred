# scripts/rodar_cenarios.py
import json, subprocess, sys, os
from pathlib import Path

BASE_CONFIG = Path("configs/config.json")
PYTHON = sys.executable  # usa o Python do seu venv

scales = [10_000, 50_000, 100_000]
prevalences = [0.01, 0.05]
seeds = [42, 1337, 2025]  # se quiser reduzir custo: use apenas [42]

def load_cfg():
    with BASE_CONFIG.open("r", encoding="utf-8") as f:
        return json.load(f)

def run():
    for v in scales:
        for p in prevalences:
            for seed in seeds:
                sid = f"V{v//1000}k_P{int(p*100)}_S{seed}"
                out_root = Path("runs") / sid
                pasta_csvs = out_root / "csvs"
                pasta_alertas = out_root / "alertas_gerados"
                pasta_cfg = out_root / "config"
                pasta_csvs.mkdir(parents=True, exist_ok=True)
                pasta_alertas.mkdir(parents=True, exist_ok=True)
                pasta_cfg.mkdir(parents=True, exist_ok=True)

                cfg = load_cfg()
                # Parâmetros do cenário
                cfg["seed"] = seed
                cfg["total_veiculos"] = v
                cfg["percentual_veiculos_clonados"] = p
                # Saídas isoladas por cenário
                cfg["pasta_csvs"] = str(pasta_csvs).replace("\\", "/")
                cfg["pasta_alertas"] = str(pasta_alertas).replace("\\", "/")
                # Apontar caminho do CSV de veículos para o simulador
                cfg["csv_veiculos_path"] = str(pasta_csvs / "veiculos_gerados_com_clones.csv").replace("\\", "/")

                cfg_path = pasta_cfg / "config.json"
                with cfg_path.open("w", encoding="utf-8") as f:
                    json.dump(cfg, f, ensure_ascii=False, indent=2)

                print(f"\n=== Rodando cenário {sid} ===")
                # Propagar o caminho da config via variável de ambiente para subprocessos
                env = dict(**os.environ)
                env["MOPRED_CONFIG"] = str(cfg_path)
                cmd = [PYTHON, "main.py", "--config", str(cfg_path), "--steps", "1,2,3"]
                subprocess.run(cmd, check=True, env=env)

if __name__ == "__main__":
    run()