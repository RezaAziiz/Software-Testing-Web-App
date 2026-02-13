import React, { ReactNode } from "react";
import { Navbar } from "@/components/custom/Navbar";

interface LayoutProps {
  children: ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div>
      <Navbar />
      <main id="main">
        {children}
      </main>
    </div>
  );
};

export default Layout;
