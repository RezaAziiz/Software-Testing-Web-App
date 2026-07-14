import React from "react";
import { highlightJavaCode } from "../../../utils/javaHighlighter";

type CfgTooltipContentProps = {
  text: string;
  code?: string;
};

export const CfgTooltipContent: React.FC<CfgTooltipContentProps> = ({ text, code }) => (
  <>
    <span style={{ whiteSpace: "pre-wrap" }}>{text}</span>
    {code && (
      <div
        style={{
          marginTop: 6,
          padding: "6px 8px",
          background: "#0f172a",
          borderRadius: 4,
          border: "1px solid #334155",
          fontFamily: "'Cascadia Code', 'Fira Code', 'JetBrains Mono', 'Consolas', monospace",
          fontSize: 11,
          lineHeight: 1.6,
          whiteSpace: "pre-wrap",
          overflowX: "auto",
          color: "#e2e8f0",
        }}
      >
        <div style={{ color: "#64748b", fontSize: 10, marginBottom: 4, fontFamily: "inherit", fontWeight: 600, letterSpacing: 0.5 }}>ISI KODE</div>
        {highlightJavaCode(code)}
      </div>
    )}
  </>
);
