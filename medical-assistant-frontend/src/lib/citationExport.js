export const exportCitations = {
  toBibTeX: (citations) => {
    return citations
      .map((citation) => {
        return `@article{${citation.pmid},
    title={${citation.title}},
    author={Unknown},
    journal={PubMed},
    year={${citation.publication_year || "n.d."}},
    pmid={${citation.pmid}},
    note={Study Type: ${citation.study_type}}
  }`;
      })
      .join("\n\n");
  },

  toRIS: (citations) => {
    return citations
      .map((citation) => {
        return `TY  - JOUR
  TI  - ${citation.title}
  PY  - ${citation.publication_year || "n.d."}
  AN  - ${citation.pmid}
  N1  - Study Type: ${citation.study_type}
  ER  -`;
      })
      .join("\n\n");
  },

  toAPA: (citations) => {
    return citations
      .map((citation, idx) => {
        const year = citation.publication_year || "n.d.";
        return `[${idx + 1}] ${citation.title} (${year}). PubMed ID: ${citation.pmid}. Study Type: ${citation.study_type}.`;
      })
      .join("\n\n");
  },

  downloadFile: (content, filename, type = "text/plain") => {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  },
};
