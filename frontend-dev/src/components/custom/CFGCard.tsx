import React, { useEffect, useState } from "react";
import ReactFlow, { Controls, Background } from "reactflow";
import PercentageCodeCoverage from "./PresentaseCodeCoverage";
import "reactflow/dist/style.css";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import "../../index.css";

const calculateCyclomaticComplexity = (edgesCount: number, nodesCount: number) => {
  return edgesCount - nodesCount + 2;
};

type Node = {
  id: string;
  data: { label: string };
  position: { x: number; y: number };
  type: string;
  style: object;
};

type Edge = {
  id: string;
  source: string;
  target: string;
  label?: string;
};

type CFGCardProps = {
  showCyclomaticComplexity?: boolean;
  showCodeCoverage?: boolean;
  codeCoveragePercentage?: number;
};

const CFGCard: React.FC<CFGCardProps> = ({
  showCyclomaticComplexity = false,
  showCodeCoverage = false,
  codeCoveragePercentage,
}) => {
  const apiUrl = import.meta.env.VITE_API_URL;
  let apiKey = import.meta.env.VITE_API_KEY;
  // const modulId = import.meta.env.VITE_MODULE_ID;
  const sessionData = localStorage.getItem('session')
  if (sessionData != null){
      const session = JSON.parse(sessionData);
      apiKey = session.token
  }
  const queryParameters = new URLSearchParams(window.location.search)
  const modulId = queryParameters.get("topikModulId")

  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchCFG = async ()=>{
    fetch(`${apiUrl}/modul/detailByIdTopikModul/${modulId}`, {
      method: "GET",
      headers: {
        Accept: "application/json",
        Authorization: `Bearer ${apiKey}`,
      },
    })
    .then((response) => response.json())
    .then((data) => {
      console.log("Data CFG:", data.data.data_cfg.nodes); // Cetak data CFG ke konsol
      
      const nodesData = data.data.data_cfg.nodes.map((node: any) => ({
        id: node.ms_id_node,
        data: { label: node.ms_line_number.toString() },
        position: { x: 250+((node.ms_no%2)*50), y: 100 * node.ms_no },
        type: "default",
        style: {
          width: 50,
          height: 50,
          borderRadius: "50%",
          backgroundColor: "lightblue",
        },
      }));
  
      const edgesData = data.data.data_cfg.edges.map((edge: any) => ({
        id: `${edge.id_node_start}-${edge.id_node_finish}`,
        source: edge.id_node_start,
        target: edge.id_node_finish,
      }));
  
      setNodes(nodesData);
      setEdges(edgesData);
    })
    .catch((error) => {
      console.error("Failed to fetch data:", error);
    })
    .finally(() => {
      setLoading(false);
    });
  };
  useEffect(() => {
    fetchCFG();
  }, []);
  

  if (loading) {
    return (
      <div className="p-6 bg-white rounded-lg shadow-lg h-full space-y-6">
        <div className="bg-gray-100 p-4 rounded-lg">
          <Skeleton className="h-5 w-32 bg-gray-200" />
        </div>
        <div className="bg-gray-100 p-4 rounded-lg">
          <Skeleton className="h-5 w-full mb-4 bg-gray-200" />
          <Skeleton className="h-5 w-full mb-4 bg-gray-200" />
          <Skeleton className="h-5 w-full mb-4 bg-gray-200" />
          <Skeleton className="h-5 w-full mb-4 bg-gray-200" />
        </div>
      </div>

    );
  }

  const cyclomaticComplexity = calculateCyclomaticComplexity(edges.length, nodes.length);

  const containerStyle = {
    display: "flex",
    justifyContent: "space-between",
  };

  return (
    <div className="h-full w-full">
      <Card>
        <CardHeader className="pt-6">
          <CardTitle className="text-base module-title">Struktur Program</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col">
          <div className="w-full" style={containerStyle}>
            <div className="w-1/2">
              <p className="text-sm font-medium mb-2">Control Flow Graph</p>
              <div className="text-sm h-96 relative react-flow-container">
                <ReactFlow
                  nodes={nodes}
                  edges={edges}
                  style={{ width: "100%", height: "100%" }}
                  zoomOnScroll={false}
                  fitView
                >
                  <Background color="#f0f0f0" gap={16} />
                  <Controls />
                </ReactFlow>
              </div>
            </div>
            <div className="w-1/2 ml-3 flex flex-col items-center">
              {showCodeCoverage && codeCoveragePercentage !== undefined && (
                <>
                  <p className="text-sm font-medium mb-5">Presentase Code Coverage</p>
                  <PercentageCodeCoverage percentage={codeCoveragePercentage} />
                </>
              )}
              {showCyclomaticComplexity && (
                <>
                <p className="text-sm font-medium mb-2">Nilai Cyclomatic Complexity</p>
                <div className="text-sm flex items-start"> 
                  <div className="mr-4"> 
                    <div>V(G)</div>
                  </div>
                  <div>
                    <div className="flex flex-col"> 
                      <span>= E - N + 2</span>
                      <span>= {edges.length} - {nodes.length} + 2</span>
                      <span>= {cyclomaticComplexity}</span>
                    </div>
                  </div>
                </div>
              </>
              
              )}
            </div>
          </div>
        </CardContent>
        <CardFooter className="card-footer">
          {/* Konten footer card di sini */}
        </CardFooter>
      </Card>
    </div>
  );
};

export default CFGCard;
