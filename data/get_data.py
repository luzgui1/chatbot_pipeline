
import os
from kaggle.api.kaggle_api_extended import KaggleApi
import polars as pl

# Initialize Kaggle API
api = KaggleApi()
api.authenticate()

# Specify dataset and download location
dataset = "dylanjcastillo/7k-books-with-metadata"
download_path = "data/datasets"

# Create download folder if it doesn't exist
os.makedirs(download_path, exist_ok=True)

# Download the dataset
api.dataset_download_files(dataset, path=download_path, unzip=True)

print(f"Dataset downloaded and saved to: {download_path}")

# Load the dataset
df = pl.read_csv("./datasets/books.csv")

# Select relevant columns
dft = df.select(["title", "authors", "categories", "description"])

# Clean double quotes and remove rows with "null" or null in the description
dff = dft.with_columns([
    dft[col].str.replace('"', '') if dft[col].dtype == pl.Utf8 else dft[col]
    for col in dft.columns
]).filter(
    (dft["description"].fill_null("null") != "null")
)

combined = dff.with_columns([
    pl.concat_str(dff.columns, separator=" ").alias("combined_column")
]).select("combined_column").unique()

combined.write_csv("datasets/books_clean.csv")