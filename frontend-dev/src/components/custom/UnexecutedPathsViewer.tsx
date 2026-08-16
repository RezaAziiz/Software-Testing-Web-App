import React, { useState } from 'react';
import { ChevronDown, ChevronUp, CheckCircle2 } from 'lucide-react';

interface NodeStatusInfo {
  id?: string;
  status_execution?: string;
  status?: string;
}

interface UnexecutedPathsViewerProps {
  paths?: string[];
  nodesWithStatus?: NodeStatusInfo[];
  defaultCollapsed?: boolean;
}

export const UnexecutedPathsViewer: React.FC<UnexecutedPathsViewerProps> = ({
  paths = [],
  nodesWithStatus = [],
  defaultCollapsed = false,
}) => {
  const [isCollapsed, setIsCollapsed] = useState(defaultCollapsed);

  // Helper map for quick node execution status lookup
  const nodeStatusMap = React.useMemo(() => {
    const map = new Map<string, string>();
    if (Array.isArray(nodesWithStatus)) {
      nodesWithStatus.forEach((node) => {
        const id = String(node.id || '');
        const status = node.status || node.status_execution || '';
        map.set(id, status);
      });
    }
    return map;
  }, [nodesWithStatus]);

  // Helper to check if node ID is unexecuted
  const isNodeUnexecuted = (nodeId: string): boolean => {
    const cleanId = nodeId.trim();
    const lower = cleanId.toLowerCase();
    if (lower === 'start' || lower === 'end') {
      return false;
    }
    const status = nodeStatusMap.get(cleanId);
    if (!status) {
      // If node status is not explicitly present in map, treat numbered decision nodes in unexecuted paths as unexecuted
      return true;
    }
    return status === 'N' || status === 'NOT_COVERED' || status === 'PARTLY_COVERED';
  };

  // Helper to parse path string like "Start -> 1 -> 2 -> 9 -> 14 -> End" or "Start→1→2→9→14→End"
  const parsePathTokens = (pathStr: string): string[] => {
    if (!pathStr) return [];
    return pathStr
      .replace(/→/g, '->')
      .split('->')
      .map((s) => s.trim())
      .filter((s) => s.length > 0);
  };

  const totalPaths = paths.length;

  return (
    <div className="w-full bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden transition-all">
      {/* Header — Warna Biru */}
      <div
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="flex items-center justify-between px-5 py-3.5 bg-[#0b48b3] hover:bg-[#093c96] cursor-pointer select-none transition-colors text-white"
      >
        <div className="flex items-center gap-3">
          <h3 className="text-sm font-bold text-white tracking-wide">
            Jalur Belum Tereksekusi
          </h3>
          <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-white/20 text-white border border-white/30 backdrop-blur-xs">
            {totalPaths} jalur
          </span>
        </div>

        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            setIsCollapsed(!isCollapsed);
          }}
          style={{ background: 'transparent', border: 'none', boxShadow: 'none', padding: '4px' }}
          className="text-white/90 hover:text-white cursor-pointer rounded-lg transition-colors flex items-center justify-center hover:bg-white/10"
          aria-label={isCollapsed ? "Expand paths" : "Collapse paths"}
        >
          {isCollapsed ? <ChevronDown className="w-5 h-5 text-white" /> : <ChevronUp className="w-5 h-5 text-white" />}
        </button>
      </div>

      {/* Body Content — Warna Putih */}
      {!isCollapsed && (
        <div className="p-5 bg-white space-y-4">
          {totalPaths === 0 ? (
            <div className="flex flex-col items-center justify-center py-6 text-center gap-2">
              <div className="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center">
                <CheckCircle2 className="w-7 h-7 text-green-600" />
              </div>
              <p className="text-sm font-bold text-green-700">
                Semua jalur telah tereksekusi!
              </p>
            </div>
          ) : (
            <>
              {/* Scrollable list container */}
              <div className="flex flex-col gap-3 max-h-[300px] overflow-y-auto pr-1.5 custom-light-scrollbar">
                {paths.map((pathStr, pathIdx) => {
                  const tokens = parsePathTokens(pathStr);
                  return (
                    <div
                      key={pathIdx}
                      className="flex items-center flex-wrap gap-1.5 bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 hover:border-slate-300 transition-colors shadow-2xs"
                    >
                      {tokens.map((token, tIdx) => {
                        const isStart = token.toLowerCase() === 'start';
                        const isEnd = token.toLowerCase() === 'end';
                        const unexec = !isStart && !isEnd && isNodeUnexecuted(token);

                        return (
                          <React.Fragment key={tIdx}>
                            {/* Node Pill */}
                            <span
                              className={`inline-flex items-center justify-center px-3 py-1 text-xs font-mono rounded-full transition-all ${isStart || isEnd
                                ? 'bg-slate-200/90 text-slate-700 font-semibold border border-slate-300/80'
                                : unexec
                                  ? 'bg-red-100 text-red-700 border border-red-300 font-bold shadow-2xs'
                                  : 'bg-slate-100 text-slate-700 border border-slate-200 font-medium'
                                }`}
                            >
                              {token.toLowerCase()}
                            </span>

                            {/* Arrow separator */}
                            {tIdx < tokens.length - 1 && (
                              <span className={`text-xs font-mono px-0.5 ${unexec ? 'text-red-500 font-bold' : 'text-slate-400'}`}>
                                →
                              </span>
                            )}
                          </React.Fragment>
                        );
                      })}
                    </div>
                  );
                })}
              </div>

              {/* Legend at bottom */}
              <div className="flex items-center gap-2 pt-3 border-t border-slate-100 text-xs text-slate-600 font-medium">
                <span className="inline-block w-3 h-3 rounded-full bg-red-500 border border-red-600 shrink-0" />
                <span>node dan edge yang belum tereksekusi</span>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default UnexecutedPathsViewer;