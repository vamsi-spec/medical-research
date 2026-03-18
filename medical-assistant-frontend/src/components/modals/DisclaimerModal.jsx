import React from "react";
import Modal from "../ui/Modal";
import Button from "../ui/Button";
import { AlertTriangle } from "lucide-react";

const DisclaimerModal = ({ isOpen, onAccept }) => {
  return (
    <Modal
      isOpen={isOpen}
      onClose={() => {}} // Cannot close without accepting
      title="Medical Information Disclaimer"
      size="lg"
    >
      <div className="space-y-4">
        <div className="bg-red-50 border-2 border-red-300 rounded-lg p-4 flex items-start gap-3">
          <AlertTriangle className="w-6 h-6 text-red-600 flex-shrink-0 mt-1" />
          <div>
            <h3 className="font-bold text-red-900 mb-2">
              Important Legal Notice
            </h3>
            <p className="text-sm text-red-800">
              This is an educational tool only. It is not a substitute for
              professional medical advice.
            </p>
          </div>
        </div>

        <div className="prose prose-sm max-w-none">
          <h4 className="font-bold text-slate-900">Terms of Use</h4>

          <p className="text-slate-700">
            By using this Medical Research Assistant, you acknowledge and agree
            to the following:
          </p>

          <ol className="text-slate-700 space-y-2">
            <li>
              <strong>Not Medical Advice:</strong> This system provides general
              medical information from peer-reviewed literature for educational
              purposes only. It does not provide medical advice, diagnosis, or
              treatment recommendations.
            </li>

            <li>
              <strong>Consult Healthcare Professionals:</strong> Always seek the
              advice of qualified healthcare providers with any questions
              regarding medical conditions. Never disregard professional medical
              advice or delay seeking it because of information from this
              system.
            </li>

            <li>
              <strong>Emergency Situations:</strong> If you are experiencing a
              medical emergency, call 911 (or your local emergency number)
              immediately. Do not rely on this system for emergency medical
              guidance.
            </li>

            <li>
              <strong>Accuracy Limitations:</strong> While this system uses
              peer-reviewed medical literature, AI-generated responses may
              contain errors or omissions. Always verify critical information
              with healthcare professionals and primary sources.
            </li>

            <li>
              <strong>No Doctor-Patient Relationship:</strong> Use of this
              system does not create a doctor-patient relationship. Information
              provided is general and not tailored to your specific medical
              situation.
            </li>

            <li>
              <strong>Privacy:</strong> Do not enter personal health
              information. This system is designed for general medical research
              queries only.
            </li>
          </ol>

          <p className="text-slate-700 font-medium mt-4">
            By clicking "I Accept," you confirm that you have read, understood,
            and agree to these terms and will use this system responsibly for
            educational purposes only.
          </p>
        </div>

        <div className="flex gap-3 pt-4">
          <Button onClick={onAccept} className="flex-1">
            I Accept - Continue to Medical Research Assistant
          </Button>
        </div>

        <p className="text-xs text-slate-500 text-center">
          Last Updated: {new Date().toLocaleDateString()}
        </p>
      </div>
    </Modal>
  );
};

export default DisclaimerModal;
