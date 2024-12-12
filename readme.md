# Docker-based Qdrant Pipeline

## Overview

This project demonstrates how to automate a pipeline using Docker and Qdrant for managing vector databases. The pipeline provides tools to manage Docker containers, check and manipulate Qdrant collections, and insert data from CSV files.

## Features

1. **Docker Management**
   - Check if Docker is installed and running.
   - Verify if required Docker images are present locally.
   - Automatically pull missing images from Docker Hub based on the image name as in DockerHub.
   - Start or run containers dynamically.

2. **Qdrant Database Integration**
   - Check if collections exist and have content.
   - Create collections with the appropriate vector configuration.
   - Insert data into collections from CSV files using `SentenceTransformer` for vector embeddings. Note: The first column of the CSV file will be used as the vector embedding.
   - Delete collections when no longer needed.

## Project Structure

```plaintext
.
├── pipelines
│   ├── pipeline.py         # Core logic for Docker and Qdrant management
├── pipeline_execute.py     # Main execution script
├── test_db.py              # Test script for checking the collection search
├── data
│   └── get_data.py         # Script for getting the data from Kaggle
│   └── datasets
│       └── books_clean.csv # Example dataset
├── README.md               # Project documentation
```

## Requirements

- Python 3.8+
- Docker installed and running
- Required Python libraries (see below)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/luzgui1/chatbot_pipeline.git
   cd chatbot_pipeline
   ```

2. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```
   or

   ```bash
   conda install -c conda-forge requirements.txt
   ```

3. Ensure Docker is installed and running on your machine.

## Usage

### Running the Pipeline

1. Prepare your dataset:
   - Place your CSV file in the `data/datasets` folder.
   - Ensure the file is named in pipeline_execute.py in the place of `books_clean.csv` or modify the path in `pipeline_execute.py` accordingly.

2. Execute the pipeline:

   ```bash
   python pipeline_execute.py
   ```

3. The script will:
   - Check if Docker is running.
   - Manage the `qdrant/qdrant` container or any other container you want to manage.
   - Verify if the `books` collection exists and has content or any other collection you want to manage.
   - Insert data into the `books` collection if needed or any other collection you want to manage.

### Example Dataset

The project includes a sample dataset: `books_clean.csv`, which contains book metadata to demonstrate the pipeline’s functionality.

### Managing Docker Containers

You can use `DockerManager` class methods directly to:

- Check Docker installation:
  ```python
  DockerManager.is_docker_running()
  ```

- Manage images and containers by pulling the image from DockerHub and running the container in any port you want:
  ```python
  DockerManager.manage_container('qdrant/qdrant', 6333, 6333)
  ```


### Working with Qdrant

Use the `DockerManager` class to:

- Check if a collection exists:
  ```python
  DockerPipeline.check_collection_exists('collection_name')
  ```

- Insert data into a collection:
  ```python
  DockerPipeline.insert_data('collection_name', './path/to/dataset.csv')
  ```

- Delete a collection if needed:
  ```python
  DockerPipeline.delete_collection('collection_name')
  ```

## Dependencies

The following Python libraries are required:

- `qdrant-client`
- `sentence-transformers`
- `pandas`
- `subprocess`
- `pytorch`
- `polars`

Install them via:

```bash
pip install requirements.txt
```

or

```bash
conda install -c conda-forge requirements.txt
```

## Notes

- Ensure that Docker has sufficient permissions and resources to run Qdrant containers.
- The pipeline is configured to use port `6333` by default; modify it as needed in the scripts.

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests for improvements or new features.


## Acknowledgments

- [Qdrant](https://qdrant.tech) for providing a robust vector search engine.
- [Hugging Face](https://huggingface.co) for the `SentenceTransformer` model used in embedding generation.
- [Kaggle](https://kaggle.com) for the dataset used in the example.
- [Docker](https://docker.com) for providing the containerization platform.

---

