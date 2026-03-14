import os
from typing import Dict
from .config import config
from news_ai_analysis.config import config as global_config
from .utils import *
from sentence_transformers import SentenceTransformer
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document


class Vectorstore():
    def __init__(self, path: str = config.VECTOR_STORE_PATH, embedding_model: str = config.EMBEDDING_MODEL):
        self.emb_model = SentenceTransformer(
            embedding_model)
        self.__vectorstore = FAISS.load_local(
            os.getcwd() + path, self.emb_model, allow_dangerous_deserialization=True)

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
