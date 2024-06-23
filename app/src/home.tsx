import { useEffect, useState } from "react";

type Props = {
  targetImage: File;
};

export function Home({ targetImage }: Props) {
  const program = "(+ (- (Circle 8 8 8) (Circle 5 8 8)) (Quad 8 8 4 4 H))";
  const imageUrl = URL.createObjectURL(targetImage);

  useEffect(() => {
    function listenToServerEvents(): void {
      const source = new EventSource("http://localhost:5000");

      source.onmessage = function (event) {
        console.log("Received data:", event.data);
      };

      source.onerror = function (event) {
        console.error("EventSource failed:", event);
        source.close();
      };

      window.onunload = function () {
        source.close();
      };
    }

    listenToServerEvents();
  }, []);

  useEffect(() => {
    return () => {
      // URL.revokeObjectURL(imageUrl);
    };
  }, [imageUrl]);

  return (
    <div style={{ display: "flex", width: "100%", height: "100vh" }}>
      <div
        style={{
          width: "33.33%",
          border: "2px solid red",
          height: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <img src={imageUrl} alt="Uploaded Target" style={{ width: "100%" }} />
      </div>
      <div
        style={{
          width: "33.33%",
          height: "100%",
          border: "2px solid green",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: "20px",
          overflow: "auto",
          fontFamily: "'Courier New', monospace",
          fontSize: "16px",
          textAlign: "center",
          whiteSpace: "pre-wrap",
          backgroundColor: "#f4f4f4",
          borderRadius: "8px",
        }}
      >
        {program}
      </div>
      <div
        style={{ width: "33.33%", height: "100%", border: "2px solid blue" }}
      ></div>
    </div>
  );
}
