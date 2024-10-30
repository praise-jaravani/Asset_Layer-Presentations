# deadline_manager.py

from datetime import datetime, timedelta
import pandas as pd
from rag_system import RAGSystem

class DocumentDeadlineManager:
    def __init__(self):
        """Initialize the deadline manager"""
        # Initialize RAG system
        self.rag = RAGSystem()
        
        # Common document types and their typical renewal periods
        self.document_patterns = {
            'BBBEE Certificate': {'period': 365},  # Annual renewal
            'Environmental Authorization': {'period': 730},  # Bi-annual
            'Safety Certification': {'period': 365}  # Annual renewal
        }
        
        # Store document deadlines
        self.document_deadlines = pd.DataFrame(columns=[
            'document_id',
            'document_name',
            'document_type',
            'upload_date',
            'deadline_date',
            'deadline_source',  # 'explicit', 'inferred', or 'unknown'
            'confidence_level'  # 'high', 'medium', 'low'
        ])
        
        # Initialize document counter for IDs
        self.doc_counter = 0

    def parse_date(self, date_str):
        """Parse date string to datetime object"""
        if not date_str:
            return None
            
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            print(f"Error parsing date: {date_str}")
            return None

    def calculate_inferred_deadline(self, doc_type: str, document_date: str = None) -> datetime:
        """Calculate deadline based on document type and date"""
        try:
            # Use document date if provided, otherwise use current date
            start_date = self.parse_date(document_date) if document_date else datetime.now()
            if not start_date:
                start_date = datetime.now()
                
            period = self.document_patterns.get(doc_type, {}).get('period', 365)  # Default to annual
            return start_date + timedelta(days=period)
        except Exception as e:
            print(f"Error calculating deadline: {str(e)}")
            return None

    def determine_confidence_level(self, deadline_source: str, doc_info: dict) -> str:
        """Determine confidence level of deadline determination"""
        if deadline_source == 'explicit':
            return 'high'
        elif deadline_source == 'inferred':
            if doc_info.get('document_date'):
                return 'medium'
            else:
                return 'low'
        return 'low'

    def store_deadline_info(self, document_name: str, doc_info: dict, deadline_date: datetime, deadline_source: str):
        """Store document deadline information"""
        try:
            self.doc_counter += 1
            confidence = self.determine_confidence_level(deadline_source, doc_info)
            
            new_row = pd.DataFrame([{
                'document_id': f"DOC_{self.doc_counter}",
                'document_name': document_name,
                'document_type': doc_info.get('document_type'),
                'upload_date': datetime.now(),
                'deadline_date': deadline_date,
                'deadline_source': deadline_source,
                'confidence_level': confidence
            }])
            
            self.document_deadlines = pd.concat([self.document_deadlines, new_row], ignore_index=True)
            
            # Print detailed information
            print("\nDocument Analysis Results:")
            print(f"Document Type: {doc_info.get('document_type')}")
            print(f"Deadline Date: {deadline_date.strftime('%Y-%m-%d') if deadline_date else 'Not determined'}")
            print(f"Deadline Source: {deadline_source}")
            print(f"Confidence Level: {confidence}")
            if doc_info.get('other_dates'):
                print("Other relevant dates found:", doc_info.get('other_dates'))
            
        except Exception as e:
            print(f"Error storing deadline info: {str(e)}")

    def process_new_document(self, document_content: str, document_name: str):
        """Process a new document and determine its deadline"""
        try:
            print("\nAnalyzing document...")
            
            # Use RAG to analyze document
            doc_info = self.rag.analyze_document(document_content)
            
            if not doc_info:
                print(f"Could not analyze document: {document_name}")
                return
            
            print("\nDocument type identified:", doc_info.get('document_type'))
            
            # Try to find explicit deadline
            explicit_deadline = self.parse_date(doc_info.get('explicit_deadline'))
            doc_type = doc_info.get('document_type')
            
            if explicit_deadline:
                print("Explicit deadline found:", explicit_deadline.strftime('%Y-%m-%d'))
                deadline_date = explicit_deadline
                deadline_source = 'explicit'
            else:
                print("No explicit deadline found, attempting to infer...")
                # Infer deadline based on document type
                if doc_type in self.document_patterns:
                    deadline_date = self.calculate_inferred_deadline(
                        doc_type,
                        doc_info.get('document_date')
                    )
                    deadline_source = 'inferred'
                    if deadline_date:
                        print("Inferred deadline:", deadline_date.strftime('%Y-%m-%d'))
                else:
                    deadline_date = None
                    deadline_source = 'unknown'
                    print("Could not infer deadline - unknown document type")
            
            # Store document deadline info
            if deadline_date:
                self.store_deadline_info(
                    document_name,
                    doc_info,
                    deadline_date,
                    deadline_source
                )
            else:
                print(f"Could not determine deadline for document: {document_name}")
                
        except Exception as e:
            print(f"Error processing document: {str(e)}")

    def get_upcoming_deadlines(self, days_threshold: int = 30):
        """Get documents with upcoming deadlines"""
        try:
            if self.document_deadlines.empty:
                return pd.DataFrame()
                
            current_date = datetime.now()
            mask = (
                (self.document_deadlines['deadline_date'] >= current_date) & 
                (self.document_deadlines['deadline_date'] <= current_date + timedelta(days=days_threshold))
            )
            return self.document_deadlines[mask]
        except Exception as e:
            print(f"Error getting upcoming deadlines: {str(e)}")
            return pd.DataFrame()

    def get_expired_deadlines(self):
        """Get documents with expired deadlines"""
        try:
            if self.document_deadlines.empty:
                return pd.DataFrame()
                
            current_date = datetime.now()
            return self.document_deadlines[self.document_deadlines['deadline_date'] < current_date]
        except Exception as e:
            print(f"Error getting expired deadlines: {str(e)}")
            return pd.DataFrame()

    def get_all_deadlines(self):
        """Get all document deadlines"""
        return self.document_deadlines
