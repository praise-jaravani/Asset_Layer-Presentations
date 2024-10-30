# rag_system.py

from langchain_community.vectorstores import PGVector
from langchain_community.embeddings import HuggingFaceHubEmbeddings
from text_generation import Client
import json
import time
from datetime import datetime
import re

class RAGSystem:
    def __init__(self):
        """Initialize connections to embedding service, database, and LLM"""
        self.embeddings = HuggingFaceHubEmbeddings(
            model="http://localhost:9002",
            huggingfacehub_api_token="EMPTY"
        )
        
        self.store = PGVector(
            collection_name="documents",
            connection_string="postgresql+psycopg2://postgres:postgres@localhost:9003/postgres",
            embedding_function=self.embeddings,
        )
        
        self.llm_client = Client("http://localhost:9001", timeout=30)  # Increased timeout

    def clean_date(self, date_str: str) -> str:
        """Convert various date formats to YYYY-MM-DD"""
        try:
            # Try different date formats
            for fmt in [
                "%d/%m/%Y", "%Y-%m-%d", "%B %d, %Y", "%d %B %Y",
                "%Y/%m/%d", "%d-%m-%Y", "%d.%m.%Y"
            ]:
                try:
                    return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
                except ValueError:
                    continue
            return None
        except Exception:
            return None


    def search_similar_docs(self, query: str, k: int = 2):
        """Search for similar documents in vector database"""
        try:
            # Convert query to embedding and search
            docs = self.store.similarity_search(query, k=k)
            return docs
        except Exception as e:
            print(f"Error searching documents: {str(e)}")
            # Return empty list as fallback
            return []

    def extract_dates_from_text(self, text: str) -> list:
        """Extract dates from text using regex"""
        # Various date patterns
        patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # DD/MM/YYYY
            r'\d{1,2}\s(?:January|February|March|April|May|June|July|August|September|October|November|December)\s\d{4}',  # DD Month YYYY
            r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s\d{1,2},?\s\d{4}'  # Month DD, YYYY
        ]
        
        dates = []
        for pattern in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                date_str = match.group()
                cleaned_date = self.clean_date(date_str)
                if cleaned_date:
                    dates.append(cleaned_date)
        
        return list(set(dates))  # Remove duplicates

    def generate_answer(self, query: str, similar_docs: list) -> dict:
        """Generate answer using LLM based on query and similar documents"""
        try:
            # Construct prompt with better structure for JSON response
            context = "\n".join(doc.page_content for doc in similar_docs)
            prompt = f"""Analyze this document and provide information in the following JSON format:
            {{
                "document_type": "CHOOSE ONE: BBBEE Certificate, Environmental Authorization, Safety Certification",
                "explicit_deadline": "YYYY-MM-DD format if found, null if not found",
                "document_date": "YYYY-MM-DD format if found, null if not found",
                "other_dates": ["YYYY-MM-DD", "YYYY-MM-DD", ...]
            }}

            Document content: {context}

            Provide ONLY the JSON response, no additional text.
            """
            
            # Generate response with retries
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = self.llm_client.generate(
                        prompt,
                        max_new_tokens=1024,
                        stop_sequences=["</s>"]
                    ).generated_text

                    # Clean up response to ensure valid JSON
                    response = response.strip()
                    response = re.sub(r'^[^{]*', '', response)  # Remove any text before {
                    response = re.sub(r'[^}]*$', '', response)  # Remove any text after }
                    
                    # Parse JSON
                    data = json.loads(response)
                    
                    # Clean up dates
                    if data.get('explicit_deadline'):
                        data['explicit_deadline'] = self.clean_date(data['explicit_deadline'])
                    if data.get('document_date'):
                        data['document_date'] = self.clean_date(data['document_date'])
                    if data.get('other_dates'):
                        data['other_dates'] = [self.clean_date(d) for d in data['other_dates'] if self.clean_date(d)]
                    
                    return data

                except json.JSONDecodeError:
                    if attempt == max_retries - 1:
                        print(f"Failed to parse JSON after {max_retries} attempts")
                        # Fallback to date extraction from raw text
                        dates = self.extract_dates_from_text(context)
                        return {
                            "document_type": self.infer_document_type(context),
                            "explicit_deadline": dates[0] if dates else None,
                            "document_date": None,
                            "other_dates": dates[1:] if len(dates) > 1 else []
                        }
                    time.sleep(1)  # Wait before retry
                
                except Exception as e:
                    print(f"Error in attempt {attempt + 1}: {str(e)}")
                    if attempt == max_retries - 1:
                        raise

        except Exception as e:
            print(f"Error generating answer: {str(e)}")
            return None

    def infer_document_type(self, text: str) -> str:
        """Infer document type from text content"""
        text = text.lower()
        if 'b-bbee' in text or 'bbbee' in text or 'broad-based black economic empowerment' in text:
            return 'BBBEE Certificate'
        elif 'environmental authorization' in text or 'environmental assessment' in text:
            return 'Environmental Authorization'
        elif 'safety' in text and ('certification' in text or 'certificate' in text):
            return 'Safety Certification'
        return None

    def analyze_document(self, content: str) -> dict:
        """Complete RAG pipeline for document analysis"""
        try:
            # Get similar documents
            similar_docs = self.search_similar_docs(
                f"Represent this document for finding similar document types: {content}"
            )
            
            # Generate and return analysis
            result = self.generate_answer(content, similar_docs)
            
            if not result:
                # Fallback to basic analysis
                dates = self.extract_dates_from_text(content)
                return {
                    "document_type": self.infer_document_type(content),
                    "explicit_deadline": dates[0] if dates else None,
                    "document_date": None,
                    "other_dates": dates[1:] if len(dates) > 1 else []
                }
                
            return result

        except Exception as e:
            print(f"Error in document analysis: {str(e)}")
            return None

# rag_system.py

def search_similar_docs(self, query: str, k: int = 2):
    """Search for similar documents in vector database"""
    try:
        # Convert query to embedding and search
        docs = self.store.similarity_search(query, k=k)
        return docs
    except Exception as e:
        print(f"Error searching documents: {str(e)}")
        # Return empty list as fallback
        return []	
