import React, { useState } from "react";
import Modal from "../ui/Modal";
import Button from "../ui/Button";
import Card from "../ui/Card";
import Badge from "../ui/Badge";
import { medicalAPI } from "../../api/endpoints";
import { Search, Copy, CheckCircle } from "lucide-react";

const MedicalCodeModal = ({ isOpen, onClose }) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [codeType, setCodeType] = useState("ICD10");
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [copiedCode, setCopiedCode] = useState(null);

  const handleSearch = async () => {
    if (!searchTerm.trim()) {
      setError("Please enter a search term");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await medicalAPI.lookupMedicalCode(searchTerm, codeType, 15);
      setResults(data);
    } catch (err) {
      const backendMessage =
        err.response?.data?.detail ||
        "Failed to lookup medical codes. Please try again.";
      setError(`Error: ${backendMessage}`);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setSearchTerm("");
    setCodeType("ICD10");
    setResults(null);
    setError(null);
    setCopiedCode(null);
    onClose();
  };

  const copyCode = (code) => {
    navigator.clipboard.writeText(code);
    setCopiedCode(code);
    setTimeout(() => setCopiedCode(null), 2000);
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Medical Code Lookup"
      size="lg"
    >
      <div className="space-y-4">
        {/* Search Controls */}
        <div className="space-y-3">
          {/* Code Type Selection */}
          <div className="flex gap-2">
            <button
              onClick={() => setCodeType("ICD10")}
              className={`flex-1 py-2 px-4 rounded-lg font-medium transition-colors ${
                codeType === "ICD10"
                  ? "bg-blue-700 text-white"
                  : "bg-slate-100 text-slate-700 hover:bg-slate-200"
              }`}
            >
              ICD-10
            </button>
            <button
              onClick={() => setCodeType("CPT")}
              className={`flex-1 py-2 px-4 rounded-lg font-medium transition-colors ${
                codeType === "CPT"
                  ? "bg-blue-700 text-white"
                  : "bg-slate-100 text-slate-700 hover:bg-slate-200"
              }`}
            >
              CPT
            </button>
          </div>

          {/* Search Input */}
          <div className="flex gap-2">
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && handleSearch()}
              placeholder={
                codeType === "ICD10"
                  ? "e.g., diabetes, E11.9"
                  : "e.g., office visit, 99213"
              }
              className="medical-input flex-1"
            />
            <Button
              onClick={handleSearch}
              loading={loading}
              disabled={!searchTerm.trim()}
            >
              <Search className="w-5 h-5" />
            </Button>
          </div>

          {/* Info Badge */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <p className="text-xs text-blue-800">
              {codeType === "ICD10"
                ? "🔍 ICD-10: Diagnosis codes from National Library of Medicine"
                : "🔍 CPT: Procedure codes (public subset only)"}
            </p>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {/* Results */}
        {results && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-lg">
                Found {results.total_found} {results.code_type} Code
                {results.total_found !== 1 ? "s" : ""}
              </h3>
              <Badge variant="info">
                {results.code_type === "ICD10" ? "NLM API" : "Public Dataset"}
              </Badge>
            </div>

            {results.codes && results.codes.length > 0 ? (
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {results.codes.map((codeItem, index) => (
                  <Card
                    key={index}
                    className="hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex-1">
                        {/* Code and Description */}
                        <div className="flex items-center gap-2 mb-2">
                          <span className="font-mono font-bold text-lg text-blue-700">
                            {codeItem.code}
                          </span>
                          <button
                            onClick={() => copyCode(codeItem.code)}
                            className="text-slate-400 hover:text-slate-600 transition-colors"
                            title="Copy code"
                          >
                            {copiedCode === codeItem.code ? (
                              <CheckCircle className="w-4 h-4 text-green-600" />
                            ) : (
                              <Copy className="w-4 h-4" />
                            )}
                          </button>
                        </div>

                        <p className="text-sm text-slate-700 mb-2">
                          {codeItem.description}
                        </p>

                        {/* Metadata */}
                        <div className="flex flex-wrap gap-2">
                          {codeItem.category && (
                            <Badge variant="default">{codeItem.category}</Badge>
                          )}

                          {codeItem.billable !== undefined && (
                            <Badge
                              variant={
                                codeItem.billable ? "success" : "default"
                              }
                            >
                              {codeItem.billable
                                ? "✓ Billable"
                                : "Not Billable"}
                            </Badge>
                          )}

                          {codeItem.code_system && (
                            <Badge variant="info">{codeItem.code_system}</Badge>
                          )}
                        </div>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-slate-500">
                <p>No codes found for "{results.search_term}"</p>
              </div>
            )}

            {/* CPT Disclaimer */}
            {results.code_type === "CPT" && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                <p className="text-xs text-yellow-800">
                  ⚠️ Note: This shows a public CPT code subset. Full CPT
                  database requires AMA license.
                </p>
              </div>
            )}
          </div>
        )}

        {/* Initial State */}
        {!results && !loading && (
          <div className="text-center py-8 text-slate-500">
            <Search className="w-12 h-12 mx-auto mb-3 text-slate-300" />
            <p className="text-sm mb-2">Search for medical codes</p>
            <div className="text-xs space-y-1">
              <p>• ICD-10: Diagnosis codes (e.g., "diabetes", "E11.9")</p>
              <p>• CPT: Procedure codes (e.g., "office visit", "99213")</p>
            </div>
          </div>
        )}
      </div>
    </Modal>
  );
};

export default MedicalCodeModal;
