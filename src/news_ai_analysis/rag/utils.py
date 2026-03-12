from langchain_core.documents import Document


def distinct_documents(documents: list[Document]) -> list[Document]:
    doc_ids = list()
    result = list()
    for doc in documents:
        if doc.id not in doc_ids:
            doc_ids.append(doc.id)
            result.append(doc)
    return result