import React from "react";
import AddTestCaseCard from "@/components/custom/AddTestCaseCard";
import MinimalCard from "@/components/custom/MinimalCard";
import ModuleWorkspaceLayout from "@/components/custom/ModuleWorkspaceLayout";
import { useAuthGuard } from "@/hooks/useAuthGuard";

const CreateTestCasePage: React.FC = () => {
  const { session } = useAuthGuard();

  return (
    <ModuleWorkspaceLayout>
      {/* Section 3: Test Case dan Hasil Pengujian (Full Width) */}
      {session?.login_type === "student" && (
        <div className="w-full flex flex-col gap-6 pb-6">
          <AddTestCaseCard />
          <MinimalCard />
        </div>
      )}
    </ModuleWorkspaceLayout>
  );
};

export default CreateTestCasePage;
