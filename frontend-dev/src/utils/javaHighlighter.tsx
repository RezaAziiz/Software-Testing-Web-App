import React from "react";

// Java keyword sets for syntax highlighting
export const JAVA_KEYWORDS = new Set([
  "abstract", "assert", "boolean", "break", "byte", "case", "catch", "char",
  "class", "const", "continue", "default", "do", "double", "else", "enum",
  "extends", "final", "finally", "float", "for", "goto", "if", "implements",
  "import", "instanceof", "int", "interface", "long", "native", "new",
  "package", "private", "protected", "public", "return", "short", "static",
  "strictfp", "super", "switch", "synchronized", "this", "throw", "throws",
  "transient", "try", "void", "volatile", "while",
]);

export const JAVA_LITERALS = new Set(["true", "false", "null"]);

/** Lightweight Java syntax highlighter – returns React elements */
export const highlightJavaCode = (code: string): React.ReactNode[] => {
  // Regex: strings, single-line comments, multi-line comments, numbers, words
  const tokenRegex = /("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'|\/\/.*|\/\*[\s\S]*?\*\/|\b\d+(?:\.\d+)?\b|[a-zA-Z_$][a-zA-Z0-9_$]*|[^\s]|\s+)/g;
  const tokens = code.match(tokenRegex) || [code];
  return tokens.map((token, i) => {
    // String literals
    if (/^["']/.test(token)) {
      return <span key={i} style={{ color: "#a5d6a7" }}>{token}</span>;
    }
    // Comments
    if (token.startsWith("//") || token.startsWith("/*")) {
      return <span key={i} style={{ color: "#78909c", fontStyle: "italic" }}>{token}</span>;
    }
    // Numbers
    if (/^\d/.test(token)) {
      return <span key={i} style={{ color: "#f48fb1" }}>{token}</span>;
    }
    // Keywords
    if (JAVA_KEYWORDS.has(token)) {
      return <span key={i} style={{ color: "#90caf9", fontWeight: 600 }}>{token}</span>;
    }
    // Literals (true/false/null)
    if (JAVA_LITERALS.has(token)) {
      return <span key={i} style={{ color: "#ce93d8" }}>{token}</span>;
    }
    return <span key={i}>{token}</span>;
  });
};
