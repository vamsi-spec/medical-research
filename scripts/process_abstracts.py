import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from Backend.services.preprocessing_service import MedicalTextPreprocessor, preprocessor
from Backend.models.database_models import MedicalAbstract,ProcessedChunk
from Backend.core.database import get_db_context
from loguru import logger
from tqdm import tqdm


logger.add("logs/processing.log",rotation="100 MB",level="INFO")


def process_all_abstracts(
    chunk_size: int = 500,
    chunk_overlap: int = 50,
    batch_size: int = 100
):


    with get_db_context() as db:
        abstracts = db.query(MedicalAbstract).filter(
            MedicalAbstract.processed == False
        ).all()

        total = len(abstracts)
        logger.info(f"Processing {total} abstracts")

        if total == 0:
            logger.info("No abstracts to process")
            return
        
        processed_count = 0
        chunks_created = 0

        for i in tqdm(range(0,total,batch_size),desc="Processing batches"):
            batch = abstracts[i:i+batch_size]
            for abstract in batch:
                chunks = preprocessor.chunk_abstract(
                    title=abstract.title,
                    abstract=abstract.abstract,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap
                )

                for chunk_data in chunks:
                    chunk = ProcessedChunk(
                        pmid=abstract.pmid,
                        chunk_index=chunk_data['chunk_index'],
                        chunk_text=chunk_data['text'],
                        chunk_size=chunk_data['chunk_size'],
                        title=abstract.title,
                        study_type=abstract.study_type,
                        publication_year=abstract.publication_date.year if abstract.publication_date else None,
                        embedded=False,
                        embedding_model=None
                    )
                    db.add(chunk)
                    chunks_created += 1

                abstract.processed = True
                processed_count += 1
                
            db.commit()

            logger.info(f"Processed {min(i+batch_size, total)}/{total} abstracts")
        
        logger.info(f"Processing complete!")
        logger.info(f"Abstracts processed: {processed_count}")
        logger.info(f"Chunks created: {chunks_created}")
        logger.info(f"Avg chunks per abstract: {chunks_created/processed_count:.2f}")


if __name__ == "__main__":
    process_all_abstracts()
    
    # Print statistics
    with get_db_context() as db:
        total_chunks = db.query(ProcessedChunk).count()
        total_abstracts = db.query(MedicalAbstract).filter(
            MedicalAbstract.processed == True
        ).count()
        
        print("\n" + "="*60)
        print("PROCESSING STATISTICS")
        print("="*60)
        print(f"Total abstracts processed: {total_abstracts}")
        print(f"Total chunks created: {total_chunks}")
        if total_abstracts > 0:
            print(f"Average chunks per abstract: {total_chunks/total_abstracts:.2f}")
        else:
            print("Average chunks per abstract: 0.00")
        
        # Sample chunk
        sample = db.query(ProcessedChunk).first()
        if sample:
            print(f"\n📄 Sample Chunk:")
            print(f"PMID: {sample.pmid}")
            print(f"Chunk Index: {sample.chunk_index}")
            print(f"Chunk Size: {sample.chunk_size}")
            print(f"Text: {sample.chunk_text[:200]}...")
