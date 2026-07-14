import React, { useMemo } from "react";
import CytoscapeComponent from "react-cytoscapejs";
import cytoscape from "cytoscape";

type CfgCytoscapeViewportProps = {
  elements: cytoscape.ElementDefinition[];
  cyRef: React.MutableRefObject<cytoscape.Core | null>;
  setCyInstance?: (cy: cytoscape.Core | null) => void;
  style?: React.CSSProperties;
  zoomControlSuffix?: string;
};

export const CfgCytoscapeViewport: React.FC<CfgCytoscapeViewportProps> = ({
  elements,
  cyRef,
  setCyInstance,
  style = { width: "100%", height: "100%" },
  zoomControlSuffix = "inline",
}) => {
  const presetLayout = useMemo(() => ({ name: "preset" }), []);

  const stylesheet: cytoscape.StylesheetCSS[] = useMemo(() => [
    {
      selector: "node",
      css: {
        shape: "ellipse",
        width: 52,
        height: 52,
        "background-color": "data(bgColor)",
        "border-width": 2.5,
        "border-color": "#111827",
        label: "data(label)",
        "text-valign": "center",
        "text-halign": "center",
        "font-size": "20px",
        "font-weight": "bold",
        color: "#111827",
        "text-wrap": "none",
      },
    },
    {
      selector: "node[?isMerge]",
      css: { label: "" },
    },
    {
      selector: "node[nodeType = 'START'], node[nodeType = 'END']",
      css: {
        "font-size": "14px",
        "text-valign": "center",
        "text-halign": "center",
        "background-color": "#ffffff",
        shape: "round-rectangle",
        width: 60,
        height: 40,
      } as any,
    },
    {
      selector: "node:selected",
      css: {
        "border-width": 4,
        "border-color": "#1D4ED8",
        "background-color": "#DBEAFE",
      },
    },
    {
      selector: "edge",
      css: {
        width: 2,
        "line-color": "data(lineColor)",
        "target-arrow-color": "data(lineColor)",
        "target-arrow-shape": "triangle",
        "curve-style": "bezier",
        "control-point-step-size": 60,
        label: "data(label)",
        "font-size": "16px",
        "font-weight": "bold",
        "text-background-color": "#f9fafb",
        "text-background-opacity": 1,
        "text-background-padding": "3px",
        "edge-text-rotation": "autorotate",
        color: "data(lineColor)",
      } as any,
    },
  ], []);

  return (
    <div style={{ position: "relative", width: "100%", height: "100%", ...style }}>
      <CytoscapeComponent
        elements={elements}
        layout={presetLayout}
        stylesheet={stylesheet}
        cy={(cy) => {
          cyRef.current = cy;
          if (setCyInstance) {
            setCyInstance(cy);
          }
        }}
        style={{
          width: "100%",
          height: "100%",
          background: "#fafbfc",
          borderRadius: 10,
          border: "1px solid rgba(255,255,255,0.08)",
        }}
        wheelSensitivity={0.5}
      />

      {/* Zoom Controls */}
      <div
        style={{
          position: "absolute",
          bottom: 12,
          right: 12,
          display: "flex",
          gap: 4,
          background: "rgba(255,255,255,0.9)",
          backdropFilter: "blur(8px)",
          borderRadius: 8,
          padding: 4,
          border: "1px solid #e5e7eb",
          boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
          zIndex: 10,
        }}
      >
        {[
          {
            label: "+",
            title: "Zoom In",
            action: () => {
              const cy = cyRef.current;
              if (cy) cy.zoom(cy.zoom() * 1.3);
            },
          },
          {
            label: "−",
            title: "Zoom Out",
            action: () => {
              const cy = cyRef.current;
              if (cy) cy.zoom(cy.zoom() * 0.75);
            },
          },
          {
            label: "⊞",
            title: "Fit",
            action: () => {
              const cy = cyRef.current;
              if (cy) cy.fit(undefined, 20);
            },
          },
        ].map(({ label, title, action }) => (
          <button
            key={`${zoomControlSuffix}-${label}`}
            title={title}
            onClick={action}
            style={{
              width: 30,
              height: 30,
              background: "transparent",
              border: "none",
              borderRadius: 6,
              fontSize: 15,
              fontWeight: 600,
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#374151",
              transition: "background 0.15s ease",
            }}
            onMouseEnter={(e) => (e.currentTarget.style.background = "#f3f4f6")}
            onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
          >
            {label}
          </button>
        ))}
      </div>
    </div>
  );
};
export default CfgCytoscapeViewport;
