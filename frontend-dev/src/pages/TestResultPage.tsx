import Layout from "./Layout";
import { useState, useEffect } from "react";
import { Menu } from "@/components/custom/Menu";
import CFGCard from "@/components/custom/CFGCard";
import TestResultCard from "@/components/custom/TestResultCard";
import UnexecutedPathsViewer from "@/components/custom/UnexecutedPathsViewer";
import { useNavigate } from "react-router-dom";
import { CheckCircle2, AlertTriangle, XCircle } from "lucide-react";

interface DataResultTest {
  coverageScore: number;
  point: number;
  totalTestCase: number;
  totalPassTestCase: number;
  totalFailedTestCase: number;
  executionDate: string;
  linkReportTesting: string;
  linkReportCoverage: string;
  linkSourceCoverage: string;
  minimum_coverage_score?: number;
  data_cfg: {
    nodes: any[];
    edges: any[];
    unexecutedPaths?: string[];
  };
}

const TestResultPage = () => {
  const navigate = useNavigate();
  const apiUrl = import.meta.env.VITE_API_URL;
  let apiKey = import.meta.env.VITE_API_KEY;
  const sessionData = localStorage.getItem("session");
  let session = null;
  if (sessionData != null) {
    session = JSON.parse(sessionData);
    apiKey = session.token;
  }

  const queryParameters = new URLSearchParams(window.location.search);
  const modulId = queryParameters.get("topikModulId");
  const defaultData: DataResultTest = {
    coverageScore: 0,
    point: 0,
    totalTestCase: 0,
    totalPassTestCase: 0,
    totalFailedTestCase: 0,
    executionDate: "",
    linkReportTesting: "",
    linkReportCoverage: "",
    linkSourceCoverage: "",
    minimum_coverage_score: 80,
    data_cfg: {
      nodes: [],
      edges: [],
      unexecutedPaths: [],
    },
  };

  const [dataTestResult, setDataTestResult] =
    useState<DataResultTest>(defaultData);
  const [error, setError] = useState<string | null>(null);
  const [highlightedLines, setHighlightedLines] = useState<{
    start: number;
    end: number;
  } | null>(null);
  const [className, setClassName] = useState<string>("");

  const fetchDataTestResult = async () => {
    try {
      const response = await fetch(
        `${apiUrl}/modul/getResultTest/${modulId}`,
        {
          method: "GET",
          headers: {
            Accept: "application/json",
            Authorization: `Bearer ${apiKey}`,
          },
        }
      );

      if (!response.ok) {
        if (response.status === 403) {
          navigate("/error");
        } else if (response.status !== 404) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
      } else {
        const data = await response.json();
        setDataTestResult(data || null);
      }
    } catch (error) {
      console.error("Error fetching data:", error);
      setError((error as Error).message);
    }
  };

  // Fetch class name for Source Code Coverage header
  const fetchClassName = async () => {
    try {
      const response = await fetch(
        `${apiUrl}/modul/detailByIdTopikModul/${modulId}`,
        {
          method: "GET",
          headers: {
            Accept: "application/json",
            Authorization: `Bearer ${apiKey}`,
          },
        }
      );
      if (response.ok) {
        const data = await response.json();
        const name = data?.data?.data_modul?.ms_class_name;
        if (name) setClassName(name + ".java");
      }
    } catch (e) {
      console.error("Error fetching class name:", e);
    }
  };

  useEffect(() => {
    window.scrollTo(0, 0);
    if (session === null) {
      navigate("/login");
    } else if (session.login_type != "student") {
      navigate("/dashboard-teacher");
    } else {
      fetchDataTestResult();
      fetchClassName();
    }
  }, []);

  // --- Derived values ---
  const unexecutedPaths = dataTestResult.data_cfg?.unexecutedPaths ?? [];
  const nodes = dataTestResult.data_cfg?.nodes ?? [];
  const edges = dataTestResult.data_cfg?.edges ?? [];

  // Calculate total paths from cyclomatic complexity: V(G) = E - N + 2
  const totalPaths = Math.max(edges.length - nodes.length + 2, 0);
  const coveredPaths = Math.max(totalPaths - unexecutedPaths.length, 0);

  const allTestCasePass =
    dataTestResult.totalTestCase > 0 &&
    dataTestResult.totalFailedTestCase === 0;
  const allPathsCovered = unexecutedPaths.length === 0;
  const minimumCoverage = dataTestResult.minimum_coverage_score ?? 80;
  const coverageMet = dataTestResult.coverageScore >= minimumCoverage;

  const hasFailedTests = dataTestResult.totalFailedTestCase > 0;
  const allTargetsMet = allTestCasePass && allPathsCovered && coverageMet;

  // Badge status helpers
  const testCaseBadgeOk = allTestCasePass;
  const pathCoverageBadgeOk = allPathsCovered;
  const codeCoverageBadgeOk = coverageMet;

  // JaCoCo iframe URL
  const timestamp = new Date().getTime();
  const jacocoIframeUrl = dataTestResult.linkSourceCoverage
    ? `${apiUrl}/${dataTestResult.linkSourceCoverage}?t=${timestamp}`
    : null;

  if (error) {
    return (
      <div className="p-4 bg-white rounded-lg shadow-md h-screen">
        Error: {error}
      </div>
    );
  }

// Remove unused variables

  return (
    <Layout>
      <Menu />
      <div className="flex flex-col w-screen min-h-screen p-4 gap-6 bg-slate-50 overflow-x-hidden">
        {/* ===== SECTION 1: Ringkasan Hasil Pengujian ===== */}
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
          <h2 className="text-lg font-bold text-slate-800 mb-5">
            Ringkasan Hasil Pengujian
          </h2>

          {/* Stat Badges */}
          <div className="flex flex-col md:flex-row gap-4 mb-5">
            {/* Test Case Result */}
            <div className="flex-1 flex items-center gap-3 bg-slate-50 border border-slate-200 rounded-xl px-5 py-3">
              {testCaseBadgeOk ? (
                <CheckCircle2 className="w-7 h-7 text-green-500 shrink-0" />
              ) : (
                <AlertTriangle className="w-7 h-7 text-orange-500 shrink-0" />
              )}
              <div>
                <p className="text-xs text-slate-500">Test Case Result</p>
                <p className="text-base font-bold text-slate-800">
                  {dataTestResult.totalPassTestCase}/
                  {dataTestResult.totalTestCase} Pass
                </p>
              </div>
            </div>

            {/* Path Coverage */}
            <div className="flex-1 flex items-center gap-3 bg-slate-50 border border-slate-200 rounded-xl px-5 py-3">
              {pathCoverageBadgeOk ? (
                <CheckCircle2 className="w-7 h-7 text-green-500 shrink-0" />
              ) : (
                <AlertTriangle className="w-7 h-7 text-orange-500 shrink-0" />
              )}
              <div>
                <p className="text-xs text-slate-500">Path Coverage</p>
                <p className="text-base font-bold text-slate-800">
                  {coveredPaths}/{totalPaths} Jalur Tercakup
                </p>
              </div>
            </div>

            {/* Code Coverage */}
            <div className="flex-1 flex items-center gap-3 bg-slate-50 border border-slate-200 rounded-xl px-5 py-3">
              {codeCoverageBadgeOk ? (
                <CheckCircle2 className="w-7 h-7 text-green-500 shrink-0" />
              ) : (
                <AlertTriangle className="w-7 h-7 text-orange-500 shrink-0" />
              )}
              <div>
                <p className="text-xs text-slate-500">Code Coverage</p>
                <p className="text-base font-bold text-slate-800">
                  {dataTestResult.coverageScore}%
                </p>
              </div>
            </div>
          </div>

          {/* Alert Box */}
          {dataTestResult.executionDate !== "" && (
            <>
              {allTargetsMet ? (
                <div className="flex items-start gap-3 bg-green-50 border border-green-200 rounded-xl p-4">
                  <CheckCircle2 className="w-6 h-6 text-green-600 shrink-0 mt-0.5" />
                  <div>
                    <p className="font-bold text-green-800 text-sm">
                      Semua target pengujian tercapai
                    </p>
                    <p className="text-green-700 text-sm mt-1">
                      Seluruh test case Pass, semua jalur pada CFG telah
                      tercakup, dan code coverage mencapai {minimumCoverage}%.
                    </p>
                  </div>
                </div>
              ) : hasFailedTests ? (
                <div className="flex items-start gap-3 bg-red-50 border border-red-200 rounded-xl p-4">
                  <XCircle className="w-6 h-6 text-red-600 shrink-0 mt-0.5" />
                  <div>
                    <p className="font-bold text-red-800 text-sm">
                      Terdapat test case yang gagal
                    </p>
                    <p className="text-red-700 text-sm mt-1">
                      {dataTestResult.totalFailedTestCase} dari{" "}
                      {dataTestResult.totalTestCase} test case gagal. Perbaiki
                      test case yang gagal terlebih dahulu.
                    </p>
                  </div>
                </div>
              ) : !coverageMet ? (
                <div className="flex items-start gap-3 bg-orange-50 border border-orange-200 rounded-xl p-4">
                  <AlertTriangle className="w-6 h-6 text-orange-600 shrink-0 mt-0.5" />
                  <div>
                    <p className="font-bold text-orange-800 text-sm">
                      Code Coverage masih rendah
                    </p>
                    <p className="text-orange-700 text-sm mt-1">
                      Semua test case berhasil dijalankan, tetapi code coverage ({dataTestResult.coverageScore}%) masih di bawah target minimal ({minimumCoverage}%). Tambahkan test case untuk meningkatkan coverage.
                    </p>
                  </div>
                </div>
              ) : (
                <div className="flex items-start gap-3 bg-orange-50 border border-orange-200 rounded-xl p-4">
                  <AlertTriangle className="w-6 h-6 text-orange-600 shrink-0 mt-0.5" />
                  <div>
                    <p className="font-bold text-orange-800 text-sm">
                      Jalur eksekusi (Path) belum lengkap
                    </p>
                    <p className="text-orange-700 text-sm mt-1">
                      Target minimum Code Coverage tercapai ({dataTestResult.coverageScore}%), namun masih ada {unexecutedPaths.length} jalur program (Path) yang belum dilalui oleh test case Anda.
                    </p>
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* ===== SECTION 2: Source Code Coverage (Kiri) + CFG & Jalur Belum Tereksekusi (Kanan) ===== */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 w-full items-stretch lg:h-[720px]">
          {/* Kolom Kiri: Source Code Coverage (JaCoCo) */}
          <div className="flex flex-col min-w-0 bg-white rounded-2xl shadow-sm border border-slate-200 p-5 h-full">
            <div className="flex items-center justify-between mb-3 border border-slate-200 rounded-t-xl px-4 py-3 bg-slate-50 shrink-0">
              <span className="text-sm font-bold text-slate-800">
                Source code coverage {className ? `(${className})` : ""}
              </span>
              <div className="flex items-center gap-3 text-xs">
                <span className="flex items-center gap-1.5 font-medium text-slate-600">
                  <span className="inline-block w-2.5 h-2.5 rounded-full bg-green-500" />
                  Fully executed
                </span>
                <span className="flex items-center gap-1.5 font-medium text-slate-600">
                  <span className="inline-block w-2.5 h-2.5 rounded-full bg-yellow-500" />
                  Partial
                </span>
                <span className="flex items-center gap-1.5 font-medium text-slate-600">
                  <span className="inline-block w-2.5 h-2.5 rounded-full bg-red-500" />
                  Not executed
                </span>
              </div>
            </div>

            {dataTestResult.totalTestCase > 0 &&
            dataTestResult.totalFailedTestCase === 0 &&
            jacocoIframeUrl ? (
              <div className="border border-t-0 border-slate-200 rounded-b-xl overflow-hidden min-h-[400px] flex-1 relative">
                <iframe
                  src={jacocoIframeUrl}
                  className="w-full h-full border-0 absolute"
                  style={{ height: "calc(100% + 80px)", top: "-80px", left: 0 }}
                  title="JaCoCo Source Code Coverage"
                />
              </div>
            ) : dataTestResult.totalFailedTestCase > 0 ? (
              <div className="p-8 text-center bg-red-50 rounded-xl border border-red-200 flex-1 flex items-center justify-center">
                <p className="text-sm font-semibold text-red-700">
                  Code Coverage gagal terbentuk karena terdapat test case dengan status Fail.
                </p>
              </div>
            ) : (
              <div className="p-8 text-center bg-slate-50 rounded-xl border border-slate-200 flex-1 flex items-center justify-center">
                <p className="text-sm text-slate-500">
                  Code Coverage tidak terbentuk karena belum ada test case.
                </p>
              </div>
            )}
          </div>

          {/* Kolom Kanan: CFG Graph (Atas) + Jalur Belum Tereksekusi (Bawah) */}
          <div className="flex flex-col gap-6 min-w-0 min-h-0 h-full">
            {/* Control Flow Graph */}
            <div className="w-full flex-1 min-h-0">
              <CFGCard
                showCyclomaticComplexity={false}
                showCodeCoverage={false}
                codeCoveragePercentage={dataTestResult.coverageScore}
                nodesWithStatus={dataTestResult.data_cfg?.nodes}
                edgesWithStatus={dataTestResult.data_cfg?.edges}
                unexecutedPaths={unexecutedPaths}
                onNodeClick={setHighlightedLines}
                highlightedLines={highlightedLines}
                jacocoUrl={
                  dataTestResult.linkSourceCoverage
                    ? `${apiUrl}/${dataTestResult.linkSourceCoverage}`
                    : null
                }
              />
            </div>

            {/* Jalur Belum Tereksekusi (Collapsible & Scrollable) */}
            <div className="w-full">
              <UnexecutedPathsViewer
                paths={unexecutedPaths}
                nodesWithStatus={dataTestResult.data_cfg?.nodes}
                defaultCollapsed={false}
              />
            </div>
          </div>
        </div>

        {/* ===== SECTION 3: Tabel Hasil Test Case ===== */}
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
          <h3 className="text-base font-bold text-slate-800 mb-4">
            Tabel Test Case
          </h3>
          <TestResultCard dataResultTest={dataTestResult} />
        </div>
      </div>
    </Layout>
  );
};

export default TestResultPage;