
# Hybrid-Search based Insurance Knowledge Graph Assistant 🏥

A RAG-based question-answering system that uses LlamaIndex and Neo4j to provide intelligent responses about insurance concepts. The system builds a knowledge graph from insurance documents and uses it to provide context-aware answers along with visual graph representations.

<p align="left">
    <img src="https://github.com/Mithil01/Hybrid-Search-GraphRAG/blob/main/img/Arch.png" width="600">
</p>

## 🌟 Features

- Question answering with context from knowledge graph
- Visual representation of related concepts
- Hybrid search combining vector and keyword approaches
- Interactive web interface built with Streamlit
- Graph-based visualization of related concepts
- Community-based summarization

## 🛠️ Architecture
<p align="left">
    <img src="https://github.com/Mithil01/Hybrid-Search-GraphRAG/blob/main/img/Graphrag_img.png" width="1000">
</p>

- **Frontend**: Streamlit
- **Database**: Neo4j Aura
- **Embedding**: OpenAI
- **Graph Processing**: LlamaIndex
- **Visualization**: Plotly

## 📋 Prerequisites

- Python 3.9+
- Docker and Docker Compose
- Neo4j Aura Account
- OpenAI API Key

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/Mithil01/Hybrid-Search-GraphRAG.git
cd Hybrid-Search-GraphRAG
```

2. Set up environment variables:
```bash
# Export OpenAI API Key
export OPENAI_API_KEY='your_openai_api_key'

# Export Neo4j Credentials
export NEO4J_URI='neo4j+s://your_aura_instance_uri'
export NEO4J_USERNAME='neo4j'
export NEO4J_PASSWORD='your_neo4j_password'
```

3. Pull and run using Docker:
```bash
# Pull the Docker image
docker pull your-docker-image:latest

# Run with Docker Compose
docker compose up --build
```

4. Alternative: Local Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Unix/macOS
.\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run src/app.py
```

## 📁 Project Structure

```
insurance-knowledge-assistant/
├── book/                   # Source documents
├── src/
│   ├── app.py             # Streamlit application
│   ├── data_index.py      # Neo4j indexing logic
│   ├── data_models.py     # Data models
│   ├── generation.py      # Response generation
│   ├── graph_communities.py # Community detection
│   ├── graph_extractor.py  # Entity extraction
│   ├── graph_resolver.py   # Entity resolution
│   ├── indexing_pipeline.py# Data indexing
│   └── text_splitter.py   # Document processing
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## 🔧 Configuration

1. Neo4j Aura Setup:
   - Create an account at Neo4j Aura
   - Create a new database
   - Get connection details (URI, username, password)

2. OpenAI API Setup:
   - Get an API key from OpenAI
   - Set it as an environment variable

3. Docker Configuration:
```yaml
# docker-compose.yml
version: '3.12.6'
services:
  app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - NEO4J_URI=${NEO4J_URI}
      - NEO4J_USERNAME=${NEO4J_USERNAME}
      - NEO4J_PASSWORD=${NEO4J_PASSWORD}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
```
- Expose secret keys from the terminal before the docker build.
```
   export NEO4J_USERNAME="your_neo4j_username"
   export NEO4J_URI="your_neo4j_URI"
   export NEO4J_PASSWORD="your_neo4j_password"
   export OPENAI_API_KEY="your_OPENAI_API_KEY"
```

## 🚀 Usage

1. Start the application:
```bash
docker compose up
```

2. Access the web interface:
   - Open browser and navigate to `http://localhost:8501`
   - Enter insurance-related questions
   - View answers and related concept visualizations

## 📝 Example Queries

- "What are the different types of auto insurance coverage?"
- "What is the difference between term and whole life insurance?"
- "What is the process for handling insurance claims?"

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- Mithil Gaonkar

## 🙏 Acknowledgments

- Neo4j for graph database
- OpenAI for embeddings
- LlamaIndex for graph processing
- Streamlit for web interface

## 📞 Support

For support, email your-email@example.com or open an issue in the repository.
