import React, { useState, useCallback } from "react";

export const useSplitPane = (initialPercent: number = 45) => {
  const [splitPercent, setSplitPercent] = useState<number>(initialPercent);
  const [isDragging, setIsDragging] = useState(false);

  const startSplitResize = useCallback((mouseDownEvent: React.MouseEvent) => {
    mouseDownEvent.preventDefault();
    setIsDragging(true);

    const doDrag = (mouseMoveEvent: MouseEvent) => {
      const newPercent = (mouseMoveEvent.clientX / window.innerWidth) * 100;
      // Constraints:
      // Minimum: 0% (allow complete collapse of left panel)
      // Maximum: 75% (left panel cannot grow above 75%)
      if (newPercent >= 0 && newPercent <= 75) {
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

  return {
    splitPercent,
    isDragging,
    startSplitResize,
    setSplitPercent,
  };
};
