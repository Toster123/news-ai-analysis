import os
from typing import Dict
from .config import config
from src.news_ai_analysis.config import config as global_config
from .utils import *
from sentence_transformers import SentenceTransformer
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
import numpy as np


class Vectorstore():
    def __init__(self, path: str = config.VECTOR_STORE_PATH, embedding_model: str = config.EMBEDDING_MODEL):
        self.emb_model = SentenceTransformer(embedding_model) if not global_config.DISABLE_LOCAL_MODELS else None
        
        # Используем os.path.join вместо конкатенации строк
        full_path = os.path.join(os.getcwd(), path)
        
        # Проверяем существование файла и создаем новый индекс если нужно
        if os.path.exists(full_path + ".faiss") and os.path.exists(full_path + ".pkl"):
            self.__vectorstore = FAISS.load_local(full_path, self.emb_model, allow_dangerous_deserialization=True)
        else:
            # Создаем индекс с одним фиктивным документом, который потом удалим
            from langchain_community.embeddings import HuggingFaceEmbeddings
            embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
            
            # Создаем фиктивный документ для инициализации индекса
            dummy_doc = Document(page_content="dummy", metadata={"dummy": True})
            self.__vectorstore = FAISS.from_documents([dummy_doc], embeddings)
            
            # Удаляем фиктивный документ (очищаем индекс)
            if hasattr(self.__vectorstore, 'index') and self.__vectorstore.index.ntotal > 0:
                # Для FAISS нет прямого метода удаления, создаем новый пустой индекс с правильной размерностью
                dummy_embedding = embeddings.embed_query("dummy")
                dimension = len(dummy_embedding)
                
                # Создаем новый пустой индекс
                import faiss
                index = faiss.IndexFlatL2(dimension)
                self.__vectorstore.index = index
                self.__vectorstore.docstore = {}
                self.__vectorstore.index_to_docstore_id = {}

    def add_documents(self, documents: list[Document]):
        self.__vectorstore.add_documents(documents)
    
    def add(self, document: Document):
        self.add_documents([document])
        
    def search(self, queries: list[Dict]) -> list[Document]:
        docs = list()

        for q in queries:
            docs += self.__vectorstore.similarity_search(q.query, k=q.k, filter=q.filter)
        return distinct_documents(docs)
    
    def save_local(self):
        """
        Вызвать по завершении цикла сборщика
        """
        full_path = os.path.join(os.getcwd(), config.VECTOR_STORE_PATH)
        # Создаем директорию если нужно
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        self.__vectorstore.save_local(full_path)