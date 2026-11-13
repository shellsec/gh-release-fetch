const field = name => document.getElementById(`motion-${name}`);
const form = field('form');
const preview = field('preview');
const status = field('status');
let gifUrl;
let poster;
let playing = false;

function updatePrompt() {
  const columns = Number(field('columns').value);
  const rows = Number(field('rows').value);
  field('prompt').value = [
    '使用随附的品牌定稿作为固定参考。若同时提供上一版分镜，只修改指定动作。',
    `主体与必须保留的细节：${field('subject').value.trim()}`,
    `本轮动作：${field('action').value.trim()}`,
    '各帧固定镜头、构图、光线、背景和产品比例。首尾动作能自然衔接。',
    `输出一张静态 PNG 分镜图，恰好 ${columns} 列 × ${rows} 行，共 ${columns * rows} 个等尺寸格。按从左到右、从上到下排列。总宽和总高分别能被列数与行数整除。画面铺满网格，不加边框、间距、帧号或新文字。`,
  ].join('\n\n');
}

function canvas(width, height) {
  const element = document.createElement('canvas');
  element.width = width;
  element.height = height;
  return element;
}

function demoSheet() {
  const sheet = canvas(720, 300);
  const context = sheet.getContext('2d');
  const lift = [0, 4, 8, 12, 8, 4];
  for (const [index, offset] of lift.entries()) {
    context.save();
    context.translate(index % 3 * 240, Math.floor(index / 3) * 150);
    context.fillStyle = '#edf2ff';
    context.fillRect(0, 0, 240, 150);
    context.fillStyle = '#172b4d';
    context.beginPath();
    context.roundRect(101, 47 - offset, 38, 25, 9);
    context.fill();
    context.fillStyle = '#245edb';
    context.beginPath();
    context.roundRect(73, 62, 94, 61, 12);
    context.fill();
    context.fillStyle = '#ffffff';
    for (const x of [109, 122]) {
      for (const y of [81, 94]) context.fillRect(x, y, 9, 9);
    }
    context.restore();
  }
  return sheet;
}

function colorIndex(red, green, blue) {
  return Math.round(red * 7 / 255) * 32 + Math.round(green * 7 / 255) * 4 + Math.round(blue * 3 / 255);
}

function encodeGif(sheet, columns, rows, delay) {
  if (sheet.width % columns || sheet.height % rows) {
    throw new Error('图片尺寸无法均分。请裁掉边缘留白，或修改行列数。');
  }
  const sourceWidth = sheet.width / columns;
  const sourceHeight = sheet.height / rows;
  const scale = Math.min(1, 320 / Math.max(sourceWidth, sourceHeight));
  const width = Math.max(1, Math.round(sourceWidth * scale));
  const height = Math.max(1, Math.round(sourceHeight * scale));
  const frame = canvas(width, height);
  const context = frame.getContext('2d', { willReadFrequently: true });
  const word = value => [value & 255, value >> 8];
  const bytes = [...new TextEncoder().encode('GIF89a'), ...word(width), ...word(height), 0xf7, 0, 0];
  const palette = [];
  for (let index = 0; index < 256; index++) {
    palette.push(Math.round((index >> 5) * 255 / 7), Math.round((index >> 2 & 7) * 255 / 7), (index & 3) * 85);
  }
  for (const [r, g, b] of [[36, 94, 219], [23, 43, 77], [237, 242, 255]]) {
    palette.splice(colorIndex(r, g, b) * 3, 3, r, g, b);
  }
  bytes.push(...palette, 0x21, 0xff, 11, ...new TextEncoder().encode('NETSCAPE2.0'), 3, 1, 0, 0, 0);
  let firstFrame;
  for (let index = 0; index < columns * rows; index++) {
    const x = index % columns * sourceWidth;
    const y = Math.floor(index / columns) * sourceHeight;
    context.fillStyle = '#ffffff';
    context.fillRect(0, 0, width, height);
    context.drawImage(sheet, x, y, sourceWidth, sourceHeight, 0, 0, width, height);
    const { data } = context.getImageData(0, 0, width, height);
    // Reset before the dictionary reaches 512 codes, keeping every code 9 bits wide.
    const packed = [];
    let bits = 0;
    let buffer = 0;
    const write = code => {
      buffer |= code << bits;
      bits += 9;
      while (bits >= 8) {
        packed.push(buffer & 255);
        buffer >>= 8;
        bits -= 8;
      }
    };
    for (let pixel = 0; pixel < data.length; pixel += 4) {
      if (pixel % 1000 === 0) write(256);
      const color = colorIndex(data[pixel], data[pixel + 1], data[pixel + 2]);
      write(color);
      if (index === 0) {
        const offset = color * 3;
        data[pixel] = palette[offset];
        data[pixel + 1] = palette[offset + 1];
        data[pixel + 2] = palette[offset + 2];
      }
    }
    if (index === 0) {
      context.putImageData(new ImageData(data, width, height), 0, 0);
      firstFrame = frame.toDataURL('image/png');
    }
    write(257);
    if (bits) packed.push(buffer & 255);
    bytes.push(0x21, 0xf9, 4, 4, ...word(delay / 10), 0, 0);
    bytes.push(0x2c, 0, 0, 0, 0, ...word(width), ...word(height), 0, 8);
    for (let offset = 0; offset < packed.length; offset += 255) {
      const block = packed.slice(offset, offset + 255);
      bytes.push(block.length, ...block);
    }
    bytes.push(0);
  }
  bytes.push(0x3b);
  return { blob: new Blob([Uint8Array.from(bytes)], { type: 'image/gif' }), firstFrame, width, height };
}

async function exportSheet(useDemo) {
  const controls = field('controls');
  const file = field('file').files[0];
  const columns = Number(field('columns').value);
  const rows = Number(field('rows').value);
  const delay = Number(field('delay').value);
  controls.disabled = true;
  field('result').hidden = true;
  if (gifUrl) URL.revokeObjectURL(gifUrl);
  gifUrl = undefined;
  status.textContent = '正在准备 GIF…';
  let source;
  try {
    if (columns * rows < 2 || columns * rows > 16) throw new Error('请选择 2–16 帧。');
    if (!useDemo && !file) throw new Error('请选择一张分镜图，或先试用样例。');
    if (!useDemo && (!['image/png', 'image/jpeg', 'image/webp'].includes(file.type) || file.size > 12 * 1024 * 1024)) {
      throw new Error('请选择不超过 12 MB 的 PNG、JPEG 或 WebP。');
    }
    source = useDemo ? demoSheet() : await createImageBitmap(file);
    if (source.width * source.height > 16_000_000) throw new Error('图片像素过多，请缩小后重试。');
    const result = encodeGif(source, columns, rows, delay);
    gifUrl = URL.createObjectURL(result.blob);
    poster = result.firstFrame;
    playing = false;
    preview.src = poster;
    field('play').textContent = '播放预览';
    field('download').href = gifUrl;
    field('result').hidden = false;
    status.textContent = `${columns * rows} 帧，${result.width} × ${result.height} 像素，每帧 ${delay} 毫秒。`;
  } catch (error) {
    status.textContent = error instanceof DOMException ? '无法读取这张图片，请确认文件可以正常打开。' : error.message;
  } finally {
    source?.close?.();
    controls.disabled = false;
  }
}

for (const name of ['subject', 'action', 'columns', 'rows']) {
  field(name).addEventListener('input', updatePrompt);
}
field('copy').addEventListener('click', async () => {
  try {
    await navigator.clipboard.writeText(field('prompt').value);
    field('copy-status').textContent = '已复制';
  } catch {
    field('prompt').select();
    field('copy-status').textContent = '已选中提示词，请手动复制。';
  }
});
form.addEventListener('submit', event => {
  event.preventDefault();
  exportSheet(false);
});
field('demo').addEventListener('click', () => {
  field('file').value = '';
  field('columns').value = '3';
  field('rows').value = '2';
  if (!form.reportValidity()) return;
  updatePrompt();
  exportSheet(true);
});
field('play').addEventListener('click', () => {
  playing = !playing;
  preview.src = playing ? gifUrl : poster;
  field('play').textContent = playing ? '停止预览' : '播放预览';
});
updatePrompt();
document.getElementById('brand-motion').hidden = false;
