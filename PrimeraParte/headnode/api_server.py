from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess, os, json, asyncio

app = FastAPI()
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

SLICES_DIR = os.path.join(BASE_PATH, "slices")
LOGS_DIR = os.path.join(BASE_PATH, "logs")
STATE_FILE = os.path.join(BASE_PATH, "state.json")
WORKERS = ["worker1", "worker2", "worker3"]

# Cola de despliegues
deploy_queue = asyncio.Queue()

# === MODELOS DE DATOS ===

class SliceRequest(BaseModel):
    name: str

class LoginRequest(BaseModel):
    user: str
    password: str

# === AUTENTICACIÓN ===

@app.post("/login")
def login(req: LoginRequest):
    with open(os.path.join(BASE_PATH, "usuarios.json")) as f:
        usuarios = json.load(f)
    if req.user in usuarios and usuarios[req.user] == req.password:
        return {"status": "ok"}
    raise HTTPException(status_code=401, detail="Login inválido")

# === UTILIDAD PARA LLAMAR SCRIPTS ===

def run_script(script, args):
    script_path = os.path.join(BASE_PATH, "scripts", script)
    subprocess.run(["python3", script_path] + args)

# === DEPLOY CON COLA ===

@app.on_event("startup")
async def start_deploy_worker():
    async def worker():
        while True:
            topo, slice_name = await deploy_queue.get()
            print(f"[→] Desplegando slice: {slice_name} ({topo})")
            run_script("deploy_slice.py", ["--topo", topo, "--name", slice_name])
            print(f"[✓] Slice {slice_name} desplegado")
            deploy_queue.task_done()
    asyncio.create_task(worker())

@app.post("/deploy/{topo}")
async def deploy(topo: str, req: SliceRequest):
    if topo not in ["single", "lineal", "anillo"]:
        raise HTTPException(status_code=400, detail="Topología no válida")
    await deploy_queue.put((topo, req.name))
    return {"status": "enqueued", "topology": topo, "name": req.name}

# === ELIMINAR SLICE ===

@app.delete("/slice/{name}")
def delete_slice(name: str):
    run_script("delete_slice.py", ["--name", name])
    return {"status": "deleted", "name": name}

# === LISTAR SLICES ACTIVOS ===

@app.get("/slices")
def listar_slices():
    if not os.path.exists(SLICES_DIR):
        return []
    return [f.replace(".json", "") for f in os.listdir(SLICES_DIR) if f.endswith(".json")]

# === ESTADO DE VM POR SLICE ===

@app.get("/status/{name}")
def estado_slice(name: str):
    slice_path = os.path.join(SLICES_DIR, f"{name}.json")
    if not os.path.exists(slice_path):
        raise HTTPException(status_code=404, detail="Slice no encontrado")
    with open(slice_path) as f:
        data = json.load(f)
    vms = data.get("vms", {})
    resultados = {}
    for vm_name, vm_data in vms.items():
        worker = vm_data.get("worker", "")
        cmd = f"ssh {worker} pgrep -f 'qemu-system.*{vm_name}'"
        result = os.system(cmd + " > /dev/null 2>&1")
        resultados[vm_name] = "activo" if result == 0 else "inactivo"
    return resultados

# === RECURSOS POR WORKER ===

@app.get("/resources")
def recursos_workers():
    recursos = {}
    for w in WORKERS:
        try:
            output = subprocess.check_output(f"ssh {w} free -m | grep Mem", shell=True).decode()
            partes = output.split()
            recursos[w] = {
                "total_MB": partes[1],
                "usado_MB": partes[2],
                "libre_MB": partes[3]
            }
        except:
            recursos[w] = {"error": "No se pudo obtener info"}
    return recursos

# === LISTAR VMs POR WORKER ===

@app.get("/vms")
def listar_vms_workers():
    resultado = {}
    for w in WORKERS:
        try:
            cmd = f"ssh {w} ps aux | grep qemu-system | grep -v grep"
            output = subprocess.check_output(cmd, shell=True).decode()
            vms = []
            for line in output.strip().split("\n"):
                if not line.strip():
                    continue
                vm_name = "desconocido"
                if "ifname=tap-" in line:
                    vm_name = line.split("ifname=tap-")[-1].split(",")[0]
                vms.append(vm_name)
            resultado[w] = vms or ["(sin VMs)"]
        except:
            resultado[w] = ["(error al conectar)"]
    return resultado

# === VER LOGS DE SLICE ===

@app.get("/logs/{name}")
def ver_logs(name: str):
    log_path = os.path.join(LOGS_DIR, f"{name}.log")
    if not os.path.exists(log_path):
        raise HTTPException(status_code=404, detail="Log no encontrado")
    with open(log_path) as f:
        contenido = f.read()
    return {"log": contenido}
