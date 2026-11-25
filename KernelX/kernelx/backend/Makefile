# Works on Linux/macOS (gcc) and Windows (MinGW-w64 / MSYS2: mingw32-make).
# On Windows you can also just run build.bat from the project folder.
CC     ?= gcc
CFLAGS  = -std=c11 -Wall -Wextra -O2 -D_DEFAULT_SOURCE
SRC     = algorithms.c wasm_api.c

ifeq ($(OS),Windows_NT)
  EXE = .exe
  LIB = kernelx.dll
  PIC =
else
  EXE =
  LIB = libkernelx.so
  PIC = -fPIC
endif

all: kernelx_cli$(EXE) $(LIB)

kernelx_cli$(EXE): $(SRC) main.c
	$(CC) $(CFLAGS) $(SRC) main.c -o $@

$(LIB): $(SRC)
	$(CC) $(CFLAGS) $(PIC) -shared $(SRC) -o $@

native: kernelx_cli$(EXE)
	./kernelx_cli$(EXE) --demo

test: test_algorithms$(EXE)
	./test_algorithms$(EXE)

test_algorithms$(EXE): $(SRC) test_algorithms.c
	$(CC) $(CFLAGS) $(SRC) test_algorithms.c -o $@

# Optional: needs Emscripten (emcc). Not required for the normal run.
wasm:
	emcc -std=c11 -O2 algorithms.c wasm_api.c -o ../frontend/kernelx.js -s MODULARIZE=1 -s EXPORT_NAME=KernelXModule \
	  -s EXPORTED_FUNCTIONS=_kernelx_run,_kernelx_free -s EXPORTED_RUNTIME_METHODS=ccall,UTF8ToString

clean:
	rm -f kernelx_cli kernelx_cli.exe libkernelx.so kernelx.dll test_algorithms test_algorithms.exe

.PHONY: all native test wasm clean
