import chromadb
from sentence_transformers import SentenceTransformer
from typing import List
import PyPDF2
import io
import uuid

class RAGEngine:
    def __init__(self):
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self.client = chromadb.Client()
        
        # Try to delete existing collection if it exists
        try:
            self.client.delete_collection(name="documents")
        except:
            pass
            
        self.collection = self.client.create_collection(name="documents")
        
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start = end - overlap
        return chunks
    
    def extract_text_from_pdf(self, file_bytes: bytes) -> str:
        """Extract text from PDF file"""
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    
    def clear_documents(self):
        """Clear all documents from the collection"""
        try:
            self.client.delete_collection(name="documents")
            self.collection = self.client.create_collection(name="documents")
            return True
        except Exception as e:
            print(f"Error clearing documents: {e}")
            return False
    
    def ingest_document(self, content: bytes, filename: str) -> int:
        """Ingest a document into the RAG system"""
        if filename.endswith('.pdf'):
            text = self.extract_text_from_pdf(content)
        else:
            text = content.decode('utf-8')
        
        chunks = self.chunk_text(text)
        
        # Generate unique IDs for each chunk
        ids = [str(uuid.uuid4()) for _ in chunks]
        
        # Add to vector database
        self.collection.add(
            documents=chunks,
            ids=ids
        )
        
        return len(chunks)
    
    def search(self, query: str, top_k: int = 3) -> List[str]:
        """Search for relevant chunks based on query with token limiting"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k
            )
            
            if results['documents'] and len(results['documents']) > 0:
                chunks = results['documents'][0]
                
                # Token limiting: Keep context under ~4000 tokens
                # Rough estimate: 4 characters per token
                total_chars = sum(len(c) for c in chunks)
                
                if total_chars > 16000:  # ~4000 tokens
                    # Truncate to top 2 chunks to stay within limit
                    chunks = chunks[:2]
                
                return chunks
            return []
        except Exception as e:
            print(f"Search error: {e}")
            return []
