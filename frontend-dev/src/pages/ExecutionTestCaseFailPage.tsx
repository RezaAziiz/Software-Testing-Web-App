import React, { useEffect, useRef } from "react";
import { useLocation, useNavigate, useSearchParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import AddTestCaseCard from "@/components/custom/AddTestCaseCard";
import FailCard from "@/components/custom/FailCard";
import ModuleWorkspaceLayout from "@/components/custom/ModuleWorkspaceLayout";
import { useAuthGuard } from "@/hooks/useAuthGuard";

const ExecutionTestCaseFailPage: React.FC = () => {
  useAuthGuard({ requiredRole: "student" });

  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams] = useSearchParams();
  const bottomRef = useRef<HTMLDivElement>(null);

  const { state: navigationData } = location;
  const modulId = searchParams.get("topikModulId");

  // Scroll otomatis ke bagian bawah saat halaman selesai dimuat
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  // Navigasi ke halaman hasil pengujian lengkap
  const handleNavigateToTestResult = () => {
    navigate("/test-result?topikModulId=" + modulId, {
      state: {
        modul_id: navigationData?.modul_id,
      },
    });
  };

  return (
    <ModuleWorkspaceLayout>
      {/* Section 3: Test Case, Hasil Pengujian, dan Tombol (Full Width) */}
      <div className="w-full flex flex-col gap-6 pb-6">
        <AddTestCaseCard />
        <div className="w-full">
          <FailCard
            percentageCoverage={navigationData?.coverage_score || 0}
            minimumCoverage={navigationData?.minimum_coverage_score || 0}
            statusEksekusi={navigationData?.status_eksekusi || false}
            tanggalEksekusi={navigationData?.tgl_eksekusi || ""}
            modulId={navigationData?.modul_id || ""}
          />
        </div>
        <Button
          className="text-sm bg-white rounded-lg font-bold text-red-700 border border-red-700 hover:bg-red-700 hover:text-white button-custom"
          onClick={handleNavigateToTestResult}
        >
          Laporan Pengujian
        </Button>
        <div ref={bottomRef}></div>
      </div>
    </ModuleWorkspaceLayout>
  );
};

export default ExecutionTestCaseFailPage;
