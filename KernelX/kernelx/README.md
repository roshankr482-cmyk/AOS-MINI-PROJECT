# KernelX – Powering Smarter Disk Scheduling

An Advanced Operating Systems mini project. Feed in a queue of disk requests and **KernelX** replays the
read/write head's journey for **FCFS, SSTF, SCAN, C-SCAN, LOOK and C-LOOK**, then ranks all six so you can see
which one travels the fewest cylinders.

All six algorithms are written in **C11** (`backend/algorithms.c`). A tiny Python server loads the C code as a
shared library and the browser UI draws the result. **No pip / npm install needed.**

## Windows par chalane ke steps
1. Python install karo (agar nahi hai): https://www.python.org/downloads/ → installer mein **"Add python.exe to PATH"** tick karo.
2. Zip ko **Extract All** karo (zip ke andar se mat chalao), e.g. `C:\kernelx`.
3. Folder kholo → **`run.bat` pe double-click** karo.
4. Browser khud khulega: **http://localhost:8000** . Band karne ke liye CMD window mein `Ctrl+C`.

C compiler ke bina bhi chalta hai (Python engine same algorithms use karta hai, results C jaise hi).
Asli C engine ke liye MinGW-w64 gcc install karo (`winget install -e --id BrechtSanders.WinLibs.POSIX.UCRT`),
naya CMD kholo aur `run.bat` chalao. Top-right badge mein "C (native)" dikhega.

```bat
run.bat -p 8080                  :: different port
run.bat --host 0.0.0.0           :: LAN pe share
run.bat --no-browser             :: browser auto-open na ho
run.bat cli                      :: terminal menu (gcc chahiye)
run.bat cli --demo               :: textbook example
```

## Linux / Kali
```bash
sudo apt update && sudo apt install -y build-essential python3   # one time
cd kernelx && chmod +x run.sh
./run.sh                 # builds C, runs tests, opens http://localhost:8000
./run.sh -p 8080         # different port
./run.sh cli --demo      # terminal version
./run.sh cli -a scan -h 53 98 183 37 122 14 124 65 67
cd backend && make test  # self-test only
```

## What is in the UI
- **Control Deck** (left): request queue, strategy, head position, sweep direction, cylinder range, ms per cylinder.
- **Head trace** (dark panel): line graph of head position at every step, with Play / Pause / Back / Next / Restart and a speed slider.
- **Algorithm arena**: all six algorithms on the same queue as bars, winner highlighted, % saved vs FCFS. Click a bar to replay that algorithm.
- Keyboard: ← → step, space play/pause, Enter to launch.

## Project layout
```
kernelx/
├── run.sh / run.bat / build.bat   launchers
├── server.py                      Python stdlib server, JSON API -> C library (ctypes)
├── pyengine.py                    pure-Python fallback (Windows without gcc)
├── backend/
│   ├── algorithms.c/.h            the 6 scheduling algorithms
│   ├── wasm_api.c                 input validation + JSON output (kernelx_run / kernelx_free)
│   ├── main.c                     CLI (menu + ASCII head-movement graph)
│   ├── test_algorithms.c          unit tests (textbook values)
│   └── Makefile                   make / make test / make wasm (optional)
└── frontend/index.html            UI
```

## Conventions
SCAN / C-SCAN travel to the disk edge; LOOK / C-LOOK stop at the last request. C-SCAN / C-LOOK return jumps are
counted in total movement. Duplicate requests are kept (0-cost seeks).

Textbook check (head 53, range 0–199, moving up, queue 98 183 37 122 14 124 65 67):
FCFS 640 · SSTF 236 · SCAN 331 · C-SCAN 382 · LOOK 299 · C-LOOK 322.

## Optional: WebAssembly mode
With Emscripten installed: `cd backend && make wasm`, then serve `frontend/` with any static server.
The UI falls back to WASM automatically when the Python API is not available.

## Troubleshooting
- `Address already in use` → run with another port (`-p 8080`).
- `Permission denied: ./run.sh` → `chmod +x run.sh`.
- `gcc: command not found` → `sudo apt install build-essential`.
- `python is not recognized` (Windows) → add Python to PATH and open a fresh CMD.
