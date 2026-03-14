import os
from typing import Dict
from .config import config
from news_ai_analysis.config import config as global_config
from .utils import *
# from sentence_transformers import SentenceTransformer
from google import genai
from google.genai import types
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document


class GoogleEmbedder():
    def __init__(self):
        self.client = genai.Client(api_key="AIzaSyA0Ya9_61Me7R51hgOcYh7J-US12afkaG0")

    def __call__(self, text):
        return self.client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
        config=types.EmbedContentConfig(task_type="SEMANTIC_SIMILARITY")
        ).embeddings

class Vectorstore():
    def __init__(self, path: str = config.VECTOR_STORE_PATH, embedding_model: str = config.EMBEDDING_MODEL):
        self.emb_model = SentenceTransformer(
            embedding_model) if not global_config.DISABLE_LOCAL_MODELS else GoogleEmbedder()
        self.__vectorstore = FAISS.load_local(
            os.getcwd() + path, self.emb_model, allow_dangerous_deserialization=True) if os.path.exists(os.getcwd() + path) else FAISS()

    def add_documents(self, documents: list[Document]):
        self.__vectorstore.add_documents(documents)

    def add(self, document: Document):
        self.add_documents([document])

    def search(self, queries: list[Dict]) -> list[Document]:
        docs = list()

        for q in queries:
            docs += self.__vectorstore.similarity_search(
                q.query, k=q.k, filter=q.filter)
        return distinct_documents(docs)

    def save_local(self):
        """
        Вызвать по завершении цикла сборщика
        """
        self.__vectorstore.save_local(os.getcwd() + config.VECTOR_STORE_PATH)
