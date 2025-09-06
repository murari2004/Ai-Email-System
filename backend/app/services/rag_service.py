# Simple local RAG using sentence-transformers + FAISS
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os

MODEL_NAME = 'all-MiniLM-L6-v2'
INDEX_PATH = './kb_index.faiss'
DOCS_PATH = './kb_docs.jsonl'

class RAGService:
    def __init__(self):
        self.model = SentenceTransformer(MODEL_NAME)
        # load index if exists, else create empty structures
        self.index = None
        self.docs = []
        if os.path.exists(INDEX_PATH) and os.path.exists(DOCS_PATH):
            self.index = faiss.read_index(INDEX_PATH)
            import json
            with open(DOCS_PATH,'r',encoding='utf-8') as f:
                self.docs = [json.loads(l) for l in f]
        else:
            # create empty index
            self.index = None

    def add_docs(self, docs: list):
        # docs: list of {"id": str, "text": str, "meta": {}}
        import json
        texts = [d['text'] for d in docs]
        embs = self.model.encode(texts, convert_to_numpy=True)
        d = len(embs[0])
        if self.index is None:
            self.index = faiss.IndexFlatL2(d)
            self.docs = []
        self.index.add(np.array(embs).astype('float32'))
        # append docs and save
        for doc in docs:
            self.docs.append(doc)
        with open(DOCS_PATH,'w',encoding='utf-8') as f:
            for doc in self.docs:
                f.write(json.dumps(doc, ensure_ascii=False)+'\n')
        faiss.write_index(self.index, INDEX_PATH)

    def retrieve(self, query: str, top_k: int = 3):
        if self.index is None or len(self.docs)==0:
            return []
        q_emb = self.model.encode([query], convert_to_numpy=True).astype('float32')
        D, I = self.index.search(q_emb, top_k)
        results = []
        for idx in I[0]:
            if idx < len(self.docs):
                results.append(self.docs[idx]['text'])
        return results
