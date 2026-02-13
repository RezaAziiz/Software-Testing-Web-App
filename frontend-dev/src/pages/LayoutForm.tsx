import React, { ReactNode } from "react";
import NavbarForm from "@/components/custom/NavbarForm";

interface LayoutFormProps {
  children: ReactNode;
  screenName: string;
}

const LayoutForm: React.FC<LayoutFormProps> = ({ children, screenName }) => {
  return (
    <div>
      <NavbarForm screenName={screenName}/>
      <main id="main">
        {children}
      </main>
    </div>
  );
};

export default LayoutForm;
