import React, { useState } from "react";
import { Pill, FlaskConical, FileText } from "lucide-react";
import Button from "../ui/Button";
import DrugInteractionModal from "./DrugInteractionModal";

const ToolsMenu = () => {
  const [showDrugModal, setShowDrugModal] = useState(false);

  return (
    <>
      <div className="p-4 border-t border-slate-200 bg-white">
        <p className="text-xs font-medium text-slate-600 mb-3">Medical Tools</p>
        <div className="space-y-2">
          <Button
            onClick={() => setShowDrugModal(true)}
            variant="secondary"
            className="w-full justify-start text-sm"
          >
            <Pill className="w-4 h-4 mr-2" />
            Drug Interactions
          </Button>

          <Button
            variant="secondary"
            className="w-full justify-start text-sm opacity-50 cursor-not-allowed"
            disabled
          >
            <FlaskConical className="w-4 h-4 mr-2" />
            Clinical Trials
          </Button>

          <Button
            variant="secondary"
            className="w-full justify-start text-sm opacity-50 cursor-not-allowed"
            disabled
          >
            <FileText className="w-4 h-4 mr-2" />
            Medical Codes
          </Button>
        </div>
      </div>

      <DrugInteractionModal
        isOpen={showDrugModal}
        onClose={() => setShowDrugModal(false)}
      />
    </>
  );
};

export default ToolsMenu;
