import fs from "node:fs/promises";
import path from "node:path";
import sharp from "sharp";

const logos = [
  "logo_bradesco.jpeg",
  "logo_sulamerica.jpeg",
  "logo_hapvida.jpeg",
  "logo_omint.jpeg",
  "logo_unimed.jpeg",
  "logo_alice.jpeg",
];

function computeAlpha(r, g, b) {
  // Remove pure/near-white background and softly fade border pixels.
  const minChannel = Math.min(r, g, b);

  if (minChannel >= 250) {
    return 0;
  }

  if (minChannel >= 232) {
    const t = (250 - minChannel) / (250 - 232);
    return Math.max(0, Math.min(255, Math.round(t * 255)));
  }

  return 255;
}

async function convertLogo(inputPath) {
  const outputPath = inputPath.replace(/\.jpe?g$/i, ".png");

  const { data, info } = await sharp(inputPath)
    .removeAlpha()
    .raw()
    .toBuffer({ resolveWithObject: true });

  const rgba = Buffer.alloc(info.width * info.height * 4);

  for (let i = 0, j = 0; i < data.length; i += 3, j += 4) {
    const r = data[i];
    const g = data[i + 1];
    const b = data[i + 2];

    rgba[j] = r;
    rgba[j + 1] = g;
    rgba[j + 2] = b;
    rgba[j + 3] = computeAlpha(r, g, b);
  }

  await sharp(rgba, {
    raw: {
      width: info.width,
      height: info.height,
      channels: 4,
    },
  })
    .png({ compressionLevel: 9 })
    .toFile(outputPath);

  const stats = await fs.stat(outputPath);
  return { outputPath, size: stats.size };
}

async function run() {
  const root = process.cwd();

  for (const logo of logos) {
    const inputPath = path.join(root, logo);
    const result = await convertLogo(inputPath);
    console.log(`Generated ${path.basename(result.outputPath)} (${result.size} bytes)`);
  }
}

run().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
