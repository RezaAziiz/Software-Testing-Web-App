import React, { useState, useEffect } from "react";

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

const Pagination: React.FC<PaginationProps> = ({
  currentPage,
  totalPages,
  onPageChange,
}) => {
  const [pagesToShow, setPagesToShow] = useState<number>(5);

  // Function to update the pages to show based on screen size
  useEffect(() => {
    const updatePagesToShow = () => {
      if (window.innerWidth < 768) {
        setPagesToShow(5); // Small screen
      } else {
        setPagesToShow(8); // Larger screen
      }
    };

    // Initial setting
    updatePagesToShow();

    // Event listener for resizing the window
    window.addEventListener("resize", updatePagesToShow);
    return () => {
      window.removeEventListener("resize", updatePagesToShow);
    };
  }, []);

const generatePageNumbers = () => {
    const pages: (string | number)[] = [];

    if (totalPages <= pagesToShow) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      const half = Math.floor(pagesToShow / 2);
      let startPage = Math.max(currentPage - half, 1);
      let endPage = Math.min(currentPage + half, totalPages);

      if (currentPage <= half) {
        endPage = pagesToShow;
      }

      if (currentPage + half >= totalPages) {
        startPage = totalPages - pagesToShow + 1;
      }

      for (let i = startPage; i <= endPage; i++) {
        pages.push(i);
      }

      if (startPage > 1) {
        pages.unshift("..");
        pages.unshift(1);
      }

      if (endPage < totalPages) {
        pages.push("..");
        pages.push(totalPages);
      }
    }

    return pages;
  };
  return (
    <div className="flex justify-center items-center py-2 text-xs lg:text-sm">
      <button
        className={`mx-0.5 md:mx-2 px-0.5 md:px-2 py-1 rounded-md ${
          currentPage === 1
            ? "bg-gray-200 cursor-not-allowed"
            : "bg-blue-500 text-white hover:bg-blue-600"
        }`}
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
      >
        Prev
      </button>
      {generatePageNumbers().map((page, index) => (
        <button
          key={index}
          className={`mx-0.5 md:mx-2 px-1 md:px-2 py-1 rounded-md ${
            currentPage === page
              ? "bg-blue-500 text-white"
              : "bg-gray-200 hover:bg-gray-300"
          }`}
          onClick={() => typeof page === "number" && onPageChange(page)}
          disabled={typeof page !== "number"}
        >
          {page}
        </button>
      ))}
      <button
        className={`mx-0.5 md:mx-2 px-0.5 md:px-2 py-1 rounded-md ${
          currentPage === totalPages
            ? "bg-gray-200 cursor-not-allowed"
            : "bg-blue-500 text-white hover:bg-blue-600"
        }`}
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
      >
        Next
      </button>
    </div>
  );
};

export default Pagination;
