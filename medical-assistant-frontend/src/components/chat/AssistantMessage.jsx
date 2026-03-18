import React, { useState } from "react";
import { Bot, ExternalLink } from "lucide-react";
import ReactMarkdown from "react-markdown";
import Card from "../ui/Card";
import Badge from "../ui/Badge";
import Modal from "../ui/Modal";
import BookmarkButton from "../bookmarks/BookmarkButton";
import RatingButtons from "../feedback/RatingButtons";

const AssistantMessage = ({ data, messageIndex, onRate, query }) => {
  const [selectedCitation, setSelectedCitation] = useState(null);

  const {
    answer,
    citations = [],
    confidence,
    confidence_breakdown,
    evidence_summary,
    refused,
    safety,
    warning,
  } = data;

  if (refused) {
    return (
      <div className="flex justify-start mb-6">
        <div className="flex items-start gap-3 max-w-[90%]">
          <div className="flex-shrink-0 w-8 h-8 bg-red-500 rounded-full flex items-center justify-center">
            <Bot className="w-5 h-5 text-white" />
          </div>

          <Card className="border-red-300 bg-red-50">
            <div className="text-red-800">
              <h3 className="font-bold text-lg mb-2">⚠️ Safety Alert</h3>

              {safety?.category && (
                <p className="text-sm mb-2">
                  <strong>Category:</strong>{" "}
                  {safety.category.replace(/_/g, " ").toUpperCase()}
                </p>
              )}

              {safety?.refusal_reason && (
                <p className="text-sm mb-3">{safety.refusal_reason}</p>
              )}

              {safety?.suggested_action && (
                <div className="bg-white rounded p-3 border border-red-300 mt-3">
                  <p className="text-sm font-medium">Recommended Action:</p>
                  <p className="text-sm mt-1">{safety.suggested_action}</p>
                </div>
              )}
            </div>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start mb-6">
      <div className="flex items-start gap-3 max-w-[90%]">
        <div className="flex-shrink-0 w-8 h-8 bg-blue-700 rounded-full flex items-center justify-center">
          <Bot className="w-5 h-5 text-white" />
        </div>

        <div className="flex-1 space-y-3">
          <Card>
            <div className="prose prose-sm max-w-none text-slate-700">
              <ReactMarkdown>{answer}</ReactMarkdown>
            </div>

            {citations.length > 0 && (
              <div className="mt-4 pt-4 border-t border-slate-200">
                <p className="text-xs text-slate-600 mb-2 font-medium">
                  References:
                </p>

                <div className="flex flex-wrap gap-2">
                  {citations.map((citation) => (
                    <button
                      key={citation.index}
                      onClick={() => setSelectedCitation(citation)}
                      className="inline-flex items-center justify-center w-7 h-7 text-xs font-bold text-blue-700 bg-blue-100 hover:bg-blue-200 rounded cursor-pointer transition-colors"
                      title={citation.title}
                    >
                      {citation.index}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </Card>

          <div className="flex items-center gap-4 flex-wrap">
            {evidence_summary && (
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-600 font-medium">
                  Evidence:
                </span>

                {evidence_summary.level_a_count > 0 && (
                  <Badge variant="success">
                    {evidence_summary.level_a_count} Level A
                  </Badge>
                )}

                {evidence_summary.level_b_count > 0 && (
                  <Badge variant="warning">
                    {evidence_summary.level_b_count} Level B
                  </Badge>
                )}

                {evidence_summary.level_c_count > 0 && (
                  <Badge variant="danger">
                    {evidence_summary.level_c_count} Level C
                  </Badge>
                )}
              </div>
            )}

            {confidence !== undefined && (
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-600 font-medium">
                  Confidence:
                </span>

                <span
                  className={`text-sm font-bold ${
                    confidence >= 0.85
                      ? "text-green-600"
                      : confidence >= 0.7
                        ? "text-yellow-600"
                        : "text-red-600"
                  }`}
                >
                  {Math.round(confidence * 100)}%
                </span>
              </div>
            )}
          </div>

          {warning && (
            <div className="bg-yellow-50 border border-yellow-300 rounded-lg px-3 py-2">
              <p className="text-xs text-yellow-800">⚠️ {warning}</p>
            </div>
          )}

          {confidence_breakdown && (
            <details className="text-xs">
              <summary className="cursor-pointer text-slate-600 hover:text-slate-900 font-medium">
                View detailed confidence breakdown
              </summary>

              <Card className="mt-2 bg-slate-50">
                <div className="space-y-1">
                  {Object.entries(confidence_breakdown).map(([key, value]) => (
                    <div key={key} className="flex justify-between">
                      <span className="text-slate-600 capitalize">
                        {key.replace(/_/g, " ")}:
                      </span>

                      <span className="font-medium text-slate-900">
                        {(value * 100).toFixed(0)}%
                      </span>
                    </div>
                  ))}
                </div>
              </Card>
            </details>
          )}
        </div>
      </div>

      {selectedCitation && (
        <Modal
          isOpen={true}
          onClose={() => setSelectedCitation(null)}
          title={`Citation [${selectedCitation.index}]`}
          size="md"
        >
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium text-slate-600">
                Title:
              </label>
              <p className="text-base text-slate-900 mt-1">
                {selectedCitation.title}
              </p>
            </div>

            <div>
              <label className="text-sm font-medium text-slate-600">
                PMID:
              </label>

              <a
                href={`https://pubmed.ncbi.nlm.nih.gov/${selectedCitation.pmid}/`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-700 hover:underline ml-2 inline-flex items-center gap-1"
              >
                {selectedCitation.pmid}
                <ExternalLink className="w-3 h-3" />
              </a>
            </div>

            <div>
              <label className="text-sm font-medium text-slate-600">
                Study Type:
              </label>

              <div className="mt-1">
                <Badge variant="info">{selectedCitation.study_type}</Badge>
              </div>
            </div>

            {selectedCitation.publication_year && (
              <div>
                <label className="text-sm font-medium text-slate-600">
                  Publication Year:
                </label>

                <p className="text-base text-slate-900 mt-1">
                  {selectedCitation.publication_year}
                </p>
              </div>
            )}
          </div>
        </Modal>
      )}
      {/* Actions Row */}
      <div className="flex items-center justify-between mt-3 pt-3 border-t border-slate-200 dark:border-slate-700">
        <RatingButtons messageIndex={messageIndex} onRate={onRate} />
        <BookmarkButton message={{ data, query }} messageIndex={messageIndex} />
      </div>
    </div>
  );
};

export default AssistantMessage;
