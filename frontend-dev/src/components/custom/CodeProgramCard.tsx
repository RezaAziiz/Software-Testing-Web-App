import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useNavigate } from "react-router-dom";
import "../../index.css";

type HighlightedLines = { start: number; end: number } | null;

interface CodeProgramCardProps {
  highlightedLines?: HighlightedLines;
}

// Java keyword sets for syntax highlighting
const JAVA_KEYWORDS = new Set([
  "abstract", "assert", "boolean", "break", "byte", "case", "catch", "char",
  "class", "const", "continue", "default", "do", "double", "else", "enum",
  "extends", "final", "finally", "float", "for", "goto", "if", "implements",
  "import", "instanceof", "int", "interface", "long", "native", "new",
  "package", "private", "protected", "public", "return", "short", "static",
  "strictfp", "super", "switch", "synchronized", "this", "throw", "throws",
  "transient", "try", "void", "volatile", "while",
]);
const JAVA_LITERALS = new Set(["true", "false", "null"]);
const JAVA_TYPES = new Set([
  "String", "Integer", "Long", "Double", "Float", "Boolean", "Character",
  "Byte", "Short", "Object", "System", "Math", "Arrays", "Collections",
  "List", "Map", "Set", "ArrayList", "HashMap", "HashSet", "LinkedList",
  "Scanner", "Exception", "RuntimeException", "StringBuilder", "StringBuffer",
]);

/** Lightweight Java syntax highlighter – returns React elements */
const highlightJavaLine = (code: string): React.ReactNode[] => {
  const tokenRegex = /(\"(?:[^\"\\]|\\.)*\"|'(?:[^'\\]|\\.)*'|\/\/.*|\/\*[\s\S]*?\*\/|\b\d+(?:\.\d+)?[fFdDlL]?\b|@[a-zA-Z_$][a-zA-Z0-9_$]*|[a-zA-Z_$][a-zA-Z0-9_$]*|[^\\s]|\s+)/g;
  const tokens = code.match(tokenRegex) || [code];
  return tokens.map((token, i) => {
    // String literals
    if (/^["']/.test(token)) {
      return <span key={i} style={{ color: "#f1fa8c" }}>{token}</span>;
    }
    // Comments
    if (token.startsWith("//") || token.startsWith("/*")) {
      return <span key={i} style={{ color: "#6272a4", fontStyle: "italic" }}>{token}</span>;
    }
    // Annotations
    if (token.startsWith("@")) {
      return <span key={i} style={{ color: "#ffb86c" }}>{token}</span>;
    }
    // Numbers
    if (/^\d/.test(token)) {
      return <span key={i} style={{ color: "#bd93f9" }}>{token}</span>;
    }
    // Keywords
    if (JAVA_KEYWORDS.has(token)) {
      return <span key={i} style={{ color: "#ff79c6", fontWeight: 600 }}>{token}</span>;
    }
    // Literals (true/false/null)
    if (JAVA_LITERALS.has(token)) {
      return <span key={i} style={{ color: "#bd93f9" }}>{token}</span>;
    }
    // Common types
    if (JAVA_TYPES.has(token)) {
      return <span key={i} style={{ color: "#8be9fd", fontStyle: "italic" }}>{token}</span>;
    }
    // Method calls (word followed by parenthesis — approximate)
    // We detect this by checking next token, but for simplicity just color identifiers before (
    return <span key={i}>{token}</span>;
  });
};

const CodeProgramCard: React.FC<CodeProgramCardProps> = ({ highlightedLines = null }) => {
  const apiUrl = import.meta.env.VITE_API_URL;
  let apiKey = import.meta.env.VITE_API_KEY;

  const navigate = useNavigate();

  const sessionData = localStorage.getItem('session');
  if (sessionData != null) {
    const session = JSON.parse(sessionData);
    apiKey = session.token;
  }

  const queryParameters = new URLSearchParams(window.location.search);
  const modulId = queryParameters.get("topikModulId");
  const idModul = queryParameters.get("idModul");

  const [sourceCode, setSourceCode] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const codeContainerRef = useRef<HTMLDivElement>(null);
  const highlightRef = useRef<HTMLDivElement>(null);

  const fetchDataModule = async () => {
    try {
      if (idModul) {
        fetchSourceCodeText(idModul);
      } else if (modulId) {
        const endpoint = `${apiUrl}/modul/detailByIdTopikModul/${modulId}`;
        const response = await fetch(endpoint, {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
            'Authorization': `Bearer ${apiKey}`
          }
        });

        if (!response.ok) {
          if (response.status === 403) {
            navigate('/error');
          } else {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
        }

        const data = await response.json();
        if (data.data) {
          fetchSourceCodeText(data.data.data_modul.ms_id_modul);
        }
      }
    } catch (error) {
      console.error('Error fetching data:', error);
      setError((error as Error).message);
    }
  };

  const fetchSourceCodeText = async (modulId: string) => {
    try {
      const response = await fetch(`${apiUrl}/modul/getSourceCodeText/${modulId}`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Authorization': `Bearer ${apiKey}`
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setSourceCode(data.data || '');
    } catch (error) {
      console.error('Error fetching source code:', error);
      setError((error as Error).message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (modulId || idModul) {
      fetchDataModule();
    } else {
      setLoading(false);
    }
  }, [apiUrl, apiKey, modulId, idModul]);

  // Auto-scroll to highlighted line
  useEffect(() => {
    if (highlightedLines && highlightRef.current && codeContainerRef.current) {
      const container = codeContainerRef.current;
      const target = highlightRef.current;

      const containerRect = container.getBoundingClientRect();
      const targetRect = target.getBoundingClientRect();
      const relativeTop = targetRect.top - containerRect.top + container.scrollTop;

      container.scrollTo({
        top: relativeTop - container.clientHeight / 3,
        behavior: 'smooth',
      });
    }
  }, [highlightedLines]);

  // Copy to clipboard
  const handleCopy = useCallback(() => {
    if (sourceCode) {
      navigator.clipboard.writeText(sourceCode).then(() => {
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      });
    }
  }, [sourceCode]);

  // Split source code into lines for rendering
  const codeLines = useMemo(() => sourceCode ? sourceCode.split('\n') : [], [sourceCode]);

  // Memoize the line gutter width based on total lines
  const gutterWidth = useMemo(() => {
    const digits = Math.max(2, String(codeLines.length).length);
    return digits * 10 + 20;
  }, [codeLines.length]);

  if (error) {
    return (
      <Card className="w-full h-full">
        <CardHeader>
          <CardTitle className="text-base font-bold">Kode Program</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-red-600">Error: {error}</div>
        </CardContent>
      </Card>
    );
  }

  if (loading) {
    return (
      <Card className="w-full h-full">
        <CardHeader>
          <CardTitle className="text-base font-bold">Kode Program</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-3/4" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full h-full flex flex-col">
      <CardHeader className="pb-0">
        <CardTitle className="text-base font-bold">Kode Program</CardTitle>
      </CardHeader>
      <CardContent className="flex-1 overflow-hidden p-0">
        <div className="text-sm p-4">
          <div
            style={{
              position: 'relative',
              borderRadius: '8px',
              boxShadow: '0 4px 24px rgba(0,0,0,0.3)',
              overflow: 'hidden',
              border: '1px solid #44475a',
            }}
          >
            {/* Header bar (like VS Code title bar) */}
            <div
              style={{
                background: '#21222c',
                padding: '6px 12px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                borderBottom: '1px solid #44475a',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <div style={{ width: 12, height: 12, borderRadius: '50%', background: '#ff5555', opacity: 0.8 }} />
                <div style={{ width: 12, height: 12, borderRadius: '50%', background: '#f1fa8c', opacity: 0.8 }} />
                <div style={{ width: 12, height: 12, borderRadius: '50%', background: '#50fa7b', opacity: 0.8 }} />
                <span style={{ color: '#6272a4', fontSize: 11, marginLeft: 8, fontFamily: 'system-ui' }}>
                  source.java
                </span>
              </div>

              {/* Copy Button */}
              <button
                onClick={handleCopy}
                style={{
                  background: copied ? 'rgba(80, 250, 123, 0.2)' : 'transparent',
                  border: '1px solid ' + (copied ? 'rgba(80, 250, 123, 0.4)' : 'rgba(255,255,255,0.1)'),
                  borderRadius: 6,
                  padding: '3px 10px',
                  fontSize: 11,
                  color: copied ? '#50fa7b' : '#6272a4',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 4,
                }}
                onMouseEnter={(e) => {
                  if (!copied) {
                    e.currentTarget.style.borderColor = 'rgba(255,255,255,0.25)';
                    e.currentTarget.style.color = '#f8f8f2';
                  }
                }}
                onMouseLeave={(e) => {
                  if (!copied) {
                    e.currentTarget.style.borderColor = 'rgba(255,255,255,0.1)';
                    e.currentTarget.style.color = '#6272a4';
                  }
                }}
                title="Copy code"
              >
                {copied ? (
                  <>
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
                    Copied!
                  </>
                ) : (
                  <>
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                    Copy
                  </>
                )}
              </button>
            </div>

            {/* Code Container */}
            <div
              ref={codeContainerRef}
              style={{
                height: '450px',
                overflowY: 'auto',
                background: '#282a36',
                fontFamily: "'Cascadia Code', 'Fira Code', 'JetBrains Mono', 'Consolas', monospace",
                fontSize: '12.5px',
                lineHeight: '1.7',
                padding: '8px 0',
              }}
            >
              {codeLines.length > 0 ? codeLines.map((line, index) => {
                const lineNumber = index + 1;
                const isHighlighted = highlightedLines
                  && lineNumber >= highlightedLines.start
                  && lineNumber <= highlightedLines.end;

                return (
                  <div
                    key={lineNumber}
                    ref={isHighlighted && lineNumber === highlightedLines!.start ? highlightRef : undefined}
                    style={{
                      display: 'flex',
                      alignItems: 'stretch',
                      minHeight: '1.7em',
                      background: isHighlighted
                        ? 'rgba(59, 130, 246, 0.18)'
                        : 'transparent',
                      borderLeft: isHighlighted
                        ? '3px solid #3b82f6'
                        : '3px solid transparent',
                      transition: 'background 0.3s ease, border-left 0.3s ease',
                      position: 'relative',
                    }}
                  >
                    {/* Glow effect for highlighted lines */}
                    {isHighlighted && (
                      <div
                        style={{
                          position: 'absolute',
                          inset: 0,
                          background: 'linear-gradient(90deg, rgba(59,130,246,0.12) 0%, rgba(59,130,246,0.04) 50%, transparent 100%)',
                          pointerEvents: 'none',
                        }}
                      />
                    )}

                    {/* Line Number */}
                    <span
                      style={{
                        display: 'inline-block',
                        width: gutterWidth,
                        minWidth: gutterWidth,
                        textAlign: 'right',
                        paddingRight: '16px',
                        color: isHighlighted ? '#93c5fd' : '#6272a4',
                        userSelect: 'none',
                        fontWeight: isHighlighted ? 600 : 400,
                        transition: 'color 0.3s ease',
                        flexShrink: 0,
                        position: 'relative',
                        zIndex: 1,
                        borderRight: '1px solid rgba(98, 114, 164, 0.2)',
                        marginRight: '12px',
                      }}
                    >
                      {lineNumber}
                    </span>

                    {/* Code Content — syntax highlighted */}
                    <span
                      style={{
                        color: '#f8f8f2',
                        whiteSpace: 'pre',
                        paddingRight: '16px',
                        position: 'relative',
                        zIndex: 1,
                      }}
                    >
                      {highlightJavaLine(line || ' ')}
                    </span>
                  </div>
                );
              }) : (
                <div style={{ padding: '12px 16px', color: '#6272a4' }}>
                  Loading source code...
                </div>
              )}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default CodeProgramCard;