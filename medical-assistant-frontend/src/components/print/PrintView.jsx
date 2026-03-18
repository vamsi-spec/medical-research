import React, { useRef } from "react";
import { Printer } from "lucide-react";
import Button from "../ui/Button";
import { useReactToPrint } from "react-to-print";

const PrintView = ({ messages }) => {
  const printRef = useRef();

  const handlePrint = useReactToPrint({
    content: () => printRef.current,
    documentTitle: `Medical-Conversation-${new Date().toISOString().split("T")[0]}`,
  });

  return (
    <>
      <Button onClick={handlePrint} variant="secondary" className="text-sm">
        <Printer className="w-4 h-4 mr-2" />
        Print
      </Button>

      {/* Hidden print content */}
      <div style={{ display: "none" }}>
        <div ref={printRef} className="print-container">
          <style>{`
            @media print {
              body { 
                font-family: Arial, sans-serif;
                color: #000;
                background: #fff;
              }
              .print-container {
                padding: 20px;
              }
              .print-header {
                border-bottom: 2px solid #1e40af;
                padding-bottom: 10px;
                margin-bottom: 20px;
              }
              .print-message {
                margin-bottom: 20px;
                page-break-inside: avoid;
              }
              .print-question {
                font-weight: bold;
                margin-bottom: 5px;
              }
              .print-answer {
                margin-bottom: 10px;
                line-height: 1.6;
              }
              .print-citations {
                font-size: 12px;
                color: #666;
                margin-top: 10px;
                padding-top: 10px;
                border-top: 1px solid #ddd;
              }
              .print-footer {
                margin-top: 40px;
                padding-top: 20px;
                border-top: 2px solid #1e40af;
                font-size: 12px;
                color: #666;
              }
            }
          `}</style>

          <div className="print-header">
            <h1 style={{ fontSize: "24px", margin: 0 }}>
              Medical Research Conversation
            </h1>
            <p style={{ fontSize: "14px", color: "#666", margin: "5px 0 0 0" }}>
              Generated: {new Date().toLocaleString()}
            </p>
          </div>

          {messages.map((msg, idx) => (
            <div key={idx} className="print-message">
              {msg.type === "user" ? (
                <div>
                  <div className="print-question">Q: {msg.content}</div>
                </div>
              ) : (
                <div>
                  <div className="print-answer">
                    <strong>A:</strong> {msg.data.answer}
                  </div>

                  {msg.data.citations && msg.data.citations.length > 0 && (
                    <div className="print-citations">
                      <strong>References:</strong>
                      <ul style={{ margin: "5px 0", paddingLeft: "20px" }}>
                        {msg.data.citations.map((citation, i) => (
                          <li key={i}>
                            [{i + 1}] {citation.title} (PMID: {citation.pmid})
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {msg.data.confidence && (
                    <div
                      style={{
                        fontSize: "12px",
                        color: "#666",
                        marginTop: "5px",
                      }}
                    >
                      Confidence: {Math.round(msg.data.confidence * 100)}%
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}

          <div className="print-footer">
            <p>
              <strong>Disclaimer:</strong> This information is for educational
              purposes only and does not constitute medical advice. Always
              consult qualified healthcare professionals for medical guidance.
            </p>
            <p style={{ marginTop: "10px" }}>
              Source: Medical Research Assistant | Powered by PubMed & AI
            </p>
          </div>
        </div>
      </div>
    </>
  );
};

export default PrintView;
