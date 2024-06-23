import express from "express";

import multer from "multer";
import { v4 as uuidv4 } from "uuid";
import cors from "cors";
import fs from "fs";
import path from "path";
import { exec } from "child_process";
import { promisify } from "util";

const app = express();

app.use(cors());
app.use(express.json());

const storage = multer.memoryStorage();
const upload = multer({ storage: storage });

const PORT = 3000;

app.post("/upload", upload.single("image"), (req, res) => {
  if (!req.file) {
    return res.status(400).send("No image uploaded.");
  }

  const requestId = uuidv4();

  //   fs.writeFile(
  //     `/Users/nathanvogt/tree-diffusion/app/uploads/${requestId}.png`,
  //     req.file.buffer,
  //     (err) => {
  //       if (err) {
  //         console.error(err);
  //         return res.status(500).send("Failed to save image.");
  //       }
  //     }
  //   );

  const pythonScriptPath =
    "/Users/nathanvogt/tree-diffusion/scripts/eval_td.py";
  const args = `${requestId} --checkpoint_name /Users/nathanvogt/tree-diffusion/assets/td_tinysvgoffset.pt --device cpu`;

  const execPromisified = promisify(exec);

  execPromisified(`python3 ${pythonScriptPath} ${args}`)
    .then(({ stdout, stderr }) => {
      console.log(`stdout: ${stdout}`);
      if (stderr) {
        console.error(`stderr: ${stderr}`);
      }
    })
    .catch((error) => {
      console.error(`exec error: ${error}`);
    });

  return res.json({
    message: "Image uploaded successfully.",
    requestId: requestId,
  });
});

app.get("/updates/:requestId", (req, res) => {
  const { requestId } = req.params;
  const updatesDir = `/Users/nathanvogt/tree-diffusion/app/uploads`;

  fs.readdir(updatesDir, (err, files) => {
    if (err) {
      return res.status(500).send("Failed to read updates directory.");
    }
    const updateFiles = files
      .filter((file) => file.startsWith(requestId + "_"))
      .sort((a, b) => {
        const stepA = parseInt(a.split("_")[1].split(".")[0]);
        const stepB = parseInt(b.split("_")[1].split(".")[0]);
        return stepB - stepA;
      });
    if (updateFiles.length > 0) {
      const latestUpdateFile = path.join(updatesDir, updateFiles[0]);
      fs.readFile(latestUpdateFile, "utf8", (err, data) => {
        if (err) {
          return res.status(500).send("Error reading the update file.");
        }
        res.status(200).json(JSON.parse(data));
      });
    } else {
      res.status(404).send("No updates available.");
    }
  });
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
