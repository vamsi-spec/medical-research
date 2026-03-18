import React, { useState } from "react";
import { Download, FileText, Copy } from "lucide-react";
import Button from "../ui/Button";
import Modal from "../ui/Modal";
import { exportCitations } from "../../lib/citationExport";
import { showToast } from "../../lib/toast";
import jsPDF from "jspdf";

const ExportMenu = ({ isOpen, onClose, messages }) => {
  const [exporting, setExporting] = useState(false);

  const exportAsText = () => {
    const text = messages
      .map((msg, idx) => {
        if (msg.type === "user") {
          return `[User]: ${msg.content}\n`;
        } else {
          const citations = msg.data.citations || [];
          const citationText =
            citations.length > 0
              ? `\n\nReferences:\n${citations.map((c, i) => `[${i + 1}] ${c.title} (PMID: ${c.pmid})`).join("\n")}`
              : "";
          return `[Assistant]: ${msg.data.answer}${citationText}\n`;
        }
      })
      .join("\n---\n\n");

    const blob = new Blob([text], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `medical-conversation-${Date.now()}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    showToast.success("Exported as text file");
    onClose();
  };

  const exportAsPDF = async () => {
    setExporting(true);

    try {
      const pdf = new jsPDF();
      let yPos = 20;
      const pageHeight = pdf.internal.pageSize.height;
      const margin = 20;
      const lineHeight = 7;

      // Title
      pdf.setFontSize(16);
      pdf.setFont(undefined, "bold");
      pdf.text("Medical Research Conversation", margin, yPos);
      yPos += 10;

      pdf.setFontSize(10);
      pdf.setFont(undefined, "normal");
      pdf.text(`Generated: ${new Date().toLocaleString()}`, margin, yPos);
      yPos += 15;

      // Content
      messages.forEach((msg, idx) => {
        // Check if we need a new page
        if (yPos > pageHeight - 30) {
          pdf.addPage();
          yPos = 20;
        }

        if (msg.type === "user") {
          pdf.setFont(undefined, "bold");
          pdf.text("Q:", margin, yPos);
          pdf.setFont(undefined, "normal");

          const lines = pdf.splitTextToSize(msg.content, 170);
          lines.forEach((line) => {
            if (yPos > pageHeight - 30) {
              pdf.addPage();
              yPos = 20;
            }
            pdf.text(line, margin + 10, yPos);
            yPos += lineHeight;
          });
          yPos += 5;
        } else {
          pdf.setFont(undefined, "bold");
          pdf.text("A:", margin, yPos);
          pdf.setFont(undefined, "normal");

          const lines = pdf.splitTextToSize(msg.data.answer, 170);
          lines.forEach((line) => {
            if (yPos > pageHeight - 30) {
              pdf.addPage();
              yPos = 20;
            }
            pdf.text(line, margin + 10, yPos);
            yPos += lineHeight;
          });

          // Add citations if available
          if (msg.data.citations && msg.data.citations.length > 0) {
            yPos += 5;
            pdf.setFontSize(8);
            pdf.setFont(undefined, "italic");
            msg.data.citations.forEach((c, i) => {
              if (yPos > pageHeight - 30) {
                pdf.addPage();
                yPos = 20;
              }
              const citationText = `[${i + 1}] ${c.title} (PMID: ${c.pmid})`;
              const citLines = pdf.splitTextToSize(citationText, 160);
              citLines.forEach((line) => {
                pdf.text(line, margin + 15, yPos);
                yPos += 6;
              });
            });
            pdf.setFontSize(10);
            pdf.setFont(undefined, "normal");
          }

          yPos += 10;
        }
      });

      // Disclaimer on last page
      if (yPos > pageHeight - 60) {
        pdf.addPage();
        yPos = 20;
      }

      yPos += 10;
      pdf.setFontSize(8);
      pdf.setFont(undefined, "italic");
      const disclaimer =
        "Disclaimer: This information is for educational purposes only and does not constitute medical advice. Always consult qualified healthcare professionals.";
      const disclaimerLines = pdf.splitTextToSize(disclaimer, 170);
      disclaimerLines.forEach((line) => {
        pdf.text(line, margin, yPos);
        yPos += 5;
      });

      pdf.save(`medical-conversation-${Date.now()}.pdf`);
      showToast.success("Exported as PDF");
      onClose();
    } catch (error) {
      console.error("PDF export error:", error);
      showToast.error("Failed to export PDF");
    } finally {
      setExporting(false);
    }
  };

  const copyToClipboard = () => {
    const text = messages
      .map((msg) => {
        if (msg.type === "user") {
          return `Q: ${msg.content}`;
        } else {
          return `A: ${msg.data.answer}`;
        }
      })
      .join("\n\n");

    navigator.clipboard.writeText(text);
    showToast.success("Copied to clipboard");
    onClose();
  };

  const exportCitationsOnly = () => {
    const allCitations = [];
    messages.forEach((msg) => {
      if (msg.type === "assistant" && msg.data.citations) {
        allCitations.push(...msg.data.citations);
      }
    });

    if (allCitations.length === 0) {
      showToast.error("No citations to export");
      return;
    }

    const bibTeX = exportCitations.toBibTeX(allCitations);
    exportCitations.downloadFile(
      bibTeX,
      `citations-${Date.now()}.bib`,
      "text/plain",
    );
    showToast.success("Citations exported as BibTeX");
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Export Conversation"
      size="sm"
    >
      <div className="space-y-3">
        <Button
          onClick={exportAsText}
          variant="secondary"
          className="w-full justify-start"
        >
          <FileText className="w-5 h-5 mr-3" />
          Export as Text File
        </Button>

        <Button
          onClick={exportAsPDF}
          variant="secondary"
          className="w-full justify-start"
          loading={exporting}
        >
          <Download className="w-5 h-5 mr-3" />
          Export as PDF
        </Button>

        <Button
          onClick={copyToClipboard}
          variant="secondary"
          className="w-full justify-start"
        >
          <Copy className="w-5 h-5 mr-3" />
          Copy to Clipboard
        </Button>

        <Button
          onClick={exportCitationsOnly}
          variant="secondary"
          className="w-full justify-start"
        >
          <FileText className="w-5 h-5 mr-3" />
          Export Citations (BibTeX)
        </Button>

        <div className="pt-3 border-t border-slate-200 dark:border-slate-700">
          <p className="text-xs text-slate-500 dark:text-slate-400">
            {messages.length} messages will be exported
          </p>
        </div>
      </div>
    </Modal>
  );
};

export default ExportMenu;
