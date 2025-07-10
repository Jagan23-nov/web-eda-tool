# Use Debian as the base image
FROM debian:bullseye

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3 python3-pip python3-venv \
    git curl wget \
    cmake bison flex libreadline-dev gawk tcl-dev libffi-dev \
    libftdi-dev libusb-1.0-0-dev libboost-all-dev pkg-config \
    clang libeigen3-dev libjsoncpp-dev zlib1g-dev \
    iverilog \
    gtkwave && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# ---------- Yosys ----------
WORKDIR /tools
RUN git config --global http.postBuffer 524288000 && \
    git clone https://github.com/YosysHQ/yosys.git && \
    cd yosys && \
    git submodule update --init --recursive && \
    make -j$(nproc) && make install

# ---------- Project IceStorm ----------
WORKDIR /tools
RUN git clone https://github.com/YosysHQ/icestorm.git && \
    cd icestorm && \
    make -j$(nproc) && make install

# ---------- Upgrade CMake (>= 3.25 required by nextpnr) ----------
WORKDIR /tmp
RUN curl -LO https://github.com/Kitware/CMake/releases/download/v3.27.9/cmake-3.27.9-linux-x86_64.tar.gz && \
    tar -xzf cmake-3.27.9-linux-x86_64.tar.gz && \
    cp -r cmake-3.27.9-linux-x86_64/bin/* /usr/local/bin/ && \
    cp -r cmake-3.27.9-linux-x86_64/share/* /usr/local/share/ && \
    cmake --version

# ---------- nextpnr (for ice40) ----------
WORKDIR /tools
RUN git clone https://github.com/YosysHQ/nextpnr.git && \
    mkdir -p /tools/nextpnr/build && \
    cd /tools/nextpnr/build && \
    cmake -DARCH=ice40 .. && \
    make -j$(nproc) && make install

# ---------- FastAPI HDL App ----------
WORKDIR /app
COPY . .

# Create results directory to store simulation outputs
RUN mkdir -p /app/backend/results

# Install Python dependencies
RUN pip3 install fastapi uvicorn pydantic aiofiles

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
