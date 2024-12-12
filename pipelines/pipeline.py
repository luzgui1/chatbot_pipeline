#%%

import subprocess
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from qdrant_client.http import models
import pandas as pd

class DockerManager:
    def __init__(self, port=6333):
        """
        Initialize DockerTest with default Qdrant port.

        Args:
            port (int): Port for the Qdrant server (default is 6333).
        """
        self.port = port

    @staticmethod
    def is_docker_running() -> bool:
        """
        Check if Docker daemon is running.
        
        Returns:
            bool: True if Docker daemon is running, False otherwise.
        """
        try:
            subprocess.run(["docker", "info"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    @staticmethod
    def check_docker_requirements():
        """
        Check Docker requirements and provide meaningful feedback.
        
        Raises:
            SystemError: If Docker is not installed or not running.
        """
        if not DockerManager.is_docker_running():
            message = (
                "Docker is not running or not installed.\n"
                "Please ensure that:\n"
                "1. Docker is installed on your system\n"
                "2. Docker is running\n"
                "3. You have necessary permissions to run Docker"
            )
            raise SystemError(message)

    @staticmethod
    def check_image(image: str) -> str:
        """
        Check if a Docker image exists locally and return the associated container ID if found.

        Args:
            image (str): The name of the Docker image (e.g., "qdrant").

        Returns:
            str: The container ID if the image exists and a container is associated, otherwise an empty string.
        """
        try:
            result = subprocess.run(
                ["docker", "images", "--format", "{{.Repository}}:{{.Tag}}"],
                capture_output=True,
                text=True,
                check=True
            )
            result_list = result.stdout.strip().split('\n')

            # Returning image name as in DockerHub
            matching_image = next((x for x in result_list if x.startswith(image)), "")
            return matching_image
        
        except subprocess.CalledProcessError:
            print("Error: Failed to execute Docker command.")
        except FileNotFoundError:
            print("Error: Docker is not installed or not in PATH.")

    @staticmethod
    def pull_image(image: str) -> str:
            """
            Pull a Docker image and return its full name.

            Args:
                image (str): The name of the Docker image (e.g., "qdrant").

            Returns:
                str: The full name of the image as found in the local Docker after pulling.
            """
            try:
                subprocess.run(["docker", "pull", image], check=True)
                print(f"Image '{image}' pulled successfully.")

                # Re-check the image name to get the full repository:tag format
                return DockerManager.check_image(image)
            except subprocess.CalledProcessError as e:
                print(f"Error pulling image '{image}': {e}")
            except FileNotFoundError:
                print("Error: Docker is not installed or not in PATH.")

    @staticmethod
    def run_container_by_id(image: str) -> None:
            """
            Run a Docker container by its ID.

            Args:
                container_id (str): The ID of the Docker container.
            """
            try:
                container_id = subprocess.run([
                    "docker", "ps", "-a", "--filter", f"ancestor={image}", "--format", "{{.ID}}"
                ], capture_output=True, text=True, check=True).stdout.strip()

                subprocess.run(["docker", "start", container_id], check=True)            
                print(f"Container with ID '{container_id}' started successfully.")

            except subprocess.CalledProcessError as e:
                print(f"Error starting container '{container_id}': {e}")
            except Exception as e:
                print(f"Unexpected error: {e}")

    @staticmethod
    def manage_container(image: str, local_port: int, remote_port: int) -> None:
            """
            Check if a Docker image exists locally, and either start an associated container
            or pull the image and create a new container.

            Args:
                image (str): The name of the Docker image (e.g., "qdrant").
                local_port (int): The local port to bind.
                remote_port (int): The remote port to bind.
            """
            image_name = DockerManager.check_image(image)
            if image_name:
                print(f"Found container ID for image: {image_name}. Starting container...")
                DockerManager.run_container_by_id(image_name)

            else:
                print(f"Image '{image}' not found locally. Pulling image...")
                image_name = DockerManager.pull_image(image)

                if not image_name:
                    print(f"Failed to pull image '{image}'.")
                    return

                print(f"Running a new container for image '{image_name}'...")
                try:
                    subprocess.run(
                        ["docker", "run", "-d", "-p", f"{local_port}:{remote_port}", image_name],
                        check=True
                    )
                    print(f"New container for '{image_name}' started successfully.")
                except subprocess.CalledProcessError as e:
                    print(f"Error running new container for '{image_name}': {e}")

    def check_collection_exists(self, collection_name: str) -> bool:
        """
        Check if a collection exists in Qdrant.

        Args:
            collection_name (str): The name of the collection to check.

        Returns:
            bool: True if the collection exists, False otherwise.
        """
        client = QdrantClient(host="localhost", port=self.port)
        collections = client.get_collections()

        return any(col.name == collection_name for col in collections.collections)
    
    def check_collection_has_content(self, collection_name: str) -> bool:
        """
        Check if a collection has any points/content in Qdrant.

        Args:
            collection_name (str): The name of the collection to check.

        Returns:
            bool: True if the collection has points, False otherwise.
        """
        client = QdrantClient(host="localhost", port=self.port)
        
        # Get collection info which includes points count
        collection_info = client.get_collection(collection_name=collection_name)
        
        # Return True if points count is greater than 0
        return collection_info.points_count > 0

    def insert_data(self, collection_name: str, data_path: str) -> None:
        """
        Insert data from a CSV file into a Qdrant collection.

        Args:
            collection_name (str): The name of the Qdrant collection.
            data_path (str): Path to the CSV file containing the data.
        """
        try:

            client = QdrantClient(host="localhost", port=self.port)
            encoder = SentenceTransformer('all-MiniLM-L6-v2')

            if self.check_collection_exists(collection_name):
                print(f"Collection '{collection_name}' already exists.")

            else:
                # Create the collection
                client.create_collection(
                    collection_name=collection_name,
                    vectors_config=models.VectorParams(
                        size=encoder.get_sentence_embedding_dimension(),
                        distance=models.Distance.COSINE
                    )
                )

            # Load data and insert into Qdrant
            data = pd.read_csv(data_path)
            column_name = data.columns[0]

            points = [
                models.PointStruct(
                    id=idx,
                    vector=encoder.encode(row[column_name]).tolist(),
                    payload=row.to_dict()
                )
                for idx, row in data.iterrows()
            ]

            client.upload_points(collection_name=collection_name, points=points)
            print(f"Data inserted into collection '{collection_name}' successfully.")
        except Exception as e:
            print(f"An error occurred while inserting data: {e}")

    def delete_colection(self,collection_name: str):
        client = QdrantClient(host="localhost", port=self.port)
        client.delete_collection(collection_name=collection_name)

        print("Your collection has been deleted.")

#%%