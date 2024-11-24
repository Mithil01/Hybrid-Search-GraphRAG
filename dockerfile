# Use Python base image
FROM python:3.12.7

# Install build dependencies and Rust/Cargo
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    pkg-config \
    libssl-dev \
    git \
    gcc \
    g++ \
    make \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Install Rust and Cargo
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Verify Rust and Cargo installation
RUN cargo --version && rustc --version

# Set working directory
WORKDIR /app

# Copy requirements first
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app/

# Set environment variables for Neo4j Aura connection
ENV NEO4J_URI=neo4j+s://e52dbfe1.databases.neo4j.io
ENV NEO4J_USER=neo4j

# Expose port for Streamlit
EXPOSE 8501

# Command to run
CMD ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]