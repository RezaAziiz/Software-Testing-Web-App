import React, { useEffect, useRef } from "react";
import { useSplitPane } from "../../../hooks/useSplitPane";
import CfgCytoscapeViewport from "./CfgCytoscapeViewport";
import { CfgTooltipContent } from "./CfgTooltipContent";

import cytoscape from "cytoscape";
import { highlightJavaCode } from "../../../utils/javaHighlighter";

type CfgFullscreenModalProps = {
  isOpen: boolean;
  onClose: () => void;
  elements: cytoscape.ElementDefinition[];
  sourceCode: string | null;
  highlightedLines: { start: number; end: number } | null;
  modalCyRef: React.MutableRefObject<cytoscape.Core | null>;
  setModalCyInstance: (cy: cytoscape.Core | null) => void;
  modalTooltip: {
    visible: boolean;
    x: number;
    y: number;
    content: string;
    codeContent: string;
  };
  initialSplitPercent?: number;
  /** If provided, renders this URL in an iframe on the left panel instead of plain source code */
  jacocoUrl?: string | null;
};

export const CfgFullscreenModal: React.FC<CfgFullscreenModalProps> = ({
  isOpen,
  onClose,
  elements,
  sourceCode,
  highlightedLines,
  modalCyRef,
  setModalCyInstance,
  modalTooltip,
  initialSplitPercent = 45,
  jacocoUrl,
}) => {
  const { splitPercent, isDragging, startSplitResize, setSplitPercent } = useSplitPane(initialSplitPercent);

  // Reset split percent when modal is opened or initialSplitPercent changes
  useEffect(() => {
    if (isOpen) {
      setSplitPercent(initialSplitPercent);
    }
  }, [isOpen, initialSplitPercent, setSplitPercent]);

  const modalCodeContainerRef = useRef<HTMLDivElement>(null);
  const modalHighlightRef = useRef<HTMLDivElement>(null);

  // Auto-scroll the code panel inside the modal when a node is clicked
  useEffect(() => {
    if (isOpen && highlightedLines && modalHighlightRef.current && modalCodeContainerRef.current) {
      const container = modalCodeContainerRef.current;
      const target = modalHighlightRef.current;

      const containerRect = container.getBoundingClientRect();
      const targetRect = target.getBoundingClientRect();
      const relativeTop = targetRect.top - containerRect.top + container.scrollTop;

      container.scrollTo({
        top: relativeTop - container.clientHeight / 3,
        behavior: 'smooth',
      });
    }
  }, [highlightedLines, isOpen]);

  if (!isOpen) return null;

  const isJacocoMode = !!jacocoUrl;
  const leftPanelLabel = isJacocoMode ? "Code Coverage (JaCoCo)" : "source.java";
  const subtitleText = isJacocoMode
    ? "Sisi Kiri: Laporan Code Coverage JaCoCo · Sisi Kanan: Grafik Aliran Kontrol (CFG)"
    : "Sisi Kiri: Kode Program · Sisi Kanan: Grafik Aliran Kontrol (CFG)";

  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        width: "100vw",
        height: "100vh",
        backgroundColor: "#1e1e24",
        zIndex: 9999,
        display: "flex",
        flexDirection: "column",
        animation: "cfgSlideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards",
      }}
    >
      {/* Modal Header */}
      <div
        style={{
          padding: "16px 24px",
          borderBottom: "1px solid rgba(255,255,255,0.08)",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexShrink: 0,
          background: "rgba(30, 30, 36, 0.95)",
        }}
      >
        <div style={{ display: "flex", flexDirection: "column" }}>
          <h2 style={{ margin: 0, fontSize: 16, fontWeight: 600, color: "#f8fafc" }}>
            Struktur Aliran Kontrol Program (Control Flow Graph)
          </h2>
          <span style={{ fontSize: 12, color: "#64748b", marginTop: 2 }}>
            {subtitleText}
          </span>
        </div>
        <button
          onClick={onClose}
          title="Tutup Fullscreen"
          style={{
            padding: "6px 16px",
            background: "rgba(255,255,255,0.05)",
            border: "1px solid rgba(255,255,255,0.12)",
            borderRadius: 8,
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            transition: "all 0.2s",
            color: "#94a3b8",
            fontSize: 13,
            fontWeight: 500,
            letterSpacing: "0.02em",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = "rgba(239,68,68,0.15)";
            e.currentTarget.style.borderColor = "rgba(239,68,68,0.4)";
            e.currentTarget.style.color = "#ef4444";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = "rgba(255,255,255,0.05)";
            e.currentTarget.style.borderColor = "rgba(255,255,255,0.12)";
            e.currentTarget.style.color = "#94a3b8";
          }}
        >
          Tutup
        </button>
      </div>

      {/* Main split content area */}
      <div style={{ display: "flex", flex: 1, position: "relative", minHeight: 0, width: "100%" }}>

        {/* Left Panel */}
        {isJacocoMode ? (
          /* JaCoCo HTML iframe mode */
          <div
            style={{
              width: `${splitPercent}%`,
              height: "100%",
              backgroundColor: "#ffffff",
              borderRight: splitPercent > 0 ? "1px solid rgba(255,255,255,0.08)" : "none",
              overflow: "hidden",
              boxSizing: "border-box",
              flexShrink: 0,
              position: "relative",
            }}
          >
            {splitPercent > 0 && (
              <>
                {/* Tab bar mimicking a browser tab */}
                <div style={{
                  padding: "6px 16px",
                  background: "#f8f9fa",
                  borderBottom: "1px solid #dee2e6",
                  display: "flex",
                  alignItems: "center",
                  gap: 6,
                  fontSize: 11,
                  color: "#6c757d",
                  flexShrink: 0,
                }}>
                  <span style={{ fontFamily: "monospace", color: "#495057" }}>{leftPanelLabel}</span>
                </div>
                <iframe
                  src={jacocoUrl!}
                  style={{
                    width: "100%",
                    height: "calc(100% - 32px)",
                    border: "none",
                    display: "block",
                  }}
                  title="JaCoCo Code Coverage Report"
                />
                {/* Transparent drag-guard overlay: prevents iframe from swallowing mouse events during resize */}
                {isDragging && (
                  <div
                    style={{
                      position: "absolute",
                      inset: 0,
                      zIndex: 200,
                      cursor: "col-resize",
                    }}
                  />
                )}
              </>
            )}
          </div>
        ) : (
          /* Plain source code mode with syntax highlighting */
          <div
            ref={modalCodeContainerRef}
            style={{
              width: `${splitPercent}%`,
              height: "100%",
              backgroundColor: "#282a36",
              borderRight: splitPercent > 0 ? "1px solid rgba(255,255,255,0.08)" : "none",
              overflow: splitPercent > 0 ? "auto" : "hidden",
              fontFamily: "'Cascadia Code', 'Fira Code', 'JetBrains Mono', 'Consolas', monospace",
              fontSize: 12,
              lineHeight: 1.6,
              color: "#f8f8f2",
              padding: splitPercent > 0 ? "16px 0" : "0",
              boxSizing: "border-box",
              flexShrink: 0,
            }}
          >
            {sourceCode ? sourceCode.split("\n").map((line, idx) => {
              const lineNr = idx + 1;
              const isHighlighted =
                highlightedLines &&
                lineNr >= highlightedLines.start &&
                lineNr <= highlightedLines.end;

              return (
                <div
                  key={idx}
                  ref={isHighlighted ? modalHighlightRef : undefined}
                  style={{
                    display: "flex",
                    alignItems: "stretch",
                    minHeight: "1.6em",
                    backgroundColor: isHighlighted ? "rgba(59, 130, 246, 0.18)" : "transparent",
                    borderLeft: isHighlighted ? "4px solid #3b82f6" : "4px solid transparent",
                    paddingRight: 16,
                    transition: "background-color 0.3s ease, border-left-color 0.3s ease",
                    position: "relative",
                  }}
                >
                  {isHighlighted && (
                    <div style={{
                      position: "absolute",
                      inset: 0,
                      background: "linear-gradient(90deg, rgba(59, 130, 246, 0.12) 0%, transparent 80%)",
                      pointerEvents: "none",
                    }} />
                  )}
                  <span
                    style={{
                      display: "inline-block",
                      width: 42,
                      minWidth: 42,
                      textAlign: "right",
                      paddingRight: 12,
                      userSelect: "none",
                      color: isHighlighted ? "#93c5fd" : "#6272a4",
                      fontWeight: isHighlighted ? "bold" : "normal",
                      borderRight: "1px solid rgba(98,114,164,0.2)",
                      marginRight: 12,
                      flexShrink: 0,
                    }}
                  >
                    {lineNr}
                  </span>
                  <span
                    style={{
                      whiteSpace: "pre",
                      paddingRight: 16,
                      zIndex: 1,
                      color: isHighlighted ? "#93c5fd" : undefined,
                      fontWeight: isHighlighted ? 500 : undefined,
                    }}
                  >
                    {isHighlighted
                      ? (line || " ")  // Keep highlighted line as-is for clarity
                      : highlightJavaCode(line || " ")}
                  </span>
                </div>
              );
            }) : (
              <div style={{ padding: '12px 16px', color: '#6272a4' }}>
                Loading source code...
              </div>
            )}
          </div>
        )}

        {/* Draggable Divider */}
        <div
          onMouseDown={startSplitResize}
          style={{
            position: "absolute",
            top: 0,
            left: splitPercent === 0 ? 0 : `calc(${splitPercent}% - 6px)`,
            width: 12,
            height: "100%",
            cursor: "col-resize",
            zIndex: 100,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            backgroundColor: "transparent",
          }}
        >
          <div
            style={{
              position: "absolute",
              top: 0,
              bottom: 0,
              width: 2,
              backgroundColor: isDragging ? "#2563eb" : "rgba(255, 255, 255, 0.1)",
              transition: "background-color 0.2s ease",
            }}
          />
          <div
            style={{
              width: 24,
              height: 56,
              borderRadius: 12,
              backgroundColor: isDragging ? "#2563eb" : "#0b6af0ff",
              border: "1px solid " + (isDragging ? "#3b82f6" : "rgba(255,255,255,0.15)"),
              boxShadow: "0 10px 25px -5px rgba(0,0,0,0.4), 0 4px 10px -4px rgba(0,0,0,0.4)",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              gap: 4,
              transition: "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)",
              zIndex: 101,
              transform: isDragging ? "scale(1.08)" : "scale(1)",
            }}
          >
            <div style={{ width: 2, height: 16, backgroundColor: "rgba(255,255,255,0.5)", borderRadius: 1 }} />
            <div style={{ width: 2, height: 16, backgroundColor: "rgba(255,255,255,0.5)", borderRadius: 1 }} />
          </div>
        </div>

        {/* Right Panel: CFG */}
        <div
          style={{
            width: `${100 - splitPercent}%`,
            height: "100%",
            display: "flex",
            flexDirection: "column",
            background: "#1e1e24",
            overflow: "hidden",
          }}
        >
          <div
            className="relative flex-1"
            style={{ minHeight: 0, overflow: "visible", margin: 16 }}
            tabIndex={0}
          >
            {elements.length > 0 && (
              <CfgCytoscapeViewport
                elements={elements}
                cyRef={modalCyRef}
                setCyInstance={setModalCyInstance}
                zoomControlSuffix="modal"
              />
            )}

            {/* Modal Tooltip */}
            {modalTooltip.visible && (
              <div
                style={{
                  position: "absolute",
                  left: modalTooltip.x,
                  top: modalTooltip.y,
                  background: "#1e293b",
                  color: "#f8fafc",
                  padding: "8px 12px",
                  borderRadius: 8,
                  fontSize: 11,
                  maxWidth: 420,
                  maxHeight: 350,
                  overflowY: "auto",
                  pointerEvents: "none",
                  zIndex: 100,
                  boxShadow: "0 4px 16px rgba(0,0,0,0.35)",
                  lineHeight: 1.5,
                  border: "1px solid #334155",
                }}
              >
                <CfgTooltipContent text={modalTooltip.content} code={modalTooltip.codeContent || undefined} />
              </div>
            )}
          </div>

          {/* Panel Footer */}
          <div
            style={{
              padding: "8px 24px 12px",
              borderTop: "1px solid rgba(255,255,255,0.08)",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              flexShrink: 0,
              background: "rgba(30, 30, 36, 0.95)",
            }}
          >
            <span style={{ fontSize: 11, color: "#64748b" }}>
              {elements.filter(e => !e.data.source).length} nodes · {elements.filter(e => e.data.source).length} edges
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
export default CfgFullscreenModal;
