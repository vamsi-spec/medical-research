import re
from typing import List,Dict
from loguru import logger


class MedicalTextPreprocessor:
    def __init__(self):
        self.medical_abbrevs = {
            'bp': 'blood pressure',
            'hr': 'heart rate',
            'rr': 'respiratory rate',
            'bmi': 'body mass index',
            'sbp': 'systolic blood pressure',
            'dbp': 'diastolic blood pressure',
            'bmi': 'body mass index',
            'chol': 'cholesterol',
            'hdl': 'high density lipoprotein cholesterol',
            'ldl': 'low density lipoprotein cholesterol',
            'er': 'emergency room',
            'hba1c': 'hemoglobin a1c'
        }

    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        
        text = re.sub(r'http\S+|www\S+','',text)

        text = re.sub(r'\S+@\S+','',text)

        text = re.sub(r'\s+','',text)

        text = text.strip()

        return text

    def chunk_abstract(
        self,
        title: str,
        abstract: str,
        chunk_size: int = 500,
        chunk_overlap: int = 50
    ) -> List[Dict[str,str]]:

        title = self.clean_text(title)
        abstract = self.clean_text(abstract)

        if len(abstract) < chunk_size:
            return [{'chunk_index': 0, 
             'text': f"{title}\n\n{abstract}",
             'chunk_size': len(abstract)
            }]

        sentences = self._split_sentences(abstract)

        chunks = []
        current_chunk = []
        current_length = len(title) + 2
        chunk_index = 0

        for sentence in sentences:
            sentence_length = len(sentence)
            if current_length + sentence_length > chunk_size and current_chunk:
                chunk_text = f"{title}\n\n{' '.join(current_chunk)}"
                chunks.append({
                    'chunk_index': chunk_index,
                    'text': chunk_text,
                    'chunk_size': len(chunk_text)
                })

                chunk_index += 1

                overlap_sentence = self._get_overlap_sentences(
                    current_chunk,
                    chunk_overlap
                )

                current_chunk = overlap_sentence
                current_length = len(title) + 2 + sum(len(s) for s in overlap_sentence)

            current_chunk.append(sentence)
            current_length += sentence_length

        if current_chunk:
            chunk_text = f"{title}\n\n{' '.join(current_chunk)}"
            chunks.append({
                'chunk_index': chunk_index,
                'text': chunk_text,
                'chunk_size': len(chunk_text)
            
            })

        return chunks


    def _split_sentences(self,text: str) -> List[str]:
        sentences = re.split(r'(?<=[.!?])\s+',text)

        sentences = [s.strip() for s in sentences if s.strip()]

        return sentences


    def _get_overlap_sentences(
        self,
        sentences: List[str],
        overlap_size: int
    ) -> List[str]:

        overlap_sentences = []
        current_length = 0

        for sentence in reversed(sentences):
            if current_length + len(sentence) > overlap_size:
                break

            overlap_sentences.append(sentence)
            current_length += len(sentence)

        return overlap_sentences

preprocessor = MedicalTextPreprocessor()

if __name__ == "__main__":
    dirty_text = """
    This is a medical abstract about diabetes. 
    Visit http://example.com for more info.
    Contact: doctor@hospital.com
    
    
    Multiple    spaces   here.
    """

    clean = preprocessor.clean_text(dirty_text)
    print("Original:", repr(dirty_text))
    print("Cleaned:", repr(clean))

    title = "Efficacy of Metformin in Type 2 Diabetes Management"
    abstract = """
    Background: Type 2 diabetes mellitus affects millions worldwide. 
    Metformin is a first-line treatment. However, optimal dosing strategies 
    remain debated. Methods: We conducted a randomized controlled trial 
    with 500 patients. Participants received either standard dosing or 
    titrated dosing of metformin. Primary outcome was HbA1c reduction. 
    Results: Titrated dosing showed 0.8% greater HbA1c reduction compared 
    to standard dosing (p<0.001). Adverse events were similar between groups. 
    Conclusion: Titrated metformin dosing provides superior glycemic control.
    """
    
    chunks = preprocessor.chunk_abstract(title, abstract, chunk_size=200, chunk_overlap=50)
    
    print(f"\n\nChunking test:")
    print(f"Abstract length: {len(abstract)}")
    print(f"Number of chunks: {len(chunks)}")
    
    for chunk in chunks:
        print(f"\nChunk {chunk['chunk_index']} ({chunk['chunk_size']} chars):")
        print(chunk['text'][:150] + "...")
