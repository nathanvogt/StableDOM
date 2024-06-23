import { useState } from "react";
import "./App.css";
import { Home } from "./home";

function App() {
  const [targetImageFile, setTargetImageFile] = useState<File | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files ? event.target.files[0] : null;
    setTargetImageFile(file);
  };

  const upload = (
    <>
      <h1>Upload an Image</h1>
      <input
        type="file"
        onChange={handleFileChange}
        accept="image/png, image/jpeg, image/gif"
      />
      {targetImageFile && <p>File name: {targetImageFile.name}</p>}
    </>
  );

  return (
    <div className="App">
      {targetImageFile ? <Home targetImage={targetImageFile} /> : upload}
    </div>
  );
}

export default App;
