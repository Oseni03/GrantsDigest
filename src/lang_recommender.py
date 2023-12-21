import os
import csv
import openai
import tiktoken
import pandas as pd

from datetime import date
from openai.embeddings_utils import get_embedding

from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
from langchain.vectorstores import Chroma
from langchain.document_loaders import TextLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders.csv_loader import CSVLoader


def data_processing(
    data_dir="src/data/synopsis", today=date.today().strftime("%Y-%m-%d")
):
    data = pd.read_csv(f"{data_dir}/{today}.csv")
    data["description"] = data.apply(
        lambda row: f"Synopsis Description: {row['description']}. Applicant Eligibility Description: {row['applicant_eligibilty_desc']}. Applicant Types: {row['applicant_types']}",
        axis=1,
    )

    # Define the headers for the output CSV file
    headers = ["opportunity_id", "description"]

    outfile = f"{data_dir}/{today}-combined.csv"
    with open(outfile, "w", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=headers)

        writer.writeheader()

        for row in data:
            # Extract the desired fields from each row
            output_row = {
                "opportunity_id": row["opportunity_id"],
                "description": f"{row['description']}",
            }

            # Write the extracted fields to the output file
            writer.writerow(output_row)
    return outfile


def get_documents(csv_path):
    loader = CSVLoader(file_path=csv_path)
    data = loader.load()

    # data transformers
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    return text_splitter.split_documents(data)
