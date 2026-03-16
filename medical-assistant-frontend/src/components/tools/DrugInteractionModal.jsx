import React, { useState } from "react";
import Modal from "../ui/Modal";
import Button from "../ui/Button";
import Card from "../ui/Card";
import { medicalAPI } from "../../api/endpoints";
import { AlertTriangle, CheckCircle } from "lucide-react";

const DrugInteractionModal = ({ isOpen, onClose }) => {
  const [drug1, setDrug1] = useState("");
  const [drug2, setDrug2] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleCheck = async () => {
    if (!drug1.trim() || !drug2.trim()) {
      setError("Please enter both drug names");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await medicalAPI.checkDrugInteraction(drug1, drug2);
      setResult(data);
    } catch (err) {
      setError("Failed to check interaction. Please try again.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setDrug1("");
    setDrug2("");
    setResult(null);
    setError(null);
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Drug Interaction Checker"
      size="md"
    >
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            First Drug
          </label>
          <input
            type="text"
            value={drug1}
            onChange={(e) => setDrug1(e.target.value)}
            placeholder="e.g., warfarin"
            className="medical-input"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Second Drug
          </label>
          <input
            type="text"
            value={drug2}
            onChange={(e) => setDrug2(e.target.value)}
            placeholder="e.g., aspirin"
            className="medical-input"
          />
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        <Button
          onClick={handleCheck}
          loading={loading}
          disabled={!drug1.trim() || !drug2.trim()}
          className="w-full"
        >
          Check Interaction
        </Button>

        {result && (
          <Card
            className={`${
              result.interaction_found
                ? result.severity === "Major"
                  ? "bg-red-50 border-red-300"
                  : result.severity === "Moderate"
                    ? "bg-yellow-50 border-yellow-300"
                    : "bg-blue-50 border-blue-300"
                : "bg-green-50 border-green-300"
            }`}
          >
            <div className="flex items-start gap-3">
              {result.interaction_found ? (
                <AlertTriangle
                  className={`w-6 h-6 flex-shrink-0 ${
                    result.severity === "Major"
                      ? "text-red-600"
                      : result.severity === "Moderate"
                        ? "text-yellow-600"
                        : "text-blue-600"
                  }`}
                />
              ) : (
                <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0" />
              )}

              <div className="flex-1">
                <h3 className="font-bold text-lg mb-2">
                  {result.interaction_found
                    ? "⚠️ Interaction Found"
                    : "✅ No Interaction"}
                </h3>

                {result.interaction_found && (
                  <p className="text-sm font-medium mb-2">
                    Severity:{" "}
                    <span className="font-bold">{result.severity}</span>
                  </p>
                )}

                <p className="text-sm mb-3">{result.description}</p>

                {result.clinical_recommendation && (
                  <div className="bg-white rounded p-3 border border-slate-200">
                    <p className="text-sm font-medium mb-1">
                      Clinical Recommendation:
                    </p>
                    <p className="text-sm text-slate-700">
                      {result.clinical_recommendation}
                    </p>
                  </div>
                )}

                <p className="text-xs text-slate-600 mt-3">
                  Source: {result.data_source}
                </p>
              </div>
            </div>
          </Card>
        )}
      </div>
    </Modal>
  );
};

export default DrugInteractionModal;
