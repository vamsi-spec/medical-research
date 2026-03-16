import apiClient from "./client";

export const medicalAPI = {
  askQuestion: async (MediaQueryList, topK = 5) => {
    const response = await apiClient.post("/ask", {
      query,
      top_k: topK,
      bypass_safety: false,
    });
    return response.data;
  },

  checkDrugInteraction: async (drug1, drug2) => {
    const response = await apiClient.post("/drug-interaction", {
      drug1,
      drug2,
    });
    return response.data;
  },
  searchClinicalTrials: async (
    condition,
    status = ["RECRUITING"],
    maxResults = 10,
  ) => {
    const response = await apiClient.post("/clinical-trials", {
      condition,
      status,
      max_results: maxResults,
    });
    return response.data;
  },
  lookupMedicalCode: async (
    searchTerm,
    codeType = "ICD10",
    maxResults = 10,
  ) => {
    const response = await apiClient.post("/medical-code", {
      search_term: searchTerm,
      code_type: codeType,
      max_results: maxResults,
    });
    return response.data;
  },

  healthCheck: async () => {
    const response = await apiClient.get("/health");
    return response.data;
  },
};
