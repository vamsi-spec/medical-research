from Bio import Entrez
from typing import List,Dict,Optional
from datetime import datetime
import time
import os
from dotenv import load_dotenv
from loguru import logger
import urllib.error
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.append(BASE_DIR)
load_dotenv(os.path.join(BASE_DIR, "config", ".env"))

Entrez.email = os.getenv("PUBMED_EMAIL", "").strip()
Entrez.tool = "MedicalResearchAssistant"

api_key = os.getenv("PUBMED_API_KEY")
if api_key:
    api_key = api_key.strip()
    if api_key.lower() in ["none", "null", ""]:
        api_key = None

Entrez.api_key = api_key

class PubMedService:
    def __init__(self):
        self.email = Entrez.email
        self.api_key = Entrez.api_key

        self.delay = 0.1 if self.api_key else 0.34

        logger.info(f"PubMed Service initialized (email: {self.email})")

    def search(
        self,
        query:str,
        max_results:int = 100,
        min_year: int = 2020,
        study_types: Optional[List[str]] = None
    ) -> List[str]:

        search_query = f"{query} AND {min_year}:3000[dp]"

        if study_types:
            type_filter = "OR".join([f'"{st}"[pt]' for st in study_types])
            search_query = f"{search_query} AND ({type_filter})"
        logger.info(f"Searching PubMed with query: {search_query}")

        try:
            handle = Entrez.esearch(
                db="pubmed",
                term=search_query,
                retmax=max_results,
                sort="relevance",
                retmode="xml"
            )

            record = Entrez.read(handle)
            handle.close()
            pmids = record["IdList"]
            count = int(record["Count"])
            logger.info(f"Found {count} results, returning {len(pmids)} PMIDS")

            return pmids
        except urllib.error.HTTPError as e:
            if e.code == 400 and Entrez.api_key:
                logger.warning("HTTP 400 received. API Key might be invalid. Retrying without API Key...")
                Entrez.api_key = None
                # Recursive retry without API key
                return self.search(query, max_results, min_year, study_types)
            
            logger.error(f"Error searching PubMed: {e}")
            return []
        except Exception as e:
            logger.error(f"Error searching PubMed: {e}")
            return []
    

    def fetch_abstracts(self,pmids: List[str],batch_size: int = 100)-> List[Dict]:
        abstracts = []
        total = len(pmids)

        for i in range(0,total,batch_size):
            batch = pmids[i:i + batch_size]
            batch_num = (i//batch_size) + 1
            total_batches = (total//batch_size) + 1

            logger.info(f"Fetching batch {batch_num}/total_batches({len(batch)} articles)")

            try:
                handle = Entrez.efetch(
                    db="pubmed",
                    id=batch,
                    retmode="xml",
                    rettype="abstract"
                )

                records = Entrez.read(handle)
                handle.close()

                for article in records["PubmedArticle"]:
                    parsed = self._parse_article(article)
                    if parsed:
                        abstracts.append(parsed)

                time.sleep(self.delay)

            except Exception as e:
                logger.error(f"Error fetching batch {batch_num}/{total_batches}: {e}")
                continue
        
        logger.info(f"Successfully fetched {len(abstracts)} abstracts")

        return abstracts

    def save_to_db(self, abstracts: List[Dict]):
        """Saves a list of abstract dictionaries to the database."""
        from Backend.core.database import SessionLocal
        from Backend.models.database_models import MedicalAbstract

        db = SessionLocal()
        saved_count = 0
        try:
            for item in abstracts:
                # Check if PMID already exists to prevent duplicates
                exists = db.query(MedicalAbstract).filter(MedicalAbstract.pmid == item['pmid']).first()
                if not exists:
                    new_abstract = MedicalAbstract(**item)
                    db.add(new_abstract)
                    saved_count += 1
            
            db.commit()
            logger.info(f"Successfully saved {saved_count} new abstracts to database")
        except Exception as e:
            logger.error(f"Database error: {e}")
            db.rollback()
        finally:
            db.close()

    def _parse_article(self,article) -> Optional[Dict]:
        try:
            medline = article['MedlineCitation']
            pubmed_data = article.get('PubmedData', {})

            pmid = str(medline['PMID'])

            article_data = medline['Article']
            title = article_data.get('ArticleTitle', '')
            abstract_texts = article_data.get('Abstract', {}).get('AbstractText', [])

            if isinstance(abstract_texts, list):
                abstract = ' '.join([str(text) for text in abstract_texts])
            else:
                abstract = str(abstract_texts)
            

            if not abstract or len(abstract) < 100:
                return None

            pub_date = article_data.get('ArticleDate', [{}])
            if pub_date:
                try:
                    year = int(pub_date[0].get('Year',0))
                    month = int(pub_date[0].get('Month',1))
                    day = int(pub_date[0].get('Day',1))
                    if year > 0:
                        publication_date = datetime(year,month,day)
                    else:
                        publication_date = None
                except:
                    publication_date = None
            else:
                publication_date = None
            
            journal = article_data.get('Journal',{}).get('Title','')


            pub_types = article_data.get('PublicationTypeList',[])
            study_type = self._determine_study_type(pub_types)


            mesh_list = medline.get('MeshHeadingList', [])
            mesh_terms = [str(mesh['DescriptorName']) for mesh in mesh_list]

            author_list = article_data.get('AuthorList', [])
            authors = []
            for author in author_list[:10]:
                name = f"{author.get('LastName', '')} {author.get('ForeName', '')}".strip()
                aff_info = author.get('AffiliationInfo', [])
                affiliation = aff_info[0].get('Affiliation', '') if aff_info else ''
                if name:
                    authors.append({"name": name, "affiliation": affiliation})
            

            article_ids = pubmed_data.get('ArticleIdList', [])
            doi = None
            for aid in article_ids:
                if aid.attributes.get('IdType') == 'doi':
                    doi = str(aid)
                    break
            return {
                "id": pmid,
                "pmid": pmid,
                "doi": doi,
                "title": title,
                "abstract": abstract,
                "publication_date": publication_date,
                "journal": journal,
                "study_type": study_type,
                "mesh_terms": mesh_terms,
                "authors": authors,
                "citation_count": 0,  # Would need separate API call
                "sample_size": None,  # Would need text extraction
                "has_full_text": False,
                "full_text_url": None,
            }

        except Exception as e:
            logger.error(f"Error parsing article: {e}")
            return None
    

    def _determine_study_type(self,pub_types: List[str]) -> str:
        pub_type_strs = [str(pt) for pt in pub_types]

        if any('Meta-Analysis' in pt for pt in pub_type_strs):
            return 'Meta-Analysis'
        
        if any('Systematic Review' in pt for pt in pub_type_strs):
            return 'Systematic Review'

        if any('Randomized Controlled Trial' in pt for pt in pub_type_strs):
            return 'Randomized Controlled Trial'
        
        if any('Clinical Trial' in pt for pt in pub_type_strs):
            return 'Clinical Trial'

        if any('Cohort' in pt or 'Prospective' in pt for pt in pub_type_strs):
            return 'Cohort Study'
        
        if any('Case-Control' in pt for pt in pub_type_strs):
            return 'Case-Control Study'
        
        if any('Case Report' in pt for pt in pub_type_strs):
            return 'Case Report'
        
        if any('Review' in pt for pt in pub_type_strs):
            return 'Review'
        
        return 'Other'

if __name__ == "__main__":
    service = PubMedService()
    pmids = service.search("diabetes treatment", max_results=5, min_year=2023)
    print(f"Found PMIDs: {pmids}")

    if pmids:
        abstracts = service.fetch_abstracts(pmids[:5])
        print(f"\nFetched {len(abstracts)} abstracts")
        
        if abstracts:
            service.save_to_db(abstracts)
            print(f"\nExample abstract:")
            print(f"PMID: {abstracts[0]['pmid']}")
            print(f"Title: {abstracts[0]['title']}")
            print(f"Study Type: {abstracts[0]['study_type']}")
            print(f"Abstract: {abstracts[0]['abstract'][:200]}...")
        
