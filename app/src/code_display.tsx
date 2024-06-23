import React, { useState, useEffect } from "react";
import { diffChars } from "diff";
import styled from "styled-components";

interface CodeDisplayProps {
  code: string;
  width?: string;
}

const CodeContainer = styled.pre<{ width?: string }>`
  width: ${(props) => props.width || "100%"};
  white-space: wrap;
  word-wrap: break-word;
  padding: 1rem;
  border-radius: 4px;
  font-size: 12px;
  backgroundColor: "#fff",
  fontFamily: "'Courier New', monospace",
  fontSize: "12px",
  whiteSpace: "wrap",
  backgroundColor: "#f4f4f4",
`;

const CodeDisplay: React.FC<CodeDisplayProps> = ({ code, width }) => {
  const [previousCode, setPreviousCode] = useState<string>("");
  const [highlightedCode, setHighlightedCode] = useState<React.ReactNode[]>([]);

  useEffect(() => {
    if (previousCode === "") {
      setPreviousCode(code);
      setHighlightedCode([<span key={0}>{code}</span>]);
      return;
    }
    if (previousCode !== code) {
      const differences = diffChars(previousCode, code);

      const newHighlightedCode = differences.map((part, index) => {
        if (part.added) {
          return (
            <span
              key={index}
              style={{ backgroundColor: "rgba(0, 255, 0, 0.4)" }}
            >
              {part.value}
            </span>
          );
        } else if (part.removed) {
          return null;
        } else {
          return <span key={index}>{part.value}</span>;
        }
      });

      setHighlightedCode(newHighlightedCode);
      setPreviousCode(code);
    }
  }, [code, previousCode]);

  return (
    <CodeContainer width={width}>
      <code>{highlightedCode}</code>
    </CodeContainer>
  );
};

export default CodeDisplay;
