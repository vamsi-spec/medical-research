import React, { useState } from "react";
import Modal from "../ui/Modal";
import Button from "../ui/Button";
import Card from "../ui/Card";
import Badge from "../ui/Badge";
import { medicalAPI } from "../../api/endpoints";
import { ExternalLink, Search } from "lucide-react";

const ClinicalTrialsModal = ({ isOpen, onClose }) => {
  const [condition, setCondition] = useState("");
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async () => {
    if (!condition.trim()) {
      setError("Please enter a medical condition");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await medicalAPI.searchClinicalTrials(
        condition,
        ["RECRUITING"],
        10,
      );
      setResults(data);
    } catch (err) {
      setError("Failed to search clinical trials. Please try again.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setCondition("");
    setResults(null);
    setError(null);
    onClose();
  };

  const getPhaseColor = (phase = "") => {
    if (phase.includes("PHASE3") || phase.includes("PHASE4")) return "success";
    if (phase.includes("PHASE2")) return "warning";
    return "info";
  };

  const copyNCTId = (nctId) => {
    navigator.clipboard.writeText(nctId);
    alert(`NCT ID ${nctId} copied to clipboard!`);
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Clinical Trials Search"
      size="lg"
    >
      <div className="space-y-4">
        {/* Search Input */}
        <div className="flex gap-2">
          <input
            type="text"
            value={condition}
            onChange={(e) => setCondition(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            placeholder="e.g., type 2 diabetes, breast cancer"
            className="medical-input flex-1"
          />
          <Button
            onClick={handleSearch}
            loading={loading}
            disabled={!condition.trim()}
          >
            <Search className="w-5 h-5" />
          </Button>
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
                Found {results.total_found} Recruiting Trials
              </h3>
              <Badge variant="info">ClinicalTrials.gov</Badge>
            </div>

            {results.trials && results.trials.length > 0 ? (
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {results.trials.map((trial, index) => (
                  <Card
                    key={index}
                    className="hover:shadow-md transition-shadow"
                  >
                    <div className="space-y-3">
                      {/* Title */}
                      <div>
                        <h4 className="font-semibold text-base text-slate-900 mb-2">
                          {trial.title}
                        </h4>
                      </div>

                      {/* Metadata */}
                      <div className="flex flex-wrap gap-2">
                        <Badge
                          variant={
                            trial.status === "RECRUITING"
                              ? "success"
                              : "default"
                          }
                        >
                          {trial.status}
                        </Badge>

                        {trial.phase && (
                          <Badge variant={getPhaseColor(trial.phase)}>
                            {trial.phase}
                          </Badge>
                        )}

                        {trial.enrollment && (
                          <Badge variant="default">
                            👥 {trial.enrollment} participants
                          </Badge>
                        )}
                      </div>

                      {/* Conditions */}
                      {trial.conditions?.length > 0 && (
                        <div>
                          <p className="text-xs font-medium text-slate-600 mb-1">
                            Conditions:
                          </p>
                          <p className="text-sm text-slate-700">
                            {trial.conditions.slice(0, 3).join(", ")}
                          </p>
                        </div>
                      )}

                      {/* Interventions */}
                      {trial.interventions?.length > 0 && (
                        <div>
                          <p className="text-xs font-medium text-slate-600 mb-1">
                            Interventions:
                          </p>
                          <p className="text-sm text-slate-700">
                            {trial.interventions.slice(0, 2).join(", ")}
                          </p>
                        </div>
                      )}

                      {/* Location */}
                      {trial.locations?.length > 0 && (
                        <div>
                          <p className="text-xs font-medium text-slate-600 mb-1">
                            Location:
                          </p>
                          <p className="text-sm text-slate-700">
                            {trial.locations[0].city},{" "}
                            {trial.locations[0].state},{" "}
                            {trial.locations[0].country}
                          </p>
                        </div>
                      )}

                      {/* Actions */}
                      <div className="flex gap-2 pt-2 border-t border-slate-200">
                        <button
                          onClick={() => copyNCTId(trial.nct_id)}
                          className="text-xs text-blue-700 hover:text-blue-800 font-medium"
                        >
                          📋 Copy NCT ID: {trial.nct_id}
                        </button>

                        <a
                          href={trial.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs text-blue-700 hover:text-blue-800 font-medium flex items-center gap-1 ml-auto"
                        >
                          View Details
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-slate-500">
                <p>No recruiting trials found for "{results.query}"</p>
              </div>
            )}
          </div>
        )}

        {/* Initial State */}
        {!results && !loading && (
          <div className="text-center py-8 text-slate-500">
            <Search className="w-12 h-12 mx-auto mb-3 text-slate-300" />
            <p className="text-sm">
              Enter a medical condition to search for recruiting clinical trials
            </p>
          </div>
        )}
      </div>
    </Modal>
  );
};

export default ClinicalTrialsModal;
