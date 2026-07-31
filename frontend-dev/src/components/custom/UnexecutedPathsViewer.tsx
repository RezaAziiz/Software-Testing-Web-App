import React from 'react';

interface UnexecutedPathsViewerProps {
  paths: string[];
}

const UnexecutedPathsViewer: React.FC<UnexecutedPathsViewerProps> = ({ paths }) => {
  return (
    <div className="mt-8 w-full max-w-xs text-left">
      <p className="text-sm text-center font-medium mb-2">
        Jalur Belum Tereksekusi
      </p>
      {paths && paths.length > 0 ? (
        <div className="ml-4 max-h-40 overflow-y-auto rounded border border-gray-200 bg-gray-50 px-3 py-2">
          {paths.map((path) => (
            <p
              key={path}
              className="font-mono text-sm text-gray-800 leading-6"
            >
              {path}
            </p>
          ))}
        </div>
      ) : (
        <p className="text-sm text-center text-gray-400">
          Tidak ada jalur yang belum tereksekusi.
        </p>
      )}
    </div>
  );
};

export default UnexecutedPathsViewer;