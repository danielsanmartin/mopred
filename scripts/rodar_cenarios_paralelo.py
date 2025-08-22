# scripts/rodar_cenarios_paralelo.py
import json, subprocess, sys, os
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing as mp

BASE_CONFIG = Path("configs/config.json")
PYTHON = "D:/Workspace/mopred/venv/Scripts/python.exe"

scales = [10_000, 50_000, 100_000]
prevalences = [0.01, 0.05]
seeds = [42, 1337, 2025]

def load_cfg():
    with BASE_CONFIG.open("r", encoding="utf-8") as f:
        return json.load(f)

def run_cenario(params):
    """Roda um único cenário (função para paralelismo)."""
    v, p, seed = params
    sid = f"V{v//1000}k_P{int(p*100)}_S{seed}"
    
    try:
        out_root = Path("runs") / sid
        pasta_csvs = out_root / "csvs"
        pasta_alertas = out_root / "alertas_gerados"
        pasta_cfg = out_root / "config"
        pasta_csvs.mkdir(parents=True, exist_ok=True)
        pasta_alertas.mkdir(parents=True, exist_ok=True)
        pasta_cfg.mkdir(parents=True, exist_ok=True)

        cfg = load_cfg()
        cfg["seed"] = seed
        cfg["total_veiculos"] = v
        cfg["percentual_veiculos_clonados"] = p
        cfg["pasta_csvs"] = str(pasta_csvs).replace("\\", "/")
        cfg["pasta_alertas"] = str(pasta_alertas).replace("\\", "/")
        cfg["csv_veiculos_path"] = str(pasta_csvs / "veiculos_gerados_com_clones.csv").replace("\\", "/")

        cfg_path = pasta_cfg / "config.json"
        with cfg_path.open("w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)

        print(f"🚀 [PID {os.getpid()}] Iniciando cenário {sid}")
        
        env = dict(**os.environ)
        env["MOPRED_CONFIG"] = str(cfg_path)
        cmd = [PYTHON, "main.py", "--config", str(cfg_path), "--steps", "1,2,3"]
        
        result = subprocess.run(cmd, check=True, env=env, 
                              capture_output=True, text=True)
        
        print(f"✅ [PID {os.getpid()}] Concluído cenário {sid}")
        return {"status": "sucesso", "cenario": sid, "pid": os.getpid()}
        
    except subprocess.CalledProcessError as e:
        # Capturar stdout e stderr para diagnóstico
        stdout_text = e.stdout if e.stdout else "N/A"
        stderr_text = e.stderr if e.stderr else "N/A" 
        
        print(f"❌ [PID {os.getpid()}] Erro no cenário {sid}")
        print(f"   Exit code: {e.returncode}")
        if stderr_text != "N/A":
            print(f"   STDERR: {stderr_text[-500:]}")  # últimas 500 chars
        
        return {
            "status": "erro", 
            "cenario": sid, 
            "exit_code": e.returncode,
            "stderr": stderr_text[-1000:] if stderr_text != "N/A" else "N/A",  # últimas 1000 chars
            "stdout": stdout_text[-1000:] if stdout_text != "N/A" else "N/A"
        }
    except Exception as e:
        print(f"💥 [PID {os.getpid()}] Falha inesperada no cenário {sid}: {e}")
        return {"status": "falha", "cenario": sid, "erro": str(e)}

def run_paralelo(max_workers=None):
    """Executa todos os cenários em paralelo."""
    # Gera lista de parâmetros (escala, prevalência, seed)
    cenarios = [(v, p, seed) for v in scales for p in prevalences for seed in seeds]
    
    if max_workers is None:
        # Usar até CPU_COUNT-1 ou máximo 6 processos (evita sobrecarga)
        max_workers = min(mp.cpu_count() - 1, 6, len(cenarios))
    
    print(f"🔥 Executando {len(cenarios)} cenários com {max_workers} processos paralelos...")
    
    resultados = []
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submete todos os cenários
        futures = {executor.submit(run_cenario, params): params for params in cenarios}
        
        # Coleta resultados conforme completam
        for future in as_completed(futures):
            params = futures[future]
            try:
                resultado = future.result()
                resultados.append(resultado)
                if resultado["status"] == "sucesso":
                    print(f"🎯 {resultado['cenario']} concluído!")
                else:
                    print(f"⚠️ {resultado['cenario']} falhou: {resultado.get('exit_code', resultado.get('erro', 'N/A'))}")
            except Exception as e:
                sid = f"V{params[0]//1000}k_P{int(params[1]*100)}_S{params[2]}"
                print(f"💀 Exceção não capturada no cenário {sid}: {e}")
                resultados.append({"status": "exceção", "cenario": sid, "erro": str(e)})
    
    # Relatório final
    sucessos = [r for r in resultados if r["status"] == "sucesso"]
    falhas = [r for r in resultados if r["status"] != "sucesso"]
    
    print(f"\n📊 RELATÓRIO FINAL:")
    print(f"   ✅ Sucessos: {len(sucessos)}/{len(cenarios)}")
    print(f"   ❌ Falhas: {len(falhas)}")
    
    if falhas:
        print(f"\n🔴 Cenários com falha:")
        for f in falhas:
            print(f"   • {f['cenario']}: exit_code={f.get('exit_code', 'N/A')}")
            if f.get('stderr') and f['stderr'] != "N/A":
                print(f"     STDERR: {f['stderr']}")
    
    return resultados

def test_single():
    """Testa um único cenário para debug."""
    print("🧪 Testando um cenário individual...")
    resultado = run_cenario((10_000, 0.01, 42))
    print(f"Resultado: {resultado}")
    return resultado

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Modo de teste: roda apenas um cenário com output detalhado
        test_single()
    else:
        # Ajuste max_workers conforme sua máquina (CPU/RAM)
        # Para 18 cenários: 4-6 processos é um bom equilíbrio
        resultados = run_paralelo(max_workers=4)