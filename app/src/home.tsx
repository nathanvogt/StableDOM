import { useEffect } from "react";

type Props = {
  targetImage: File;
};

export function Home({ targetImage }: Props) {
  const imageUrl = URL.createObjectURL(targetImage);

  useEffect(() => {
    return () => {
      // URL.revokeObjectURL(imageUrl);
    };
  }, [imageUrl]);

  return (
    <div style={{ display: "flex", width: "100vw", height: "100vh" }}>
      <div style={{ width: "33.33%", border: "2px solid red", height: "100%" }}>
        <img src={imageUrl} alt="Uploaded Target" style={{ width: "100%" }} />
      </div>
      <div
        style={{ width: "33.33%", height: "100%", border: "2px solid green" }}
      ></div>
      <div
        style={{ width: "33.33%", height: "100%", border: "2px solid blue" }}
      ></div>
    </div>
  );
}
