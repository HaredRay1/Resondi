# Rebuilding the App's Model in Edge Impulse

The app does not run a PyTorch or ONNX model. It loads an **Edge Impulse WebAssembly (browser) export** of project "SmartStethoscope" (deploy version 5) from GitHub `HaredRay1/Ausculta`, folder `model/smartstethoscope-wasm-browser-simd-v5-impulse-#1/browser`. Loading that exact export on 9 Nov showed:

| Property | Deployed model |
|---|---|
| Labels, in output order | Asthma, Bronchiolitis, Healthy, Pneumonia |
| Input | 16,000 samples = 1 s at 16 kHz |
| Classification threshold | 0.6 |

A drop-in replacement therefore has to be another Edge Impulse WebAssembly export with the **same 1 s, 16 kHz input**. Only its labels change. The PyTorch model in this package uses the same data, split, signal processing and architecture, so it shows what to expect and checks the Edge Impulse result. It is not what the app runs.

Nobody can do these steps for you: they need the Edge Impulse account. Never give that password to anyone, including an AI assistant.

## 1. Prepare the clips

```powershell
python scripts\prepare_data.py --icbhi "C:\Users\Hared\Downloads\archive.zip"
python scripts\export_edge_impulse.py --icbhi "C:\Users\Hared\Downloads\archive.zip"
```

This writes 6,898 WAV clips (one per labelled breathing cycle) to `export\edge-impulse\training` and `export\edge-impulse\testing`, and `export\edge-impulse\info.labels`, which gives each clip its label, its category and its patient.

## 2. Create a new Edge Impulse project

In Edge Impulse Studio, create a **new** project, for example `Resondi-Lung-4class`. Do not retrain the old project: it is the record of what the paper's results came from.

## 3. Upload with the labels and split kept

Install the CLI once: `npm.cmd install -g edge-impulse-cli` (use `npm.cmd` if PowerShell blocks `npm`).

```powershell
cd export\edge-impulse
edge-impulse-uploader --info-file info.labels
```

Log in to the new project when asked. If your CLI version does not accept `--info-file`, use Studio instead: **Data acquisition → Add data → Upload data**, choose the `edge-impulse` folder including `info.labels`, and Edge Impulse reads the labels and categories from that file.

Then, in **Data acquisition**, check that:
- the four labels are exactly `Crackles`, `Healthy`, `Wheezing`, `Wheezing with Crackles`;
- about 85% of clips are Training and 15% Testing;
- the clips have a `patient` metadata field.

**Never press "Perform train/test split".** It reshuffles clips at random and undoes the patient split.

## 4. Create the impulse (same as the deployed model)

**Impulse design → Create impulse:**

| Setting | Value |
|---|---|
| Window size | 1000 ms |
| Window increase | 500 ms |
| Frequency | 16000 Hz |
| Zero-pad data | On |
| Processing block | Audio (MFCC) |
| Learning block | Classification |

**MFCC** (parameters page): number of coefficients 13, frame length 0.02, frame stride 0.02, filter number 32, FFT length 256, normalisation window size 101, low frequency 0, high frequency blank, pre-emphasis coefficient 0.98. Click **Save parameters**, then **Generate features**.

**Classifier:**
- Number of training cycles 100, learning rate **0.001**, batch size 32.
- Neural network: reshape to 13 columns; 1-D convolution **32** filters, kernel 3; 1-D convolution **64** filters, kernel 3; each followed by pooling and dropout 0.25; flatten; output. This is the wider network, which scored best in the local tests (38% against 32% for Edge Impulse's default 8 and 16 filters). Change the filter numbers in the neural network editor; nothing else in the app changes.
- **Advanced training settings:** validation set size 15%, and **Split train/validation set on metadata key: `patient`**. Without this, Edge Impulse splits validation at random over 1-second windows, which is the original leak.
- Click **Start training**.

## 5. Test on the held-out patients

**Model testing → Classify all.** These are the test patients, never seen in training. Write down accuracy and the confusion matrix. Compare them with `results\test-report.txt` from the PyTorch build: they should be in the same range. A much higher Edge Impulse figure means something leaked; check that the split in step 3 held.

## 6. Deploy

**Deployment → WebAssembly (browser, SIMD)**. Choose the **Quantized (int8)** model, as the current app uses, unless Model testing shows int8 is clearly worse than float32. Build and download the zip, then unzip it.

## 7. Check the export before it goes near the app

```powershell
node scripts\check_deployed_model.js "<unzipped folder>\browser" export\edge-impulse\testing
```

It must print `PASS: labels and input size match the app`. It then classifies every test clip the way the app does and prints the accuracy: it should match step 5.

## 8. Publish and point the app at it

1. Copy the `browser` folder into the GitHub repository as `model/resondi-lung-4class-v1/browser/`. Keep the old folder.
2. Commit and push. Copy the commit's full SHA from GitHub.
3. Make the app changes in `app-changes\model-4-class-labels.md`, using the pinned URL:
   `https://cdn.jsdelivr.net/gh/HaredRay1/Ausculta@<commit SHA>/model/resondi-lung-4class-v1/browser/`

Pinning to a commit means a later push can never silently change the model the app runs.
