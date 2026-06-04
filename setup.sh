#!/usr/bin/env bash
# Bengaluru GraphRAG - Automated Environment Setup
# Maintains strict error handling
set -e
set -o pipefail

# ANSI color codes for terminal output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Initializing Bengaluru GraphRAG Environment Setup...${NC}"

# 1. Check prerequisites
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 is not installed. Please install Python 3.9+.${NC}"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed. Required for Qdrant Vector DB.${NC}"
    exit 1
fi

# 2. Setup Virtual Environment
echo -e "${BLUE}Creating Python virtual environment...${NC}"
python3 -m venv .venv
source .venv/bin/activate

# 3. Install Dependencies
echo -e "${BLUE}Installing Python dependencies...${NC}"
pip install --upgrade pip
# Assuming requirements.txt is present
pip install networkx qdrant-client sentence-transformers requests streamlit pyyaml

# 4. Bootstrap Qdrant via Docker
echo -e "${BLUE}Spinning up Qdrant Vector Database...${NC}"
mkdir -p qdrant_storage
if [ "$(docker ps -q -f name=qdrant_graphrag)" ]; then
    echo -e "${GREEN}Qdrant is already running.${NC}"
else
    docker run -d --name qdrant_graphrag -p 6333:6333 -p 6334:6334 \
        -v $(pwd)/qdrant_storage:/qdrant/storage:z \
        qdrant/qdrant
    echo -e "${GREEN}Qdrant initialized on port 6333.${NC}"
fi

# 5. Create necessary directories
echo -e "${BLUE}Verifying directory structure...${NC}"
mkdir -p src/{ingestion,retrieval,llm,evaluation}
mkdir -p data/ output/ docs/{screenshots,diagrams}

echo -e "${GREEN}Setup Complete! Activate your environment using: source .venv/bin/activate${NC}"