import React from "react";
import { MousePointerClick } from "lucide-react";


type CfgTooltipContentProps = {
  nodeLabel?: string;
  nodeType?: string;
  lineStart?: number | null;
  lineEnd?: number | null;
  code?: string;
  statusText?: string;
};

export const CfgTooltipContent: React.FC<CfgTooltipContentProps> = ({ 
  nodeLabel, 
  nodeType, 
  lineStart, 
  lineEnd, 
  code,
  statusText 
}) => {
  const isNumeric = /^\d+$/.test(nodeLabel || "");
  const displayLabel = isNumeric ? `Node ${nodeLabel}` : (nodeLabel || "");
  const typeStr = (nodeType || "").toUpperCase();
  const displayType = typeStr ? typeStr.charAt(0).toUpperCase() + typeStr.slice(1).toLowerCase() + " Node" : "";

  let lineInfo = "";
  let displayCode = code || "";

  // Hide line info and code for START, END, MERGE nodes
  if (["START", "END", "MERGE"].includes(typeStr)) {
    lineInfo = "";
    displayCode = "";
  } else {
    if (lineStart !== null && lineStart !== undefined) {
      if (lineEnd !== null && lineEnd !== undefined && lineEnd !== lineStart) {
        lineInfo = `${lineStart} - ${lineEnd}`;
      } else {
        lineInfo = `${lineStart}`;
      }
    }
    // Format code: add newline after semicolon
    if (displayCode) {
      displayCode = displayCode.replace(/;\s*/g, ';\n').trim();
    }
  }

  return (
    <div className="flex flex-col bg-white border border-[#d2d2d2] rounded-lg shadow-lg overflow-hidden text-slate-800" style={{ width: 260 }}>
      {/* Header */}
      {displayLabel && (
        <div className="flex justify-between items-center px-2 py-1.5 border-b border-[#e2e8f0] bg-[#f8fafc]">
          <span className="font-bold text-[#3758b2] text-[13px]">{displayLabel}</span>
          <div className="flex gap-1">
            {statusText && (
              <span className={`text-[10px] px-1.5 py-0.5 border rounded font-medium ${
                statusText.includes("Partially") ? "bg-yellow-50 text-yellow-600 border-yellow-200" :
                statusText.includes("Not") ? "bg-red-50 text-red-600 border-red-200" :
                "bg-green-50 text-green-600 border-green-200"
              }`}>
                {statusText}
              </span>
            )}
            {displayType && (
              <span className="text-[10px] px-1.5 py-0.5 border border-[#cbd5e1] rounded bg-white text-slate-500 font-medium">
                {displayType}
              </span>
            )}
          </div>
        </div>
      )}

      {/* Body */}
      {(lineInfo || displayCode) && (
        <div className="px-2 py-2 text-xs bg-white border-b border-[#e2e8f0]">
          {lineInfo && <div className="text-slate-500 mb-1.5">Baris kode: {lineInfo}</div>}
          {displayCode && (
            <div
              className="bg-[#f1f5f9] border border-[#e2e8f0] rounded-md p-1.5 overflow-x-auto text-[11px] text-slate-600 whitespace-pre-wrap"
              style={{
                fontFamily: "'Cascadia Code', 'Fira Code', 'JetBrains Mono', 'Consolas', monospace",
              }}
            >
              {displayCode}
            </div>
          )}
        </div>
      )}

      {/* Footer */}
      {(lineInfo || displayCode) && (
        <div className="px-2 py-1.5 bg-[#f8fafc] flex items-center justify-center gap-1.5 text-[11px] text-slate-500 font-medium hover:text-slate-700 transition-colors">
          <MousePointerClick size={12} />
          <span>Klik untuk menyorot kode sumber</span>
        </div>
      )}
    </div>
  );
};

