# %%

from pipelines.pipeline import DockerManager

DockerPipeline = DockerManager(port='6333')

if DockerPipeline.is_docker_running():

    DockerPipeline.manage_container('qdrant/qdrant',6333,6333)
    print("Container 'qdrant' is running in port 6333.")

    if DockerPipeline.check_collection_exists('books') and DockerPipeline.check_collection_has_content('books'):
        print("Collection 'books' exists and has content.")

    else:
        DockerPipeline.insert_data('books','./data/datasets/books_clean.csv')
        print("Data was inserted into 'books'.")

else:
    print("Docker is not running. Please start Docker and try again.")




# %%