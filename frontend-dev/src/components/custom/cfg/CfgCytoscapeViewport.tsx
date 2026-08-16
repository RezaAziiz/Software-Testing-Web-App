import React, { useMemo } from "react";
import CytoscapeComponent from "react-cytoscapejs";
import cytoscape from "cytoscape";
import dagre from "cytoscape-dagre";

import { ZoomIn, ZoomOut, Maximize } from "lucide-react";

// Register dagre layout extension
cytoscape.use(dagre);

type CfgCytoscapeViewportProps = {
  elements: cytoscape.ElementDefinition[];
  cyRef: React.MutableRefObject<cytoscape.Core | null>;
  setCyInstance?: (cy: cytoscape.Core | null) => void;
  style?: React.CSSProperties;
  zoomControlSuffix?: string;
  highlightedLines?: { start: number; end: number } | null;
};


export const CfgCytoscapeViewport: React.FC<CfgCytoscapeViewportProps> = ({
  elements,
  cyRef,
  setCyInstance,
  style = { width: "100%", height: "100%" },
  zoomControlSuffix = "inline",
  highlightedLines = null,
}) => {
  const dagreLayout = useMemo(() => ({
    name: "dagre",
    rankDir: "TB",               // Aliran dari atas ke bawah
    ranker: "network-simplex",   // Algoritma terbaik untuk meminimalkan edge crossing
    nodeSep: 140,                // Pemisahan horizontal antar node di tingkat yang sama
    rankSep: 180,                // Pemisahan vertikal antar tingkatan
    edgeSep: 60,                 // Pemisahan antar edge paralel
    animate: false,
    fit: true,
    padding: 50,
  }), []);

  const stylesheet: cytoscape.StylesheetCSS[] = useMemo(() => [
    {
      selector: "node",
      css: {
        shape: "ellipse",
        width: 100,
        height: 100,
        "background-color": "data(bgColor)",
        "border-width": 3,
        "border-color": "#111827",
        label: "data(label)",
        "text-valign": "center",
        "text-halign": "center",
        "font-size": "36px",
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
        "font-size": "24px",
        "text-valign": "center",
        "text-halign": "center",
        "background-color": "#ffffff",
        shape: "round-rectangle",
        width: 130,
        height: 65,
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
    // ── Edge default: LURUS (Sequence, True, False, Case, dll.) ──
    {
      selector: "edge",
      css: {
        width: 4,
        "line-color": "data(lineColor)",
        "target-arrow-color": "data(lineColor)",
        "target-arrow-shape": "triangle",
        "curve-style": "bezier",
        label: "data(label)",
        "font-size": "24px",
        "font-weight": "bold",
        "text-background-color": "#fafbfc",
        "text-background-opacity": 1,
        "text-background-padding": "6px",
        "edge-text-rotation": "autorotate",
        color: "data(lineColor)",
      } as any,
    },
    // ── Edge LENGKUNG: Back Edge, Break jauh, Return jauh ──
    {
      selector: "edge[?isCurved]",
      css: {
        "curve-style": "unbundled-bezier",
        "control-point-distances": "data(curveDistance)",
        "control-point-weights": 0.5,
        "edge-text-rotation": "none",
      } as any,
    },
  ], []);

  React.useEffect(() => {
    if (!cyRef.current) return;
    const cy = cyRef.current;
    
    // Clear selection
    cy.nodes().unselect();
    
    if (highlightedLines) {
      let nodesToSelect = cy.collection();
      cy.nodes().forEach(node => {
        const nodeType = (node.data('nodeType') ?? '').toUpperCase();
        if (nodeType === 'MERGE') return;

        const lineStart = node.data('lineStart');
        const lineEnd = node.data('lineEnd');
        if (lineStart !== undefined && lineStart !== null) {
          const end = lineEnd !== undefined && lineEnd !== null ? lineEnd : lineStart;
          if (highlightedLines.start >= lineStart && highlightedLines.start <= end) {
            nodesToSelect = nodesToSelect.union(node);
          } else if (lineStart >= highlightedLines.start && end <= (highlightedLines.end ?? highlightedLines.start)) {
            nodesToSelect = nodesToSelect.union(node);
          }
        }
      });
      
      if (nodesToSelect.length > 0) {
        nodesToSelect.select();
        // Hanya center jika nodesToSelect berjumlah kecil atau spesifik agar tidak terlalu zoom-out
        cy.animate({
          center: {
            eles: nodesToSelect
          },
          duration: 300
        });
      }
    }
  }, [highlightedLines, cyRef, elements]);

  return (
    <div style={{ position: "relative", width: "100%", height: "100%", ...style }}>
      <CytoscapeComponent
        elements={elements}
        layout={dagreLayout}
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
        className="group"
        style={{
          position: "absolute",
          bottom: 12,
          left: 12,
          display: "flex",
          flexDirection: "column",
          background: "#4b5563",
          borderRadius: 4,
          overflow: "hidden",
          border: "1px solid #374151",
          boxShadow: "0 2px 8px rgba(0,0,0,0.15)",
          zIndex: 10,
        }}
      >
        {[
          {
            icon: <ZoomIn size={14} />,
            label: "Zoom In",
            action: () => {
              const cy = cyRef.current;
              if (cy) cy.zoom(cy.zoom() * 1.3);
            },
          },
          {
            icon: <ZoomOut size={14} />,
            label: "Zoom Out",
            action: () => {
              const cy = cyRef.current;
              if (cy) cy.zoom(cy.zoom() * 0.75);
            },
          },
          {
            icon: <Maximize size={14} />,
            label: "Fit",
            action: () => {
              const cy = cyRef.current;
              if (cy) cy.fit(undefined, 20);
            },
          },
        ].map(({ icon, label, action }, index) => (
          <button
            key={`${zoomControlSuffix}-${label}`}
            onClick={action}
            className="flex items-center hover:bg-[#374151] transition-colors"
            style={{
              padding: "6px 10px",
              background: "transparent",
              border: "none",
              borderBottom: index !== 2 ? "1px solid #374151" : "none",
              cursor: "pointer",
              color: "#f9fafb",
            }}
          >
            {icon}
            <span className="text-[11px] whitespace-nowrap overflow-hidden max-w-0 opacity-0 group-hover:max-w-[80px] group-hover:opacity-100 group-hover:ml-2 transition-all duration-300 ease-in-out">
              {label}
            </span>
          </button>
        ))}
      </div>
    </div>
  );
};
export default CfgCytoscapeViewport;
