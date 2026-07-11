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
import UnexecutedPathsViewer from "./UnexecutedPathsViewer";
import { Maximize, Minimize } from "lucide-react";
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
  onNodeClick?: (lines: { start: number; end: number } | null) => void;
  highlightedLines?: { start: number; end: number } | null;
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
      return "#ef4444"; // Red for Not Executed (N) and Partially Executed (S)
    }
  } else {
    if (upperStatus === "N") {
      return "#ef4444"; // Red for Not Executed (N)
    }
  }

  return defaultColor; // Y is no longer colored
};

// Java keyword sets for syntax highlighting
const JAVA_KEYWORDS = new Set([
  "abstract", "assert", "boolean", "break", "byte", "case", "catch", "char",
  "class", "const", "continue", "default", "do", "double", "else", "enum",
  "extends", "final", "finally", "float", "for", "goto", "if", "implements",
  "import", "instanceof", "int", "interface", "long", "native", "new",
  "package", "private", "protected", "public", "return", "short", "static",
  "strictfp", "super", "switch", "synchronized", "this", "throw", "throws",
  "transient", "try", "void", "volatile", "while",
]);
const JAVA_LITERALS = new Set(["true", "false", "null"]);

/** Lightweight Java syntax highlighter – returns React elements */
const highlightJavaCode = (code: string): React.ReactNode[] => {
  // Regex: strings, single-line comments, multi-line comments, numbers, words
  const tokenRegex = /("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'|\/\/.*|\/\*[\s\S]*?\*\/|\b\d+(?:\.\d+)?\b|[a-zA-Z_$][a-zA-Z0-9_$]*|[^\s]|\s+)/g;
  const tokens = code.match(tokenRegex) || [code];
  return tokens.map((token, i) => {
    // String literals
    if (/^["']/.test(token)) {
      return <span key={i} style={{ color: "#a5d6a7" }}>{token}</span>;
    }
    // Comments
    if (token.startsWith("//") || token.startsWith("/*")) {
      return <span key={i} style={{ color: "#78909c", fontStyle: "italic" }}>{token}</span>;
    }
    // Numbers
    if (/^\d/.test(token)) {
      return <span key={i} style={{ color: "#f48fb1" }}>{token}</span>;
    }
    // Keywords
    if (JAVA_KEYWORDS.has(token)) {
      return <span key={i} style={{ color: "#90caf9", fontWeight: 600 }}>{token}</span>;
    }
    // Literals (true/false/null)
    if (JAVA_LITERALS.has(token)) {
      return <span key={i} style={{ color: "#ce93d8" }}>{token}</span>;
    }
    return <span key={i}>{token}</span>;
  });
};

/** Tooltip content component with optional syntax-highlighted code block */
const TooltipContent: React.FC<{ text: string; code?: string }> = ({ text, code }) => (
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

// Component
const CFGCard: React.FC<CFGCardProps> = ({
  showCyclomaticComplexity = false,
  showCodeCoverage = false,
  codeCoveragePercentage,
  nodesWithStatus,
  edgesWithStatus,
  unexecutedPaths = [],
  onNodeClick,
  highlightedLines = null,
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
    codeContent: string;
  }>({ visible: false, x: 0, y: 0, content: "", codeContent: "" });

  // Modal fullscreen state
  const [isModalOpen, setIsModalOpen] = useState(false);
  const modalCyRef = useRef<cytoscape.Core | null>(null);
  const [modalCyInstance, setModalCyInstance] = useState<cytoscape.Core | null>(null);
  const [modalTooltip, setModalTooltip] = useState<{
    visible: boolean;
    x: number;
    y: number;
    content: string;
    codeContent: string;
  }>({ visible: false, x: 0, y: 0, content: "", codeContent: "" });

  const [splitPercent, setSplitPercent] = useState<number>(45);
  const [isDragging, setIsDragging] = useState(false);
  const [sourceCode, setSourceCode] = useState<string | null>(null);

  const modalCodeContainerRef = useRef<HTMLDivElement>(null);
  const modalHighlightRef = useRef<HTMLDivElement>(null);

  const startSplitResize = React.useCallback((mouseDownEvent: React.MouseEvent) => {
    mouseDownEvent.preventDefault();
    setIsDragging(true);

    const doDrag = (mouseMoveEvent: MouseEvent) => {
      const newPercent = (mouseMoveEvent.clientX / window.innerWidth) * 100;

      // Constraints:
      // Minimum: 25% (left panel cannot shrink below 25%)
      // Maximum: 75% (left panel cannot grow above 75%)
      if (newPercent >= 25 && newPercent <= 75) {
        setSplitPercent(newPercent);
      }
    };

    const stopDrag = () => {
      setIsDragging(false);
      document.removeEventListener("mousemove", doDrag);
      document.removeEventListener("mouseup", stopDrag);
    };

    document.addEventListener("mousemove", doDrag);
    document.addEventListener("mouseup", stopDrag);
  }, []);

  // Dynamically trigger Cytoscape resize when width changes during dragging
  useEffect(() => {
    if (modalCyInstance) {
      modalCyInstance.resize();
    }
  }, [splitPercent, modalCyInstance]);

  // Fetch source code text for left panel when modal is open
  useEffect(() => {
    if (isModalOpen && !sourceCode && modulId) {
      const fetchCode = async () => {
        try {
          const res = await fetch(`${apiUrl}/modul/detailByIdTopikModul/${modulId}`, {
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
  }, [isModalOpen, modulId, apiUrl, apiKey, sourceCode]);

  // Auto-scroll the code panel inside the modal
  useEffect(() => {
    if (isModalOpen && highlightedLines && modalHighlightRef.current && modalCodeContainerRef.current) {
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
  }, [highlightedLines, isModalOpen]);

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

          // Ambil isi kode (disimpan terpisah untuk syntax highlighting)
          const codeContent = (!["MERGE", "START", "END"].includes(upperNodeType))
            ? (n.ms_source_code ?? n.code_fragment ?? "")
            : "";

          return {
            data: {
              id: n.ms_id_node ?? n.id_node,
              label: labelText,
              nodeType,
              isMerge,
              trStatus,
              tooltip: tooltipText,
              codeContent,
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

          // Ambil isi kode (disimpan terpisah untuk syntax highlighting)
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
        content: node.data("tooltip") ?? "",
        codeContent: node.data("codeContent") ?? "",
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

    // Handle node click to emit line info for code highlighting
    cy.on("tap", "node", (evt) => {
      if (!onNodeClick) return;
      const node = evt.target;
      const nodeType = (node.data("nodeType") ?? "").toUpperCase();
      if (["START", "END", "MERGE"].includes(nodeType)) {
        onNodeClick(null);
        return;
      }
      // Find the raw node data to get line_start and line_end
      const nodeId = node.data("id");
      const allRawNodes = nodesWithStatus ?? rawNodes;
      const rawNode = allRawNodes.find(
        (n: any) => (n.ms_id_node ?? n.id_node) === nodeId
      );
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

    // Handle tap on background to clear highlight
    cy.on("tap", (evt) => {
      if (evt.target === cy && onNodeClick) {
        onNodeClick(null);
      }
    });
  }, [elements, layout, onNodeClick, nodesWithStatus, rawNodes]);

  // Reset modal cytoscape instance saat modal ditutup agar layout berjalan ulang saat dibuka kembali
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
        content: node.data("tooltip") ?? "",
        codeContent: node.data("codeContent") ?? "",
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

    // Handle node click in modal to emit line info
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
      const rawNode = allRawNodes.find(
        (n: any) => (n.ms_id_node ?? n.id_node) === nodeId
      );
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

    // Handle tap on background in modal to clear highlight
    cy.on("tap", (evt) => {
      if (evt.target === cy && onNodeClick) {
        onNodeClick(null);
      }
    });
  }, [isModalOpen, modalCyInstance, elements, layout, onNodeClick, nodesWithStatus, rawNodes]);

  const cyStyle = React.useMemo(() => ({
    width: "100%",
    height: "100%",
    background: "#f9fafb",
    borderRadius: 8,
  }), []);

  const presetLayout = React.useMemo(() => ({ name: "preset" }), []);
  const stylesheet: cytoscape.StylesheetCSS[] = React.useMemo(() => [
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
  ], []);

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
                    layout={presetLayout}
                    stylesheet={stylesheet}
                    cy={(cy) => {
                      cyRef.current = cy;
                    }}
                    style={cyStyle}
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
                      <TooltipContent text={tooltip.content} code={tooltip.codeContent || undefined} />
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

      {/* Right-Panel Slide-Over for Expanded CFG */}
      {isModalOpen && (
        <>
          {/* Right Panel - Expanded dual resizable split-pane view */}
          <div
            style={{
              position: "fixed",
              top: 0,
              right: 0,
              width: "100vw",
              height: "100vh",
              zIndex: 9999,
              display: "flex",
              flexDirection: "column",
              background: "#1e1e24", // Modern dark slate background for the workspace
              boxShadow: "-8px 0 40px rgba(0, 0, 0, 0.4)",
              animation: "cfgSlideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1)",
              userSelect: isDragging ? "none" : "auto",
            }}
          >
            {/* Header bar */}
            <div
              style={{
                padding: "14px 24px",
                borderBottom: "1px solid rgba(255, 255, 255, 0.08)",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                flexShrink: 0,
                background: "rgba(30, 30, 36, 0.95)",
                backdropFilter: "blur(12px)",
              }}
            >
              <div style={{ display: "flex", flexDirection: "column", gap: 2 }}>
                <h3 style={{
                  fontSize: "15px",
                  fontWeight: 600,
                  color: "#f8fafc",
                  margin: 0,
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                }}>
                  <Maximize size={15} color="#3b82f6" />
                  Workspace Analisis Program (Kode & CFG)
                </h3>
                <p style={{ fontSize: "11px", color: "#94a3b8", margin: 0 }}>
                  Geser pembatas di tengah untuk merubah ukuran panel kiri dan kanan secara fleksibel.
                </p>
              </div>
              <button
                onClick={() => setIsModalOpen(false)}
                style={{
                  background: "rgba(255, 255, 255, 0.06)",
                  color: "#e2e8f0",
                  border: "1px solid rgba(255, 255, 255, 0.1)",
                  borderRadius: 8,
                  padding: "6px 14px",
                  fontSize: 12,
                  fontWeight: 500,
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  gap: 6,
                  transition: "all 0.15s ease",
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = "rgba(255, 255, 255, 0.12)";
                  e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.2)";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = "rgba(255, 255, 255, 0.06)";
                  e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.1)";
                }}
                title="Tutup Workspace"
              >
                <Minimize size={13} />
                Tutup Workspace
              </button>
            </div>

            {/* Split Panels */}
            <div style={{ display: "flex", flex: 1, overflow: "hidden", position: "relative" }}>

              {/* Left Panel: Code Program */}
              <div
                style={{
                  width: `${splitPercent}%`,
                  height: "100%",
                  overflow: "hidden",
                  display: "flex",
                  flexDirection: "column",
                  background: "#282a36", // Dracula theme background
                  borderRight: "1px solid rgba(255, 255, 255, 0.05)",
                }}
              >
                {/* Visual Header Tab */}
                <div style={{ padding: "8px 16px", background: "#21222c", color: "#6272a4", fontSize: 11, borderBottom: "1px solid #44475a", display: "flex", alignItems: "center", gap: 6, flexShrink: 0 }}>
                  <div style={{ width: 10, height: 10, borderRadius: "50%", background: "#ff5555" }} />
                  <div style={{ width: 10, height: 10, borderRadius: "50%", background: "#f1fa8c" }} />
                  <div style={{ width: 10, height: 10, borderRadius: "50%", background: "#50fa7b" }} />
                  <span style={{ marginLeft: 6, color: "#a9b2c3", fontFamily: "monospace" }}>source.java</span>
                </div>

                {/* Scrollable Code Viewer */}
                <div
                  ref={modalCodeContainerRef}
                  style={{
                    flex: 1,
                    overflowY: "auto",
                    fontFamily: "'Cascadia Code', 'Fira Code', 'JetBrains Mono', 'Consolas', monospace",
                    fontSize: "12.5px",
                    lineHeight: "1.7",
                    padding: "12px 0",
                  }}
                >
                  {sourceCode ? sourceCode.split('\n').map((line, index) => {
                    const lineNumber = index + 1;
                    const isHighlighted = highlightedLines
                      && lineNumber >= highlightedLines.start
                      && lineNumber <= highlightedLines.end;

                    const gutterWidth = Math.max(2, String(sourceCode.split('\n').length).length) * 10 + 20;

                    return (
                      <div
                        key={lineNumber}
                        ref={isHighlighted && lineNumber === highlightedLines!.start ? modalHighlightRef : undefined}
                        style={{
                          display: 'flex',
                          alignItems: 'stretch',
                          minHeight: '1.7em',
                          background: isHighlighted ? 'rgba(59, 130, 246, 0.22)' : 'transparent',
                          borderLeft: isHighlighted ? '3px solid #3b82f6' : '3px solid transparent',
                          transition: 'background 0.3s ease, border-left 0.3s ease',
                          position: 'relative',
                        }}
                      >
                        {isHighlighted && (
                          <div
                            style={{
                              position: 'absolute',
                              inset: 0,
                              background: 'linear-gradient(90deg, rgba(59,130,246,0.15) 0%, rgba(59,130,246,0.04) 50%, transparent 100%)',
                              pointerEvents: 'none',
                            }}
                          />
                        )}
                        <span
                          style={{
                            display: 'inline-block',
                            width: gutterWidth,
                            minWidth: gutterWidth,
                            textAlign: 'right',
                            paddingRight: '16px',
                            color: isHighlighted ? '#93c5fd' : '#6272a4',
                            userSelect: 'none',
                            fontWeight: isHighlighted ? 600 : 400,
                            borderRight: '1px solid rgba(98, 114, 164, 0.2)',
                            marginRight: '12px',
                            flexShrink: 0,
                          }}
                        >
                          {lineNumber}
                        </span>
                        <span style={{ color: '#f8f8f2', whiteSpace: 'pre', paddingRight: '16px', zIndex: 1 }}>
                          {highlightJavaCode(line || ' ')}
                        </span>
                      </div>
                    );
                  }) : (
                    <div style={{ padding: '12px 16px', color: '#6272a4' }}>
                      Loading source code...
                    </div>
                  )}
                </div>
              </div>

              {/* Draggable Divider Line in the Middle */}
              <div
                onMouseDown={startSplitResize}
                style={{
                  position: "absolute",
                  top: 0,
                  left: `calc(${splitPercent}% - 6px)`,
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
                {/* Visual Line Divider Track */}
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

                {/* Visible Pill Grip Handle */}
                <div
                  style={{
                    width: 24,
                    height: 56,
                    borderRadius: 12,
                    backgroundColor: isDragging ? "#2563eb" : "#0b6af0ff",
                    border: "1px solid " + (isDragging ? "#3b82f6" : "rgba(255, 255, 255, 0.15)"),
                    boxShadow: "0 10px 25px -5px rgba(243, 238, 238, 0.5), 0 8px 10px -6px rgba(0, 0, 0, 0.5)",
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: 4,
                    transition: "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)",
                    zIndex: 101,
                    transform: isDragging ? "scale(1.08)" : "scale(1)",
                  }}
                  onMouseEnter={(e) => {
                    if (!isDragging) {
                      e.currentTarget.style.backgroundColor = "#3b82f6";
                      e.currentTarget.style.borderColor = "#60a5fa";
                      e.currentTarget.style.transform = "scale(1.05)";
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!isDragging) {
                      e.currentTarget.style.backgroundColor = "#334155";
                      e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.15)";
                      e.currentTarget.style.transform = "scale(1)";
                    }
                  }}
                >
                  {/* Grip ridges */}
                  <div style={{ width: 2, height: 16, backgroundColor: "rgba(255, 255, 255, 0.5)", borderRadius: 1 }} />
                  <div style={{ width: 2, height: 16, backgroundColor: "rgba(255, 255, 255, 0.5)", borderRadius: 1 }} />
                </div>
              </div>

              {/* Right Panel: CFG Component */}
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
                    <CytoscapeComponent
                      elements={elements}
                      layout={presetLayout}
                      stylesheet={stylesheet}
                      cy={(cy) => {
                        modalCyRef.current = cy;
                        setModalCyInstance((prev) => prev === cy ? prev : cy);
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
                      <TooltipContent text={modalTooltip.content} code={modalTooltip.codeContent || undefined} />
                    </div>
                  )}

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
                        label: "−",
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
                        onMouseEnter={(e) => e.currentTarget.style.background = "#f3f4f6"}
                        onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}
                      >
                        {label}
                      </button>
                    ))}
                  </div>
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

          {/* Animation keyframe */}
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
        </>
      )}
    </div>
  );
};

export default CFGCard;