import sys
from pathlib import Path
import os


sys.path.append(str(Path(__file__).resolve().parent.parent))

from Backend.services.pubmed_service import PubMedService
from Backend.models.database_models import MedicalAbstract
from Backend.core.database import get_db_context
from loguru import logger
from tqdm import tqdm
from sqlalchemy import func

logger.add("logs/pubmed_fetch.log",rotation="100 MB",retention="10 days",level="INFO")

def fetch_and_store_abstracts(
    queries: list[str],
    abstracts_per_query: int = 500,
    min_year: int = 2020
):
    service = PubMedService()
    total_fetched = 0
    total_stored = 0

    logger.info(f"starting fetch for {len(queries)} queries")
    logger.info(f"abstracts per query: {abstracts_per_query}")

    for query in queries:
        logger.info(f"\n{'='*50}")
        logger.info(f"Query:{query}")
        logger.info(f"{'='*50}")


        pmids = service.search(query = query,max_results=abstracts_per_query,min_year=min_year)
        if not pmids:
            logger.warning(f"No PMIDs found for query: {query}")
            continue

        abstracts = service.fetch_abstracts(pmids)
        total_fetched += len(abstracts)

        stored = store_abstracts(abstracts)
        total_stored += stored

        logger.info(f"Query complete: {stored} abstracts stored")

    logger.info(f"\n{'='*60}")
    logger.info(f"FETCH COMPLETE")
    logger.info(f"{'='*60}")
    logger.info(f"Total fetched: {total_fetched}")
    logger.info(f"Total stored: {total_stored}")
    logger.info(f"Duplicates skipped: {total_fetched - total_stored}")


def store_abstracts(abstracts: list[dict]) -> int:

    stored_count = 0
    with get_db_context() as db:
        # Optimization: Check for existing PMIDs in batch to reduce DB queries
        pmids = [a["pmid"] for a in abstracts]
        existing_pmids = {
            res[0] for res in db.query(MedicalAbstract.pmid)
            .filter(MedicalAbstract.pmid.in_(pmids))
            .all()
        }

        for abstract_data in tqdm(abstracts,desc="Storing abstracts"):
            if abstract_data["pmid"] in existing_pmids:
                continue

            abstract = MedicalAbstract(**abstract_data)
            db.add(abstract)
            stored_count += 1

        db.commit()

    return stored_count


def main():
    queries = [
        # Chronic diseases (600 each = 3000 total)
        "diabetes mellitus treatment",
        "hypertension management",
        "cancer immunotherapy",
        "cardiovascular disease prevention",
        "chronic kidney disease treatment",
        
        # Recent topics (400 each = 1200 total)
        "COVID-19 treatment",
        "long COVID management",
        "mRNA vaccine safety",
        
        # Important clinical topics (200 each = 800 total)
        "drug interactions clinical",
        "adverse drug reactions",
        "clinical trial methodology",
        "evidence-based medicine",
    ]


    fetch_and_store_abstracts(queries,abstracts_per_query=500,min_year=2020)

    with get_db_context() as db:
        total = db.query(MedicalAbstract).count()
        by_type = db.query(MedicalAbstract.study_type,func.count(MedicalAbstract.id)).group_by(MedicalAbstract.study_type).all()
        print("\n" + "="*60)
        print("DATABASE STATISTICS")
        print("="*60)
        print(f"Total abstracts: {total}")
        print(f"\nBy study type:")
        for study_type, count in sorted(by_type, key=lambda x: x[1], reverse=True):
            print(f"  {study_type}: {count}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.warning("Fetch process interrupted by user.")
