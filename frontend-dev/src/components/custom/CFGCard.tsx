import React, { useEffect, useRef, useState, useCallback } from "react";
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
import UnexecutedPathsViewer from "./UnexecutedPathsViewer";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogClose,
} from "@/components/ui/dialog";
import { Maximize, X } from "lucide-react";
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
  unexecutedPaths?: Array<string>;
};

const getStatusColor = (
  status: string | undefined,
  type: "node" | "edge",
): string => {
  const defaultColor = type === "node" ? "#FFFFFF" : "black";
  if (!status) return defaultColor;

  if (status.toUpperCase() === "N") {
    return "#ef4444"; // Red
  }

  return defaultColor; // Y and S are no longer colored
};

// Component
const CFGCard: React.FC<CFGCardProps> = ({
  showCyclomaticComplexity = false,
  showCodeCoverage = false,
  codeCoveragePercentage,
  nodesWithStatus,
  edgesWithStatus,
  unexecutedPaths = [],
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

  // Modal fullscreen state
  const [isModalOpen, setIsModalOpen] = useState(false);
  const modalCyRef = useRef<cytoscape.Core | null>(null);
  const [modalTooltip, setModalTooltip] = useState<{
    visible: boolean;
    x: number;
    y: number;
    content: string;
  }>({ visible: false, x: 0, y: 0, content: "" });

  // Fetch data CFG
  const fetchCFG = async () => {
    // BLOK TEST RESULT PAGE
    if (nodesWithStatus && edgesWithStatus) {
      setRawNodes(nodesWithStatus);
      setRawEdges(edgesWithStatus);

      const cyNodes: cytoscape.ElementDefinition[] = nodesWithStatus.map(
        (n: any) => {
          const nodeType: string = n.ms_node_type ?? "NORMAL";
          const upperNodeType = nodeType.toUpperCase();
          const isMerge = upperNodeType === "MERGE";
          const rawOrder = n.ms_execution_order ?? n.execution_order;
          const executionOrder = (rawOrder !== undefined && rawOrder !== null) ? Number(rawOrder) : null;

          const trStatus: string = n.tr_status ?? "N";
          const bgColor = getStatusColor(trStatus, "node");

          const statusText =
            trStatus === "Y"
              ? "Executed"
              : trStatus === "S"
                ? "Partially Executed"
                : "Not Executed";

          let tooltipText = `Status: ${statusText}\n\nTipe: ${nodeType}`;

          // PERUBAHAN 1: Logika Label
          let labelText = "";
          if (upperNodeType === "START") {
            labelText = "Start";
          } else if (upperNodeType === "END") {
            labelText = "End";
          } else if (!isMerge && executionOrder) {
            labelText = executionOrder.toString();
          }

          const lineStart =
            n.line_start ??
            n.ms_line_start ??
            n.line_number ??
            n.ms_line_number;

          // Sembunyikan informasi baris dari tooltip untuk Start dan End
          if (
            lineStart !== undefined &&
            lineStart !== null &&
            !["MERGE", "START", "END"].includes(upperNodeType)
          ) {
            let lineInfo = `Baris Kode: ${lineStart}`;
            if (upperNodeType === "NORMAL") {
              const lineEnd = n.line_end ?? n.ms_line_end ?? lineStart;
              if (lineStart !== lineEnd) {
                lineInfo = `Baris Kode: ${lineStart} - ${lineEnd}`;
              }
            }
            tooltipText = `${lineInfo}\n${tooltipText}`;
          }

          return {
            data: {
              id: n.ms_id_node ?? n.id_node,
              label: labelText,
              nodeType,
              isMerge,
              trStatus,
              tooltip: tooltipText,
              bgColor,
              executionOrder: executionOrder !== null && !isNaN(executionOrder)
                ? executionOrder
                : (upperNodeType === "START"
                  ? 0
                  : upperNodeType === "END"
                    ? 9999
                    : 999),
            },
          };
        },
      );

      cyNodes.sort((a, b) => {
        const orderA = (a.data as any).executionOrder ?? 999;
        const orderB = (b.data as any).executionOrder ?? 999;
        return orderA - orderB;
      });

      const cyEdges: cytoscape.ElementDefinition[] = edgesWithStatus.map(
        (e: any) => {
          const branchType: string = e.ms_branch_type ?? "";
          const isTrue = branchType.toUpperCase() === "TRUE";
          const isFalse = branchType.toUpperCase() === "FALSE";
          const label = isTrue ? "True" : isFalse ? "False" : "";
          const trStatus: string = e.tr_status ?? "N";
          const lineColor = getStatusColor(trStatus, "edge");

          return {
            data: {
              id: e.ms_id_edge,
              source: e.id_node_start ?? e.ms_id_start_node,
              target: e.id_node_finish ?? e.ms_id_finish_node,
              label,
              lineColor,
              trStatus,
              branchType,
              targetExecutionOrder: (() => {
                const targetId = e.id_node_finish ?? e.ms_id_finish_node;
                const targetNode = nodesWithStatus.find(
                  (n: any) => (n.ms_id_node ?? n.id_node) === targetId,
                );
                return targetNode
                  ? (targetNode.ms_execution_order ??
                    targetNode.execution_order ??
                    999)
                  : 999;
              })(),
            },
          };
        },
      );

      cyEdges.sort((a, b) => {
        const typeA = a.data.branchType?.toUpperCase() || "";
        const typeB = b.data.branchType?.toUpperCase() || "";
        if (typeA === "TRUE" && typeB !== "TRUE") return -1;
        if (typeA !== "TRUE" && typeB === "TRUE") return 1;
        const orderDiff =
          (a.data.targetExecutionOrder || 999) -
          (b.data.targetExecutionOrder || 999);
        if (orderDiff !== 0) return orderDiff;
        return (a.data.id || "").localeCompare(b.data.id || "");
      });

      setElements([...cyNodes, ...cyEdges]);
      setLoading(false);
      return;
    }

    // BLOK GENERIC PAGE
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

      const cyNodes: cytoscape.ElementDefinition[] = backendNodes.map(
        (n: any) => {
          const nodeType: string = n.ms_node_type ?? n.node_type ?? "NORMAL";
          const upperNodeType = nodeType.toUpperCase();
          const isMerge = upperNodeType === "MERGE";
          const rawOrder = n.ms_execution_order ?? n.execution_order;
          const executionOrder = (rawOrder !== undefined && rawOrder !== null) ? Number(rawOrder) : null;

          const bgColor = "#FFFFFF";
          let tooltipText = `Tipe: ${nodeType} \n`;

          // PERUBAHAN 2: Logika Label
          let labelText = "";
          if (upperNodeType === "START") {
            labelText = "Start";
          } else if (upperNodeType === "END") {
            labelText = "End";
          } else if (!isMerge && executionOrder) {
            labelText = executionOrder.toString();
          }

          const lineStart =
            n.line_start ??
            n.ms_line_start ??
            n.line_number ??
            n.ms_line_number;

          if (
            lineStart !== undefined &&
            lineStart !== null &&
            !["MERGE", "START", "END"].includes(upperNodeType)
          ) {
            let lineInfo = `Baris Kode: ${lineStart}`;
            if (upperNodeType === "NORMAL") {
              const lineEnd = n.line_end ?? n.ms_line_end ?? lineStart;
              if (lineStart !== lineEnd) {
                lineInfo = `Baris Kode: ${lineStart} - ${lineEnd}`;
              }
            }
            tooltipText = `${lineInfo}\n\n${tooltipText}`;
          }

          return {
            data: {
              id: n.ms_id_node ?? n.id_node,
              label: labelText,
              nodeType,
              isMerge,
              tooltip: tooltipText,
              bgColor: bgColor,
              executionOrder: executionOrder !== null && !isNaN(executionOrder)
                ? executionOrder
                : (upperNodeType === "START"
                  ? 0
                  : upperNodeType === "END"
                    ? 9999
                    : 999),
            },
          };
        },
      );

      cyNodes.sort((a, b) => {
        const orderA = (a.data as any).executionOrder ?? 999;
        const orderB = (b.data as any).executionOrder ?? 999;
        return orderA - orderB;
      });

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
              targetExecutionOrder: (() => {
                const targetId =
                  e.id_node_finish ?? e.ms_id_finish_node ?? e.id_finish_node;
                const targetNode = backendNodes.find(
                  (n: any) => (n.ms_id_node ?? n.id_node) === targetId,
                );
                return targetNode
                  ? (targetNode.ms_execution_order ??
                    targetNode.execution_order ??
                    999)
                  : 999;
              })(),
            },
          };
        },
      );

      cyEdges.sort((a, b) => {
        const typeA = a.data.branchType?.toUpperCase() || "";
        const typeB = b.data.branchType?.toUpperCase() || "";
        if (typeA === "TRUE" && typeB !== "TRUE") return -1;
        if (typeA !== "TRUE" && typeB === "TRUE") return 1;
        const orderDiff =
          (a.data.targetExecutionOrder || 999) -
          (b.data.targetExecutionOrder || 999);
        if (orderDiff !== 0) return orderDiff;
        return (a.data.id || "").localeCompare(b.data.id || "");
      });

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

  // Konfigurasi layout DAGRE
  const layout = React.useMemo(() => ({
    name: "dagre",
    rankDir: "TB",
    nodeSep: 80,
    rankSep: 60,
    edgeSep: 80,
    nodeDimensionsIncludeLabels: true,
    ranker: "network-simplex",
    animate: false,
    fit: true,
    padding: 30,
    sort: (a: any, b: any) => {
      const orderA = a.data("executionOrder") ?? 999;
      const orderB = b.data("executionOrder") ?? 999;
      return orderA - orderB;
    },
  }), []);

  useEffect(() => {
    if (!cyRef.current || elements.length === 0) return;
    const cy = cyRef.current;

    setTimeout(() => {
      cy.resize();
      const layoutInstance = cy.layout({
        ...layout,
        animate: true,
      } as any);
      layoutInstance.one("layoutstop", () => {
        // Unlock all nodes so they can be dragged freely
        cy.nodes().unlock();
        cy.nodes().grabify();
        cy.fit(undefined, 30);
        cy.center();
      });
      layoutInstance.run();
    }, 50);

    cy.off("mouseover", "node");
    cy.off("mouseout", "node");
    cy.off("mousemove", "node");

    cy.on("mouseover", "node", (evt) => {
      const node = evt.target;
      const container = cy.container();
      if (!container) return;
      const renderedPos = node.renderedPosition();
      setTooltip({
        visible: true,
        x: renderedPos.x + 30,
        y: renderedPos.y - 10,
        content: node.data("tooltip") ?? "",
      });
    });
    cy.on("mousemove", "node", (evt) => {
      const cy = cyRef.current;
      if (!cy) return;
      const container = cy.container();
      if (!container) return;
      const rect = container.getBoundingClientRect();
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
  }, [elements, layout]);

  // Setup modal cytoscape events and layout
  const setupModalCytoscape = useCallback(
    (cy: cytoscape.Core) => {
      modalCyRef.current = cy;

      setTimeout(() => {
        cy.resize();
        const layoutInstance = cy.layout({
          ...layout,
          animate: true,
        } as any);
        layoutInstance.one("layoutstop", () => {
          cy.nodes().unlock();
          cy.nodes().grabify();
          cy.fit(undefined, 30);
          cy.center();
        });
        layoutInstance.run();
      }, 300); // 300ms untuk menunggu animasi render modal selesai

      cy.off("mouseover", "node");
      cy.off("mouseout", "node");
      cy.off("mousemove", "node");

      cy.on("mouseover", "node", (evt) => {
        const node = evt.target;
        const container = cy.container();
        if (!container) return;
        const renderedPos = node.renderedPosition();
        setModalTooltip({
          visible: true,
          x: renderedPos.x + 30,
          y: renderedPos.y - 10,
          content: node.data("tooltip") ?? "",
        });
      });
      cy.on("mousemove", "node", (evt) => {
        const mCy = modalCyRef.current;
        if (!mCy) return;
        const container = mCy.container();
        if (!container) return;
        const rect = container.getBoundingClientRect();
        const originalEvt = evt.originalEvent;
        if (originalEvt) {
          setModalTooltip((t) => ({
            ...t,
            x: (originalEvt as MouseEvent).clientX - rect.left + 15,
            y: (originalEvt as MouseEvent).clientY - rect.top - 10,
          }));
        }
      });
      cy.on("mouseout", "node", () => {
        setModalTooltip((t) => ({ ...t, visible: false }));
      });
    },
    [layout],
  );

  const stylesheet: cytoscape.StylesheetCSS[] = [
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
    // Stylesheet untuk node START dan END
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
  ];

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
            <div className="w-1/2 flex flex-col">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm font-medium">Control Flow Graph</p>
                {elements.length > 0 && (
                  <button
                    id="cfg-expand-btn"
                    title="Lihat CFG Fullscreen"
                    onClick={() => setIsModalOpen(true)}
                    style={{
                      width: 28,
                      height: 28,
                      padding: 0,
                      background: "#fff",
                      border: "1px solid #d1d5db",
                      borderRadius: 6,
                      fontSize: 14,
                      cursor: "pointer",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      boxShadow: "0 1px 4px rgba(0,0,0,0.10)",
                      transition: "background 0.15s",
                    }}
                    onMouseEnter={(e) =>
                      (e.currentTarget.style.background = "#f3f4f6")
                    }
                    onMouseLeave={(e) =>
                      (e.currentTarget.style.background = "#fff")
                    }
                  >
                    <Maximize size={16} color="#4b5563" />
                  </button>
                )}
              </div>
              <div className="text-[11px] text-blue-600 bg-blue-50 px-2 py-1 rounded border border-blue-100 flex items-center gap-1 mb-2">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="M12 16v-4"></path><path d="M12 8h.01"></path></svg>
                <span>Node dapat digeser dan di-hover untuk melihat detail.</span>
              </div>

              {error ? (
                <div className="h-96 flex items-center justify-center text-sm text-gray-400 bg-gray-50 rounded-lg border border-dashed border-gray-300">
                  <span>Belum ada data CFG untuk modul ini.</span>
                </div>
              ) : elements.length === 0 ? (
                <div className="h-96 flex items-center justify-center text-sm text-gray-400 bg-gray-50 rounded-lg border border-dashed border-gray-300">
                  <span>Data CFG tidak tersedia.</span>
                </div>
              ) : (
                <div
                  className="relative"
                  style={{ height: "24rem", overflow: "visible" }}
                >
                  <CytoscapeComponent
                    elements={elements}
                    layout={{ name: "preset" }}
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

            <div className="w-1/2 flex flex-col items-center">
              {showCodeCoverage && codeCoveragePercentage !== undefined && (
                <>
                  <p className="text-sm font-medium mb-5">
                    Presentase Code Coverage
                  </p>
                  <PercentageCodeCoverage percentage={codeCoveragePercentage} />
                  <UnexecutedPathsViewer paths={unexecutedPaths} />
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

      {/* Modal Fullscreen CFG */}
      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent
          className="max-w-[92vw] w-[92vw] h-[88vh] flex flex-col p-0 gap-0 bg-white rounded-xl sm:rounded-xl shadow-2xl overflow-hidden border border-gray-200"
          style={{ maxHeight: "88vh" }}
        >
          <DialogHeader className="px-6 pt-5 pb-3 border-b border-gray-200 flex-shrink-0 flex flex-row items-center justify-between">
            <div className="flex flex-col space-y-1 text-left">
              <DialogTitle className="text-base font-semibold text-gray-900">
                Control Flow Graph — Fullscreen
              </DialogTitle>
              <DialogDescription className="text-xs text-gray-500">
                Node dapat digeser dan di-hover untuk melihat detail.
              </DialogDescription>
            </div>
            <DialogClose className="rounded-lg p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors border border-transparent hover:border-gray-200">
              <X size={18} color="#4b5563" />
            </DialogClose>
          </DialogHeader>

          <div
            className="relative flex-1 m-4"
            style={{ minHeight: 0, overflow: "visible" }}
          >
            {elements.length > 0 && (
              <CytoscapeComponent
                elements={elements}
                layout={{ name: "preset" }}
                stylesheet={stylesheet}
                cy={setupModalCytoscape}
                style={{
                  width: "100%",
                  height: "100%",
                  background: "#f9fafb",
                  borderRadius: 8,
                }}
                wheelSensitivity={0.5}
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
                {modalTooltip.content}
              </div>
            )}

            {/* Modal Zoom Controls */}
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
                    const cy = modalCyRef.current;
                    if (cy) cy.zoom(cy.zoom() * 1.3);
                  },
                },
                {
                  label: "-",
                  title: "Zoom Out",
                  action: () => {
                    const cy = modalCyRef.current;
                    if (cy) cy.zoom(cy.zoom() * 0.75);
                  },
                },
                {
                  label: "⊞",
                  title: "Fit",
                  action: () => modalCyRef.current?.fit(undefined, 20),
                },
              ].map(({ label, title, action }) => (
                <button
                  key={`modal-${label}`}
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
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default CFGCard;