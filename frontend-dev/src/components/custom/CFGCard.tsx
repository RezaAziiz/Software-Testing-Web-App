import React, { useEffect, useRef, useState } from "react";
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
import { Maximize, MousePointer2, MousePointerClick, ChevronDown, ChevronUp } from "lucide-react";
import "../../index.css";

import { CfgCytoscapeViewport } from "./cfg/CfgCytoscapeViewport";
import { CfgFullscreenModal } from "./cfg/CfgFullscreenModal";
import { CfgTooltipContent } from "./cfg/CfgTooltipContent";

// Register dagre plugin to cytoscape
cytoscape.use(dagre as any);

/**
 * Menghitung jarak kelengkungan (curveDistance) untuk edge CFG.
 *
 * Aturan:
 * - Sequence / True / False ke node berdekatan  → LURUS (0)
 * - Back Edge (loop condition)                   → LENGKUNG negatif (ke kiri)
 * - Continue (kembali ke kondisi loop)            → LENGKUNG negatif
 * - Break yang melompati beberapa node            → LENGKUNG positif (ke kanan)
 * - Return yang menuju End jauh                   → LENGKUNG positif
 * - Labeled Break / Labeled Continue              → LENGKUNG (selalu)
 * - CASE / DEFAULT ke node berdekatan             → LURUS
 */
const computeCurveDistance = (
  branchType: string,
  sourceOrder: number,
  targetOrder: number,
): number => {
  const upper = branchType.toUpperCase();
  const diff = Math.abs(sourceOrder - targetOrder);
  const isBackward = targetOrder <= sourceOrder;

  // ── 1. Back Edge (kembali ke atas) → Melengkung ke kanan pada canvas (nilai positif untuk upward edge) ──
  if (isBackward && diff > 0) {
    return 40 + Math.min(diff * 12, 100);
  }

  // ── 2. Forward edges (ke bawah) → Melengkung ke kiri pada canvas (nilai positif untuk downward edge) ──

  // BREAK → lengkung ke kiri jika melompati ≥2 node
  if (upper === "BREAK" && diff > 2) {
    return 35 + Math.min(diff * 8, 80);
  }

  // RETURN → lengkung ke kiri jika menuju End yang jauh (≥3 node)
  if (upper === "RETURN" && diff >= 3) {
    return 35 + Math.min(diff * 8, 80);
  }

  // CONTINUE ke depan (labeled continue yang di-resolve ke forward)
  if (upper === "CONTINUE" && diff > 2) {
    return 35 + Math.min(diff * 8, 80);
  }

  // Jalur TRUE / FALSE / SEQUENTIAL / biasa yang melompat jauh (≥3 node) 
  // agar tidak memotong di tengah-tengah node lain
  if ((upper === "TRUE" || upper === "FALSE" || upper === "SEQUENTIAL" || upper === "") && diff > 2) {
    return 35 + Math.min(diff * 8, 80);
  }

  // Sequence / True / False / Case / Default dekat → LURUS
  return 0;
};

type CFGCardProps = {
  showCyclomaticComplexity?: boolean;
  showCodeCoverage?: boolean;
  codeCoveragePercentage?: number;
  nodesWithStatus?: Array<any>;
  edgesWithStatus?: Array<any>;
  unexecutedPaths?: Array<string>;
  onNodeClick?: (lines: { start: number; end: number } | null) => void;
  highlightedLines?: { start: number; end: number } | null;
  /** URL of the JaCoCo HTML coverage report iframe. When provided, the fullscreen modal shows it on the left panel. */
  jacocoUrl?: string | null;
};

const getStatusColor = (
  status: string | undefined,
  type: "node" | "edge",
): string => {
  const defaultColor = type === "node" ? "#FFFFFF" : "black";
  if (!status) return defaultColor;

  const upperStatus = status.toUpperCase();
  if (type === "node") {
    if (upperStatus === "N" || upperStatus === "S") {
      return "#ef4444";
    }
  } else {
    if (upperStatus === "N") {
      return "#ef4444";
    }
  }

  return defaultColor;
};

const CFGCard: React.FC<CFGCardProps> = ({
  showCyclomaticComplexity = false,
  showCodeCoverage = false,
  codeCoveragePercentage,
  nodesWithStatus,
  edgesWithStatus,
  unexecutedPaths = [],
  onNodeClick,
  highlightedLines = null,
  jacocoUrl = null,
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
  const idModul = queryParameters.get("idModul");

  const [elements, setElements] = useState<cytoscape.ElementDefinition[]>([]);
  const [rawEdges, setRawEdges] = useState<any[]>([]);
  const [rawNodes, setRawNodes] = useState<any[]>([]);
  const [cyclomaticComplexity, setCyclomaticComplexity] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const cyRef = useRef<cytoscape.Core | null>(null);

  const [tooltip, setTooltip] = useState<{
    visible: boolean;
    x: number;
    y: number;
    nodeLabel: string;
    nodeType: string;
    lineStart: number | null;
    lineEnd: number | null;
    codeContent: string;
    statusText?: string;
  }>({ visible: false, x: 0, y: 0, nodeLabel: "", nodeType: "", lineStart: null, lineEnd: null, codeContent: "" });

  const [isModalOpen, setIsModalOpen] = useState(false);
  const modalCyRef = useRef<cytoscape.Core | null>(null);
  const [modalCyInstance, setModalCyInstance] = useState<cytoscape.Core | null>(null);
  const [modalTooltip, setModalTooltip] = useState<{
    visible: boolean;
    x: number;
    y: number;
    nodeLabel: string;
    nodeType: string;
    lineStart: number | null;
    lineEnd: number | null;
    codeContent: string;
    statusText?: string;
  }>({ visible: false, x: 0, y: 0, nodeLabel: "", nodeType: "", lineStart: null, lineEnd: null, codeContent: "" });

  const [sourceCode, setSourceCode] = useState<string | null>(null);
  const [isAnalysisOpen, setIsAnalysisOpen] = useState<boolean>(true);
  const [isCcAccordionOpen, setIsCcAccordionOpen] = useState<boolean>(true);

  // Fetch source code text for left panel when modal is open
  useEffect(() => {
    if (isModalOpen && !sourceCode && (modulId || idModul)) {
      const fetchCode = async () => {
        try {
          const endpoint = idModul 
            ? `${apiUrl}/modul/detail/${idModul}`
            : `${apiUrl}/modul/detailByIdTopikModul/${modulId}`;
          const res = await fetch(endpoint, {
            headers: {
              Accept: "application/json",
              Authorization: `Bearer ${apiKey}`,
            },
          });
          if (res.ok) {
            const data = await res.json();
            const msModulId = data?.data?.data_modul?.ms_id_modul;
            if (msModulId) {
              const codeRes = await fetch(`${apiUrl}/modul/getSourceCodeText/${msModulId}`, {
                headers: {
                  Accept: "application/json",
                  Authorization: `Bearer ${apiKey}`,
                },
              });
              if (codeRes.ok) {
                const codeData = await codeRes.json();
                setSourceCode(codeData.data || '');
              }
            }
          }
        } catch (e) {
          console.error("Error fetching code in modal:", e);
        }
      };
      fetchCode();
    }
  }, [isModalOpen, modulId, idModul, apiUrl, apiKey, sourceCode]);

  // Fetch data CFG
  const fetchCFG = async () => {
    if (nodesWithStatus && edgesWithStatus) {
      setRawNodes(nodesWithStatus);
      setRawEdges(edgesWithStatus);

      const cyNodes: cytoscape.ElementDefinition[] = nodesWithStatus.map((n: any) => {
        const nodeType: string = n.ms_node_type ?? "NORMAL";
        const upperNodeType = nodeType.toUpperCase();
        const isMerge = upperNodeType === "MERGE";
        const rawOrder = n.ms_execution_order ?? n.execution_order;
        const executionOrder = (rawOrder !== undefined && rawOrder !== null) ? Number(rawOrder) : null;

        const trStatus: string = n.tr_status ?? "N";
        const bgColor = getStatusColor(trStatus, "node");

        const statusText =
          trStatus === "Y" ? "Executed" : trStatus === "S" ? "Partially Executed" : "Not Executed";

        let tooltipText = `Status: ${statusText}\n\nTipe: ${nodeType}`;

        let labelText = "";
        if (upperNodeType === "START") {
          labelText = "Start";
        } else if (upperNodeType === "END") {
          labelText = "End";
        } else if (!isMerge && executionOrder) {
          labelText = executionOrder.toString();
        }

        const lineStart = n.line_start ?? n.ms_line_start ?? n.line_number ?? n.ms_line_number;
        const lineEnd = n.line_end ?? n.ms_line_end ?? lineStart;

        if (lineStart !== undefined && lineStart !== null && !["MERGE", "START", "END"].includes(upperNodeType)) {
          let lineInfo = `Baris Kode: ${lineStart}`;
          if (upperNodeType === "NORMAL") {
            if (lineStart !== lineEnd) {
              lineInfo = `Baris Kode: ${lineStart} - ${lineEnd}`;
            }
          }
          tooltipText = `${lineInfo}\n\n${tooltipText}\n\nKlik untuk menyorot kode sumber`;
        }

        const codeContent = (!["MERGE", "START", "END"].includes(upperNodeType))
          ? (n.code_fragment ?? n.ms_source_code ?? "")
          : "";

        return {
          data: {
            id: n.ms_id_node ?? n.id_node,
            label: labelText,
            nodeType,
            isMerge,
            tooltip: tooltipText,
            codeContent,
            bgColor: bgColor,
            statusText: statusText,
            lineStart: (lineStart !== undefined && lineStart !== null) ? Number(lineStart) : null,
            lineEnd: (lineEnd !== undefined && lineEnd !== null) ? Number(lineEnd) : null,
            executionOrder: executionOrder !== null && !isNaN(executionOrder)
              ? executionOrder
              : (upperNodeType === "START" ? 0 : upperNodeType === "END" ? 9999 : 999),
          },
        };
      });

      cyNodes.sort((a, b) => {
        const orderA = (a.data as any).executionOrder ?? 999;
        const orderB = (b.data as any).executionOrder ?? 999;
        return orderA - orderB;
      });

      const cyEdges: cytoscape.ElementDefinition[] = edgesWithStatus.map((e: any) => {
        const branchType: string = e.ms_branch_type ?? e.branch_type ?? "";
        const isTrue = branchType.toUpperCase() === "TRUE";
        const isFalse = branchType.toUpperCase() === "FALSE";
        const label = isTrue ? "True" : isFalse ? "False" : "";

        const trStatus: string = e.tr_status ?? "N";
        const lineColor = getStatusColor(trStatus, "edge");

        const sourceId = e.id_node_start ?? e.ms_id_start_node ?? e.id_start_node;
        const targetId = e.id_node_finish ?? e.ms_id_finish_node ?? e.id_finish_node;

        const sourceNode = nodesWithStatus.find((n: any) => (n.ms_id_node ?? n.id_node) === sourceId);
        const targetNode = nodesWithStatus.find((n: any) => (n.ms_id_node ?? n.id_node) === targetId);

        // Deteksi tipe node sumber & target
        const sourceType = (sourceNode?.ms_node_type ?? sourceNode?.node_type ?? "").toUpperCase();
        const targetType = (targetNode?.ms_node_type ?? targetNode?.node_type ?? "").toUpperCase();
        const isStructuralEdge = ["MERGE", "START", "END"].includes(sourceType)
                              || ["MERGE", "START", "END"].includes(targetType);

        const sourceOrder = sourceNode ? (sourceNode.ms_execution_order ?? sourceNode.execution_order ?? 999) : 999;
        const targetOrder = targetNode ? (targetNode.ms_execution_order ?? targetNode.execution_order ?? 999) : 999;

        const isBackward = targetOrder <= sourceOrder;
        const isDecisionOrSwitchSource = ["DECISION", "SWITCH"].includes(sourceType);

        // Edge dari/ke MERGE, START, END selalu LURUS.
        // Edge maju dari DECISION/SWITCH juga selalu LURUS (untuk True/False/Case branch).
        const curveDistance = (isStructuralEdge || (!isBackward && isDecisionOrSwitchSource))
          ? 0
          : computeCurveDistance(branchType, sourceOrder, targetOrder);

        return {
          data: {
            id: e.ms_id_edge ?? e.id_edge,
            source: sourceId,
            target: targetId,
            label,
            lineColor,
            branchType,
            curveDistance,
            isCurved: curveDistance !== 0,
            targetExecutionOrder: targetOrder,
          },
        };
      });

      cyEdges.sort((a, b) => {
        const typeA = a.data.branchType?.toUpperCase() || "";
        const typeB = b.data.branchType?.toUpperCase() || "";
        if (typeA === "TRUE" && typeB !== "TRUE") return -1;
        if (typeA !== "TRUE" && typeB === "TRUE") return 1;
        const orderDiff = (a.data.targetExecutionOrder || 999) - (b.data.targetExecutionOrder || 999);
        if (orderDiff !== 0) return orderDiff;
        return (a.data.id || "").localeCompare(b.data.id || "");
      });

      setElements([...cyNodes, ...cyEdges]);
      setLoading(false);
      return;
    }

    if (!modulId && !idModul) {
      setLoading(false);
      return;
    }

    try {
      const endpoint = idModul 
        ? `${apiUrl}/modul/detail/${idModul}`
        : `${apiUrl}/modul/detailByIdTopikModul/${modulId}`;
      const res = await fetch(endpoint, {
        method: "GET",
        headers: {
          Accept: "application/json",
          Authorization: `Bearer ${apiKey}`,
        },
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const data = await res.json();
      const backendNodes: any[] = data?.data?.data_cfg?.nodes ?? [];
      const backendEdges: any[] = data?.data?.data_cfg?.edges ?? [];

      setRawNodes(backendNodes);
      setRawEdges(backendEdges);
      const backendCcRaw = data?.data?.data_modul?.ms_cc;
      const backendCc = backendCcRaw !== null && backendCcRaw !== undefined ? Number(backendCcRaw) : null;
      setCyclomaticComplexity(Number.isFinite(backendCc) ? backendCc : null);

      const cyNodes: cytoscape.ElementDefinition[] = backendNodes.map((n: any) => {
        const nodeType: string = n.ms_node_type ?? n.node_type ?? "NORMAL";
        const upperNodeType = nodeType.toUpperCase();
        const isMerge = upperNodeType === "MERGE";
        const rawOrder = n.ms_execution_order ?? n.execution_order;
        const executionOrder = (rawOrder !== undefined && rawOrder !== null) ? Number(rawOrder) : null;

        const bgColor = "#FFFFFF";
        let tooltipText = `Tipe: ${nodeType} \n`;

        let labelText = "";
        if (upperNodeType === "START") {
          labelText = "Start";
        } else if (upperNodeType === "END") {
          labelText = "End";
        } else if (!isMerge && executionOrder) {
          labelText = executionOrder.toString();
        }

        const lineStart = n.line_start ?? n.ms_line_start ?? n.line_number ?? n.ms_line_number;
        const lineEnd = n.line_end ?? n.ms_line_end ?? lineStart;

        if (lineStart !== undefined && lineStart !== null && !["MERGE", "START", "END"].includes(upperNodeType)) {
          let lineInfo = `Baris Kode: ${lineStart}`;
          if (upperNodeType === "NORMAL") {
            if (lineStart !== lineEnd) {
              lineInfo = `Baris Kode: ${lineStart} - ${lineEnd}`;
            }
          }
          tooltipText = `${lineInfo}\n\n${tooltipText}\n\nKlik untuk menyorot kode sumber`;
        }

        const codeContent = (!["MERGE", "START", "END"].includes(upperNodeType))
          ? (n.code_fragment ?? n.ms_source_code ?? "")
          : "";

        return {
          data: {
            id: n.ms_id_node ?? n.id_node,
            label: labelText,
            nodeType,
            isMerge,
            tooltip: tooltipText,
            codeContent,
            bgColor: bgColor,
            lineStart: (lineStart !== undefined && lineStart !== null) ? Number(lineStart) : null,
            lineEnd: (lineEnd !== undefined && lineEnd !== null) ? Number(lineEnd) : null,
            executionOrder: executionOrder !== null && !isNaN(executionOrder)
              ? executionOrder
              : (upperNodeType === "START" ? 0 : upperNodeType === "END" ? 9999 : 999),
          },
        };
      });

      cyNodes.sort((a, b) => {
        const orderA = (a.data as any).executionOrder ?? 999;
        const orderB = (b.data as any).executionOrder ?? 999;
        return orderA - orderB;
      });

      const cyEdges: cytoscape.ElementDefinition[] = backendEdges.map((e: any) => {
        const branchType: string = e.ms_branch_type ?? e.branch_type ?? "";
        const isTrue = branchType.toUpperCase() === "TRUE";
        const isFalse = branchType.toUpperCase() === "FALSE";
        const label = isTrue ? "True" : isFalse ? "False" : "";

        const sourceId = e.id_node_start ?? e.ms_id_start_node ?? e.id_start_node;
        const targetId = e.id_node_finish ?? e.ms_id_finish_node ?? e.id_finish_node;

        const sourceNode = backendNodes.find((n: any) => (n.ms_id_node ?? n.id_node) === sourceId);
        const targetNode = backendNodes.find((n: any) => (n.ms_id_node ?? n.id_node) === targetId);

        // Deteksi tipe node sumber & target
        const sourceType = (sourceNode?.ms_node_type ?? sourceNode?.node_type ?? "").toUpperCase();
        const targetType = (targetNode?.ms_node_type ?? targetNode?.node_type ?? "").toUpperCase();
        const isStructuralEdge = ["MERGE", "START", "END"].includes(sourceType)
                              || ["MERGE", "START", "END"].includes(targetType);

        const sourceOrder = sourceNode ? (sourceNode.ms_execution_order ?? sourceNode.execution_order ?? 999) : 999;
        const targetOrder = targetNode ? (targetNode.ms_execution_order ?? targetNode.execution_order ?? 999) : 999;

        const isBackward = targetOrder <= sourceOrder;
        const isDecisionOrSwitchSource = ["DECISION", "SWITCH"].includes(sourceType);

        // Edge dari/ke MERGE, START, END selalu LURUS.
        // Edge maju dari DECISION/SWITCH juga selalu LURUS (untuk True/False/Case branch).
        const curveDistance = (isStructuralEdge || (!isBackward && isDecisionOrSwitchSource))
          ? 0
          : computeCurveDistance(branchType, sourceOrder, targetOrder);

        return {
          data: {
            id: e.ms_id_edge ?? e.id_edge,
            source: sourceId,
            target: targetId,
            label,
            lineColor: "black",
            branchType,
            curveDistance,
            isCurved: curveDistance !== 0,
            targetExecutionOrder: targetOrder,
          },
        };
      });

      cyEdges.sort((a, b) => {
        const typeA = a.data.branchType?.toUpperCase() || "";
        const typeB = b.data.branchType?.toUpperCase() || "";
        if (typeA === "TRUE" && typeB !== "TRUE") return -1;
        if (typeA !== "TRUE" && typeB === "TRUE") return 1;
        const orderDiff = (a.data.targetExecutionOrder || 999) - (b.data.targetExecutionOrder || 999);
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
  }, [modulId, idModul, nodesWithStatus, edgesWithStatus]);

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
    cy.off("tap", "node");
    cy.off("tap");

    cy.on("mouseover", "node", (evt) => {
      const node = evt.target;
      const container = cy.container();
      if (!container) return;
      const renderedPos = node.renderedPosition();
      setTooltip({
        visible: true,
        x: renderedPos.x + 30,
        y: renderedPos.y - 10,
        nodeLabel: node.data("label") || (node.data("nodeType") === "START" ? "Start" : node.data("nodeType") === "END" ? "End" : "Node"),
        nodeType: node.data("nodeType") || "",
        lineStart: node.data("lineStart"),
        lineEnd: node.data("lineEnd"),
        codeContent: node.data("codeContent") ?? "",
        statusText: node.data("statusText"),
      });
    });
    cy.on("mousemove", "node", (evt) => {
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

    cy.on("tap", "node", (evt) => {
      const node = evt.target;
      const nodeType = (node.data("nodeType") ?? "").toUpperCase();
      if (["START", "END", "MERGE"].includes(nodeType)) {
        if (onNodeClick) onNodeClick(null);
        return;
      }
      const lineStart = node.data("lineStart");
      const lineEnd = node.data("lineEnd");
      if (onNodeClick && lineStart !== undefined && lineStart !== null) {
        onNodeClick({ start: Number(lineStart), end: Number(lineEnd ?? lineStart) });
      } else if (onNodeClick) {
        onNodeClick(null);
      }
    });

    cy.on("tap", (evt) => {
      if (evt.target === cy && onNodeClick) {
        onNodeClick(null);
      }
    });
  }, [elements, layout, onNodeClick]);

  // Clean up modal instance when modal closes
  useEffect(() => {
    if (!isModalOpen) {
      setModalCyInstance(null);
      modalCyRef.current = null;
    }
  }, [isModalOpen]);

  // Setup modal cytoscape events and layout identical to normal CFG
  useEffect(() => {
    if (!isModalOpen || !modalCyInstance || elements.length === 0) return;
    const cy = modalCyInstance;

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
    }, 300);

    cy.off("mouseover", "node");
    cy.off("mouseout", "node");
    cy.off("mousemove", "node");
    cy.off("tap", "node");
    cy.off("tap");

    cy.on("mouseover", "node", (evt) => {
      const node = evt.target;
      const container = cy.container();
      if (!container) return;
      const renderedPos = node.renderedPosition();
      setModalTooltip({
        visible: true,
        x: renderedPos.x + 30,
        y: renderedPos.y - 10,
        nodeLabel: node.data("label") || (node.data("nodeType") === "START" ? "Start" : node.data("nodeType") === "END" ? "End" : "Node"),
        nodeType: node.data("nodeType") || "",
        lineStart: node.data("lineStart"),
        lineEnd: node.data("lineEnd"),
        codeContent: node.data("codeContent") ?? "",
        statusText: node.data("statusText"),
      });
    });
    cy.on("mousemove", "node", (evt) => {
      const container = cy.container();
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

    cy.on("tap", "node", (evt) => {
      if (!onNodeClick) return;
      const node = evt.target;
      const nodeType = (node.data("nodeType") ?? "").toUpperCase();
      if (["START", "END", "MERGE"].includes(nodeType)) {
        onNodeClick(null);
        return;
      }
      const nodeId = node.data("id");
      const allRawNodes = nodesWithStatus ?? rawNodes;
      const rawNode = allRawNodes.find((n: any) => (n.ms_id_node ?? n.id_node) === nodeId);
      if (rawNode) {
        const lineStart = rawNode.line_start ?? rawNode.ms_line_start ?? rawNode.line_number ?? rawNode.ms_line_number;
        const lineEnd = rawNode.line_end ?? rawNode.ms_line_end ?? lineStart;
        if (lineStart !== undefined && lineStart !== null) {
          onNodeClick({ start: Number(lineStart), end: Number(lineEnd ?? lineStart) });
        } else {
          onNodeClick(null);
        }
      } else {
        onNodeClick(null);
      }
    });

    cy.on("tap", (evt) => {
      if (evt.target === cy && onNodeClick) {
        onNodeClick(null);
      }
    });
  }, [isModalOpen, modalCyInstance, elements, layout, onNodeClick, nodesWithStatus, rawNodes]);

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
      <Card className="relative overflow-hidden h-full flex flex-col min-h-[500px]">
        <CardHeader className="pt-6 pb-2 shrink-0">
          <CardTitle className="text-base module-title">Struktur Program</CardTitle>
        </CardHeader>

        <CardContent className="flex flex-col flex-1 relative min-h-0">
          <div className="w-full flex flex-row gap-3 h-full">
            <div className={`transition-all duration-300 ${(isAnalysisOpen && showCodeCoverage) ? 'w-1/2' : 'w-full'} flex flex-col h-full min-h-0`}>
              <div className="flex items-center justify-between mb-2 shrink-0">
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
                    onMouseEnter={(e) => (e.currentTarget.style.background = "#f3f4f6")}
                    onMouseLeave={(e) => (e.currentTarget.style.background = "#fff")}
                  >
                    <Maximize size={18} color="#4b5563" />
                  </button>
                )}
              </div>
              <div className="text-xs text-white bg-[#0b48b3] p-3 rounded-md mb-2 flex flex-col gap-1.5 shadow-sm">
                <div className="flex items-center gap-2">
                  <MousePointer2 size={14} /> <span>Arahkan kursor ke node: Pratinjau informasi node</span>
                </div>
                <div className="flex items-center gap-2">
                  <MousePointerClick size={14} /> <span>Klik Node: Sorot kode sumber yang terkait</span>
                </div>
                <div className="flex items-center gap-2">
                  <MousePointerClick size={14} /> <span>Klik baris kode sumber: Sorot node CFG terkait</span>
                </div>
              </div>

              {error ? (
                <div className="flex-1 min-h-0 flex items-center justify-center text-sm text-gray-400 bg-gray-50 rounded-lg border border-dashed border-gray-300">
                  <span>Belum ada data CFG untuk modul ini.</span>
                </div>
              ) : elements.length === 0 ? (
                <div className="flex-1 min-h-0 flex items-center justify-center text-sm text-gray-400 bg-gray-50 rounded-lg border border-dashed border-gray-300">
                  <span>Data CFG tidak tersedia.</span>
                </div>
              ) : (
                <div className="relative flex-1 min-h-0" style={{ overflow: "visible" }}>
                  <CfgCytoscapeViewport
                    elements={elements}
                    cyRef={cyRef}
                    zoomControlSuffix="inline"
                    style={{ position: "absolute", inset: 0 }}
                    highlightedLines={highlightedLines}
                  />

                  {tooltip.visible && (
                    <div
                      style={{
                        position: "absolute",
                        left: tooltip.x,
                        top: tooltip.y,
                        background: "#1e293b",
                        color: "#f8fafc",
                        padding: 0,
                        borderRadius: 8,
                        pointerEvents: "none",
                        zIndex: 100,
                        boxShadow: "0 10px 25px -5px rgba(0,0,0,0.15)",
                      }}
                    >
                      <CfgTooltipContent 
                        nodeLabel={tooltip.nodeLabel}
                        nodeType={tooltip.nodeType}
                        lineStart={tooltip.lineStart}
                        lineEnd={tooltip.lineEnd}
                        code={tooltip.codeContent || undefined}
                        statusText={tooltip.statusText}
                      />
                    </div>
                  )}
                </div>
              )}

              {showCyclomaticComplexity && (
                <div className="mt-4 border rounded-md shadow-sm bg-white overflow-hidden shrink-0">
                  <button 
                    className="w-full flex justify-between items-center p-3 bg-gray-50 hover:bg-gray-100 transition-colors"
                    onClick={() => setIsCcAccordionOpen(!isCcAccordionOpen)}
                  >
                    <span className="font-semibold text-sm">Cyclomatic Complexity (V(G)) = {cyclomaticComplexity ?? (rawEdges.length - rawNodes.length + 2)}</span>
                    {isCcAccordionOpen ? <ChevronDown size={18} /> : <ChevronUp size={18} />}
                  </button>
                  {isCcAccordionOpen && (
                    <div className="p-4 border-t flex flex-row gap-4 items-center">
                      <div className="flex-1 text-sm text-gray-600">
                        Minimal {cyclomaticComplexity ?? (rawEdges.length - rawNodes.length + 2)} jalur independen harus dianalisis.
                      </div>
                      <div className="bg-gray-100 p-3 rounded font-mono text-sm flex flex-col gap-1 text-black whitespace-pre">
                        <div>V(G) = Edge - Node + 2</div>
                        <div>     = {rawEdges.length} - {rawNodes.length} + 2</div>
                        <div>     = {cyclomaticComplexity ?? (rawEdges.length - rawNodes.length + 2)}</div>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>

            {isAnalysisOpen && showCodeCoverage && (
              <div className="w-1/2 flex flex-col border-l border-gray-200 relative overflow-y-auto">
                <div className="flex justify-end w-full mb-2">
                  <button
                    onClick={() => setIsAnalysisOpen(false)}
                    className="text-xs text-gray-500 hover:text-gray-700 bg-gray-100 hover:bg-gray-200 px-2 py-1 rounded transition-colors"
                  >
                    Tutup
                  </button>
                </div>
                
                <div className="flex flex-col items-center w-full">
                  {showCodeCoverage && codeCoveragePercentage !== undefined && (
                    <>
                      <p className="text-sm font-medium mb-5">Presentase Code Coverage</p>
                      <PercentageCodeCoverage percentage={codeCoveragePercentage} />
                      <UnexecutedPathsViewer paths={unexecutedPaths} />
                    </>
                  )}
                </div>
              </div>
            )}
          </div>
        </CardContent>
        <CardFooter className="card-footer shrink-0" />

        {!isAnalysisOpen && showCodeCoverage && (
          <button
            onClick={() => setIsAnalysisOpen(true)}
            className="absolute right-0 top-[56px] bg-blue-50 hover:bg-blue-100 border border-blue-200 border-r-0 rounded-l-md px-1.5 py-4 shadow-sm transition-colors z-10 flex flex-col items-center justify-center"
            title="Tampilkan Coverage"
          >
            <div style={{ writingMode: 'vertical-rl', transform: 'rotate(180deg)' }} className="text-xs font-semibold text-blue-700 tracking-wider">
              Coverage
            </div>
          </button>
        )}
      </Card>

      <CfgFullscreenModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        elements={elements}
        sourceCode={sourceCode}
        highlightedLines={highlightedLines}
        modalCyRef={modalCyRef}
        setModalCyInstance={setModalCyInstance}
        modalTooltip={modalTooltip}
        jacocoUrl={jacocoUrl}
        initialSplitPercent={jacocoUrl ? 50 : 45}
      />

      <style>{`
        @keyframes cfgSlideIn {
          from {
            transform: translateY(20px);
            opacity: 0;
          }
          to {
            transform: translateY(0);
            opacity: 1;
          }
        }
      `}</style>
    </div>
  );
};

export default CFGCard;