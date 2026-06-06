import React, { useEffect, useRef, useState } from "react";
import CytoscapeComponent from "react-cytoscapejs";
import cytoscape from "cytoscape";
import dagre from "cytoscape-dagre";
import PercentageCodeCoverage from "./PresentaseCodeCoverage";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import "../../index.css";

// Daftarkan plugin dagre ke cytoscape
cytoscape.use(dagre as any);

// Types
type CFGCardProps = {
  showCyclomaticComplexity?: boolean;
  showCodeCoverage?: boolean;
  codeCoveragePercentage?: number;
  nodesWithStatus?: Array<any>;
  edgesWithStatus?: Array<any>;
};

// Utility function to map tr_status to color
const getStatusColor = (status: string | undefined): string => {
  if (!status) return "#FFFFFF"; // Default white if no status
  switch (status.toUpperCase()) {
    case "Y": // Fully Executed
      return "#22c55e"; // Green
    case "S": // Partially Executed
      return "#eab308"; // Yellow
    case "N": // Not Executed
      return "#ef4444"; // Red
    default:
      return "#FFFFFF"; // Default white
  }
};

// Component
const CFGCard: React.FC<CFGCardProps> = ({
  showCyclomaticComplexity = false,
  showCodeCoverage = false,
  codeCoveragePercentage,
  nodesWithStatus,
  edgesWithStatus,
}) => {
  const apiUrl = import.meta.env.VITE_API_URL;
  let apiKey = import.meta.env.VITE_API_KEY;

  const sessionData = localStorage.getItem("session");
  if (sessionData != null) {
    const session = JSON.parse(sessionData);
    apiKey = session.token;
  }

  const queryParameters = new URLSearchParams(window.location.search);
  const modulId = queryParameters.get("topikModulId");

  // Cytoscape element array
  const [elements, setElements] = useState<cytoscape.ElementDefinition[]>([]);
  const [rawEdges, setRawEdges] = useState<any[]>([]);
  const [rawNodes, setRawNodes] = useState<any[]>([]);
  const [cyclomaticComplexity, setCyclomaticComplexity] = useState<
    number | null
  >(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // ref ke instance cytoscape agar bisa memanggil .fit() dll
  const cyRef = useRef<cytoscape.Core | null>(null);

  // Tooltip state
  const [tooltip, setTooltip] = useState<{
    visible: boolean;
    x: number;
    y: number;
    content: string;
  }>({ visible: false, x: 0, y: 0, content: "" });

  // Fetch data CFG
  const fetchCFG = async () => {
    // Use provided status data if available, otherwise fetch from API
    if (nodesWithStatus && edgesWithStatus) {
      setRawNodes(nodesWithStatus);
      setRawEdges(edgesWithStatus);

      // Konversi ke format Cytoscape dengan status colors
      const cyNodes: cytoscape.ElementDefinition[] = nodesWithStatus.map(
        (n: any) => {
          const nodeType: string = n.ms_node_type ?? "NORMAL";
          const isMerge = nodeType.toUpperCase() === "MERGE";
          const executionOrder = n.ms_execution_order;
          const trStatus: string = n.tr_status ?? "N";
          const bgColor = getStatusColor(trStatus);

          return {
            data: {
              id: n.ms_id_node,
              label: isMerge || !executionOrder ? "" : executionOrder,
              nodeType,
              isMerge,
              trStatus,
              tooltip: `Tipe: ${nodeType}\nStatus: ${trStatus === "Y"
                  ? "Executed"
                  : trStatus === "S"
                    ? "Partially Executed"
                    : "Not Executed"
                }\n\nIsi Kode:\n${n.ms_source_code ?? ""}`,
              bgColor,
            },
          };
        },
      );

      const cyEdges: cytoscape.ElementDefinition[] = edgesWithStatus.map(
        (e: any) => {
          const branchType: string = e.ms_branch_type ?? "";
          const isTrue = branchType.toUpperCase() === "TRUE";
          const isFalse = branchType.toUpperCase() === "FALSE";
          const label = isTrue ? "True" : isFalse ? "False" : "";
          const trStatus: string = e.tr_status ?? "N";
          const lineColor = getStatusColor(trStatus);

          return {
            data: {
              id: e.ms_id_edge,
              source: e.id_node_start ?? e.ms_id_start_node,
              target: e.id_node_finish ?? e.ms_id_finish_node,
              label,
              lineColor,
              trStatus,
              branchType,
            },
          };
        },
      );

      setElements([...cyNodes, ...cyEdges]);
      setLoading(false);
      return;
    }

    // Fallback: fetch from API (for generic CFG viewing without status)
    if (!modulId) {
      setLoading(false);
      return;
    }
    try {
      const res = await fetch(
        `${apiUrl}/modul/detailByIdTopikModul/${modulId}`,
        {
          method: "GET",
          headers: {
            Accept: "application/json",
            Authorization: `Bearer ${apiKey}`,
          },
        },
      );

      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const data = await res.json();
      const backendNodes: any[] = data?.data?.data_cfg?.nodes ?? [];
      const backendEdges: any[] = data?.data?.data_cfg?.edges ?? [];

      setRawNodes(backendNodes);
      setRawEdges(backendEdges);
      const backendCcRaw = data?.data?.data_modul?.ms_cc;
      const backendCc =
        backendCcRaw !== null && backendCcRaw !== undefined
          ? Number(backendCcRaw)
          : null;
      setCyclomaticComplexity(Number.isFinite(backendCc) ? backendCc : null);

      // Konversi ke format Cytoscape
      const cyNodes: cytoscape.ElementDefinition[] = backendNodes.map(
        (n: any) => {
          const nodeType: string = n.ms_node_type ?? n.node_type ?? "NORMAL";
          const isMerge = nodeType.toUpperCase() === "MERGE";
          const executionOrder = n.ms_execution_order ?? n.execution_order;
          return {
            data: {
              id: n.ms_id_node ?? n.id_node,
              label: isMerge || !executionOrder ? "" : executionOrder,
              nodeType,
              isMerge,
              tooltip: `Tipe: ${nodeType} \n\nIsi Kode:\n${n.ms_source_code ?? n.code_fragment ?? ""}`,
              bgColor: "#FFFFFF",
            },
          };
        },
      );

      const cyEdges: cytoscape.ElementDefinition[] = backendEdges.map(
        (e: any) => {
          const branchType: string = e.ms_branch_type ?? e.branch_type ?? "";
          const isTrue = branchType.toUpperCase() === "TRUE";
          const isFalse = branchType.toUpperCase() === "FALSE";
          const label = isTrue ? "True" : isFalse ? "False" : "";

          return {
            data: {
              id: e.ms_id_edge ?? e.id_edge,
              source: e.id_node_start ?? e.ms_id_start_node ?? e.id_start_node,
              target:
                e.id_node_finish ?? e.ms_id_finish_node ?? e.id_finish_node,
              label,
              lineColor: "black",
              branchType,
            },
          };
        },
      );

      setElements([...cyNodes, ...cyEdges]);
    } catch (err: any) {
      console.error("Failed to fetch CFG:", err);
      setError(err.message ?? "Gagal memuat CFG");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCFG();
  }, [modulId, nodesWithStatus, edgesWithStatus]);

  // Dagre layout config (Pastikan config ini konsisten)
  const layout = {
    name: "dagre",
    rankDir: "TB",
    nodeSep: 80,
    rankSep: 60,
    nodeDimensionsIncludeLabels: true, // Tambahan vital agar label tidak tertimpa
    ranker: "network-simplex", // Tambahan algoritma pencabangan optimal
    animate: false,
    fit: true,
    padding: 30,
  };

  // Re-layout & fit saat elements berubah
  useEffect(() => {
    if (!cyRef.current || elements.length === 0) return;
    const cy = cyRef.current;

    // Tunda render sedikit agar nodes tergambar di DOM & ukurannya bisa dibaca Dagre
    setTimeout(() => {
      cy.layout({
        ...layout,
        animate: true, // Saat dirender ulang, jalankan dengan animasi
        animationDuration: 500,
      } as any).run();
    }, 50);

    // Pasang event hover tooltip
    cy.off("mouseover", "node");
    cy.off("mouseout", "node");
    cy.off("mousemove", "node");

    cy.on("mouseover", "node", (evt) => {
      const node = evt.target;
      const container = cy.container();
      if (!container) return;
      const rect = container.getBoundingClientRect();
      const renderedPos = node.renderedPosition();
      setTooltip({
        visible: true,
        x: renderedPos.x + 30,
        y: renderedPos.y - 10,
        content: node.data("tooltip") ?? "",
      });
    });
    cy.on("mousemove", "node", (evt) => {
      const node = evt.target;
      const cy = cyRef.current;
      if (!cy) return;
      const container = cy.container();
      if (!container) return;
      const rect = container.getBoundingClientRect();
      // Use the original mouse event position relative to the container
      const originalEvt = evt.originalEvent;
      if (originalEvt) {
        setTooltip((t) => ({
          ...t,
          x: (originalEvt as MouseEvent).clientX - rect.left + 15,
          y: (originalEvt as MouseEvent).clientY - rect.top - 10,
        }));
      }
    });
    cy.on("mouseout", "node", () => {
      setTooltip((t) => ({ ...t, visible: false }));
    });
  }, [elements]);

  // Cytoscape stylesheet
  const stylesheet: cytoscape.StylesheetCSS[] = [
    {
      selector: "node",
      style: {
        shape: "ellipse",
        width: 52,
        height: 52,
        "background-color": "data(bgColor)",
        "border-width": 2.5,
        "border-color": "data(borderColor)",
        label: "data(label)",
        "text-valign": "center",
        "text-halign": "center",
        "font-size": "14px",
        "font-weight": "bold",
        color: "#111827",
        "text-wrap": "none",
      },
    },
    {
      // MERGE: node tanpa teks
      selector: "node[?isMerge]",
      style: { label: "" },
    },
    {
      // Node dipilih / hover
      selector: "node:selected",
      style: {
        "border-width": 4,
        "border-color": "#1D4ED8",
        "background-color": "#DBEAFE",
      },
    },
    {
      selector: "edge",
      style: {
        width: 2,
        "line-color": "data(lineColor)",
        "target-arrow-color": "data(lineColor)",
        "target-arrow-shape": "triangle",
        "curve-style": "straight", // Diubah menjadi straight agar lebih rapi
        label: "data(label)",
        "font-size": "13px",
        "font-weight": "bold",
        "text-background-color": "#f9fafb",
        "text-background-opacity": 1,
        "text-background-padding": "3px",
        // Hapus text-margin-y agar text label berada tepat di atas garis
        color: "data(lineColor)",
      },
    },
  ];

  // Loading skeleton
  if (loading) {
    return (
      <div className="p-6 bg-white rounded-lg shadow-lg h-full space-y-6">
        <div className="bg-gray-100 p-4 rounded-lg">
          <Skeleton className="h-5 w-32 bg-gray-200" />
        </div>
        <div className="bg-gray-100 p-4 rounded-lg">
          {[...Array(4)].map((_, i) => (
            <Skeleton key={i} className="h-5 w-full mb-4 bg-gray-200" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="h-full w-full">
      <Card>
        <CardHeader className="pt-6 pb-2">
          <CardTitle className="text-base module-title">
            Struktur Program
          </CardTitle>
        </CardHeader>

        <CardContent className="flex flex-col">
          <div className="w-full flex flex-row gap-3">
            {/* CFG Canvas */}
            <div className="w-1/2 flex flex-col">
              <p className="text-sm font-medium mb-2">Control Flow Graph</p>

              {error ? (
                <div className="h-96 flex items-center justify-center text-sm text-gray-400 bg-gray-50 rounded-lg border border-dashed border-gray-300">
                  <span>Belum ada data CFG untuk modul ini.</span>
                </div>
              ) : elements.length === 0 ? (
                <div className="h-96 flex items-center justify-center text-sm text-gray-400 bg-gray-50 rounded-lg border border-dashed border-gray-300">
                  <span>Data CFG tidak tersedia.</span>
                </div>
              ) : (
                <div className="relative" style={{ height: "24rem", overflow: "visible" }}>
                  {/* Cytoscape canvas */}
                  <CytoscapeComponent
                    elements={elements}
                    layout={layout as any}
                    stylesheet={stylesheet}
                    cy={(cy) => {
                      cyRef.current = cy;
                    }}
                    style={{
                      width: "100%",
                      height: "100%",
                      background: "#f9fafb",
                      borderRadius: 8,
                    }}
                    wheelSensitivity={0.5}
                  />

                  {/* Hover tooltip */}
                  {tooltip.visible && (
                    <div
                      style={{
                        position: "absolute",
                        left: tooltip.x,
                        top: tooltip.y,
                        background: "#1e293b",
                        color: "#f8fafc",
                        padding: "8px 12px",
                        borderRadius: 6,
                        fontSize: 11,
                        whiteSpace: "pre-wrap",
                        maxWidth: 320,
                        maxHeight: 250,
                        overflowY: "auto",
                        pointerEvents: "none",
                        zIndex: 100,
                        boxShadow: "0 4px 12px rgba(0,0,0,0.25)",
                        lineHeight: 1.5,
                      }}
                    >
                      {tooltip.content}
                    </div>
                  )}

                  {/* Mini tombol kontrol */}
                  <div
                    style={{
                      position: "absolute",
                      bottom: 8,
                      right: 8,
                      display: "flex",
                      gap: 4,
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
                        label: "-",
                        title: "Zoom Out",
                        action: () => {
                          const cy = cyRef.current;
                          if (cy) cy.zoom(cy.zoom() * 0.75);
                        },
                      },
                      {
                        label: "⊞",
                        title: "Fit",
                        action: () => cyRef.current?.fit(undefined, 20),
                      },
                    ].map(({ label, title, action }) => (
                      <button
                        key={label}
                        title={title}
                        onClick={action}
                        style={{
                          width: 28,
                          height: 28,
                          background: "#fff",
                          border: "1px solid #d1d5db",
                          borderRadius: 6,
                          fontSize: 14,
                          fontWeight: 700,
                          cursor: "pointer",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          boxShadow: "0 1px 4px rgba(0,0,0,0.10)",
                        }}
                      >
                        {label}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Panel kanan: Code Coverage */}
            <div className="w-1/2 flex flex-col items-center">
              {showCodeCoverage && codeCoveragePercentage !== undefined && (
                <>
                  <p className="text-sm font-medium mb-5">
                    Presentase Code Coverage
                  </p>
                  <PercentageCodeCoverage percentage={codeCoveragePercentage} />
                </>
              )}

              {showCyclomaticComplexity && cyclomaticComplexity !== null ? (
                <>
                  <p className="text-sm font-medium mb-2">
                    Nilai Cyclomatic Complexity
                  </p>
                  <div className="text-sm flex items-start">
                    <div className="mr-4">
                      <div>V(G)</div>
                    </div>
                    <div className="flex flex-col">
                      <span>= E − N + 2</span>
                      <span>
                        = {rawEdges.length} − {rawNodes.length} + 2
                      </span>
                      <span className="font-bold">
                        = {cyclomaticComplexity}
                      </span>
                    </div>
                  </div>
                </>
              ) : showCyclomaticComplexity ? (
                <>
                  <p className="text-sm font-medium mb-2">
                    Nilai Cyclomatic Complexity
                  </p>
                  <p className="text-sm text-gray-400">CC tidak tersedia</p>
                </>
              ) : null}
            </div>
          </div>
        </CardContent>

        <CardFooter className="card-footer">{/* footer kosong */}</CardFooter>
      </Card>
    </div>
  );
};

export default CFGCard;
