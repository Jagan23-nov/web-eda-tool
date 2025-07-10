from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import subprocess
import os
import uuid
import shutil
import pathlib

app = FastAPI()

# Create results dir if not exists
RESULTS_DIR = "backend/results"
os.makedirs(RESULTS_DIR, exist_ok=True)

# Mount frontend and results directories
app.mount("/static", StaticFiles(directory="frontend"), name="static")
app.mount("/results", StaticFiles(directory=RESULTS_DIR), name="results")

@app.get("/")
def serve_index():
    return FileResponse("frontend/index.html")

# Paths
COMPILED_BINARY = "/tmp/a.out"
VCD_SOURCE = "/tmp/dump.vcd"
VCD_TARGET = os.path.join(RESULTS_DIR, "dump.vcd")

@app.post("/compile")
async def compile_hdl(request: Request):
    data = await request.json()
    verilog_code = data.get("design", "")
    testbench_code = data.get("testbench", "")

    if not verilog_code.strip() or not testbench_code.strip():
        return JSONResponse(status_code=400, content={"error": "Missing Verilog or testbench code"})

    design_path = f"/tmp/design_{uuid.uuid4().hex}.v"
    tb_path = f"/tmp/testbench_{uuid.uuid4().hex}.v"

    with open(design_path, "w") as f:
        f.write(verilog_code)
    with open(tb_path, "w") as f:
        f.write(testbench_code)

    try:
        subprocess.run(["iverilog", "-o", COMPILED_BINARY, design_path, tb_path], check=True)
        return {"output": "Compilation successful."}
    except subprocess.CalledProcessError as e:
        return JSONResponse(status_code=500, content={"error": f"Compilation error:\n{e.stderr if e.stderr else str(e)}"})

@app.get("/run")
def run_sim():
    if not os.path.exists(COMPILED_BINARY):
        return JSONResponse(status_code=404, content={"error": "Please compile the design first."})

    try:
        result = subprocess.run([COMPILED_BINARY], capture_output=True, text=True)

        # Move VCD to results folder
        if os.path.exists(VCD_SOURCE):
            shutil.copy(VCD_SOURCE, VCD_TARGET)
            print(f"✅ Copied VCD to: {VCD_TARGET}")
        else:
            print("❌ VCD file not found at:", VCD_SOURCE)

        return {"output": result.stdout or result.stderr}
    except subprocess.CalledProcessError as e:
        return JSONResponse(status_code=500, content={"error": f"Simulation error:\n{e.stderr if e.stderr else str(e)}"})

@app.get("/waveform")
def serve_waveform():
    print(f"🔍 Looking for VCD at: {pathlib.Path(VCD_TARGET).absolute()}")
    if os.path.exists(VCD_TARGET):
        return {"vcd_url": "/results/dump.vcd"}
    else:
        return JSONResponse(status_code=404, content={"error": "Waveform not generated yet."})
