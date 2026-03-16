from sqlalchemy import (Column,Integer,String,Text,DateTime,
Float,Boolean,JSON,Index
)
from sqlalchemy.orm import declarative_base
from datetime import datetime
from sqlalchemy.sql import func

Base = declarative_base()

class MedicalAbstract(Base):
    __tablename__ = "medical_abstracts"

    id = Column(String(50), primary_key=True, index=True)

    pmid = Column(String(50), unique=True, nullable=False, index=True)
    doi = Column(String(100),nullable=True)

    title = Column(Text,nullable=False)
    abstract = Column(Text,nullable=False)

    publication_date = Column(DateTime,nullable=True,index=True)
    journal = Column(String(500),nullable=True)
    study_type = Column(String(500),nullable=True,index=True)


    mesh_terms = Column(JSON,nullable=True)

    authors = Column(JSON,nullable=True)

    citation_count = Column(Integer, default=0)

    sample_size = Column(Integer, nullable=True)

    has_full_text = Column(Boolean,default=False)
    full_text_url = Column(String(1000),nullable=True)

    processed = Column(Boolean,default=False,index=True)
    embedded = Column(Boolean,default=False,index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


    __table_args__ = (
        Index('idx_publication_year', 'publication_date'),
        Index('idx_study_type', 'study_type'),
        Index('idx_processed_embedded', 'processed', 'embedded'),
    )


    def __repr__(self):
        return f"<MedicalAbstract(pmid='{self.pmid}', title='{self.title[:50]}...')>"

    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "pmid": self.pmid,
            "title": self.title,
            "abstract": self.abstract,
            "publication_date": self.publication_date.isoformat() if self.publication_date else None,
            "journal": self.journal,
            "study_type": self.study_type,
            "mesh_terms": self.mesh_terms,
            "authors": self.authors,
            "citation_count": self.citation_count,
            "sample_size": self.sample_size,
        }
    
class ProcessedChunk(Base):
    __tablename__ = "processed_chunks"

    id = Column(Integer, primary_key=True,index=True)

    pmid = Column(String(50),nullable=False,index=True)

    chunk_index = Column(Integer,nullable=False)
    chunk_text = Column(Text,nullable=False)
    chunk_size = Column(Integer,nullable=False)

    title = Column(Text,nullable=False)
    study_type = Column(String(100), nullable=True)
    publication_year = Column(Integer, nullable=True, index=True)


    embedded = Column(Boolean, default=False, index=True)
    embedding_model = Column(String(100), nullable=True) 

    __table_args__ = (
        Index('idx_pmid_chunk', 'pmid', 'chunk_index'),
        Index('idx_embedded_year', 'embedded', 'publication_year'),
    )
    
    def __repr__(self):
        return f"<ProcessedChunk(pmid='{self.pmid}', chunk={self.chunk_index})>"
