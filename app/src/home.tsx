import React, { useEffect, useState } from "react";
import { io } from "socket.io-client";

type Props = {
  targetImage: File | null;
  setTargetImage: React.Dispatch<React.SetStateAction<File | null>>;
};

export function Home({ targetImage, setTargetImage }: Props) {
  const [receivedImageUrl, setReceivedImageUrl] = useState<string>('');
  const [program, setProgram] = useState<string>("");

  const fileToBase64 = (file: File): Promise<string> =>
    new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result as string);
      reader.onerror = (error) => reject(error);
    });

    const base64ToBlob = (base64: string): Blob | null => {
      try {
        const parts = base64.split(';base64,');
        if (parts.length !== 2) {
          console.error('Invalid Base64 string');
          return null;
        }
        const base64Data = parts[1];
        const byteCharacters = atob(base64Data);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
          byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
        return new Blob([byteArray], { type: 'image/jpeg' });
      } catch (error) {
        console.error('Error decoding Base64 string:', error);
        return null;
      }
    };

  useEffect(() => {
    if (!targetImage) return;

    fileToBase64(targetImage).then((base64Image) => {
      const socket = io("http://127.0.0.1:5000", {
        withCredentials: false,
      });

      socket.on("connect", () => {
        socket.emit("upload-image", { image: base64Image });
      });

      socket.on("new-step", (data: { image: string; expression: string }) => {
        const blob = base64ToBlob(data.image);
        const url = blob ? URL.createObjectURL(blob) : '';
        setReceivedImageUrl(url);
        setProgram(data.expression);
      });

      return () => {
        socket.off("new-step");
        socket.off("connect");
        socket.close();
      };
    }).catch((error) => console.error("Error converting file to Base64:", error));
  }, [targetImage]);

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
        {targetImage && (
          <img
            src={URL.createObjectURL(targetImage)}
            alt="Uploaded Target"
            style={{ width: "100%" }}
          />
        )}
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
        style={{
          width: "33.33%",
          height: "100%",
          border: "2px solid blue",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        {receivedImageUrl && (
          <img src={receivedImageUrl} alt="Generated" style={{ width: "100%" }} />
        )}
      </div>
    </div>
  );
}