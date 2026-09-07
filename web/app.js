const imageInput = document.querySelector("#imageInput");
const dropzone = document.querySelector("#dropzone");
const preview = document.querySelector("#preview");
const dropText = document.querySelector("#dropText");
const runButton = document.querySelector("#runButton");
const messageCard = document.querySelector("#messageCard");
const messageText = document.querySelector("#messageText");
const faceCard = document.querySelector("#faceCard");
const faceId = document.querySelector("#faceId");
const embeddingLen = document.querySelector("#embeddingLen");
const matchCard = document.querySelector("#matchCard");
const matchError = document.querySelector("#matchError");
const matchContent = document.querySelector("#matchContent");
const matchThumb = document.querySelector("#matchThumb");
const matchedUrl = document.querySelector("#matchedUrl");
const sourceDomain = document.querySelector("#sourceDomain");
const matchTitle = document.querySelector("#matchTitle");
const blockCard = document.querySelector("#blockCard");
const blockData = document.querySelector("#blockData");
const verifyButton = document.querySelector("#verifyButton");
const verifyBadge = document.querySelector("#verifyBadge");
const chainToggle = document.querySelector("#chainToggle");
const chainPanel = document.querySelector("#chainPanel");

let selectedFile = null;
let currentBlockIndex = null;

const stages = {
  face: document.querySelector('[data-step="face"]'),
  search: document.querySelector('[data-step="search"]'),
  chain: document.querySelector('[data-step="chain"]'),
};

function setStage(name, status) {
  const step = stages[name];
  step.classList.remove("active", "done", "error");
  if (status === "running") step.classList.add("active");
  if (status === "done") step.classList.add("done");
  if (status === "error") step.classList.add("error");
  step.querySelector("code").textContent = status === "running" ? "running…" : status;
}

function resetUi() {
  Object.keys(stages).forEach((name) => setStage(name, "pending"));
  [messageCard, faceCard, matchCard, blockCard, verifyBadge].forEach((el) => el.classList.add("hidden"));
  matchError.classList.add("hidden");
  matchContent.classList.add("hidden");
  messageText.classList.remove("message-error");
  currentBlockIndex = null;
}

function showMessage(text, isError = false) {
  messageText.textContent = text;
  messageText.classList.toggle("message-error", isError);
  messageCard.classList.remove("hidden");
}

async function parseResponse(response) {
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = new Error(body.error || `Request failed with ${response.status}`);
    error.status = response.status;
    throw error;
  }
  return body;
}

async function postImage(url) {
  const form = new FormData();
  form.append("image", selectedFile);
  return parseResponse(await fetch(url, { method: "POST", body: form }));
}

function renderFace(face) {
  faceId.textContent = face.face_id;
  embeddingLen.textContent = face.embedding_len;
  faceCard.classList.remove("hidden");
}

function renderMatch(result) {
  matchError.classList.add("hidden");
  matchContent.classList.remove("hidden");
  matchThumb.src = result.thumbnail_url || "";
  matchThumb.style.display = result.thumbnail_url ? "block" : "none";
  matchedUrl.href = result.matched_url;
  matchedUrl.textContent = result.matched_url;
  sourceDomain.textContent = result.source_domain;
  matchTitle.textContent = result.title || "Untitled match";
  matchCard.classList.remove("hidden");
}

function renderSearchError(error) {
  matchContent.classList.add("hidden");
  matchError.textContent = error.message || "No usable match returned by SerpApi.";
  matchError.classList.remove("hidden");
  matchCard.classList.remove("hidden");
}

function renderBlock(block) {
  currentBlockIndex = block.index;
  blockData.textContent = [
    `index: ${block.index}`,
    `timestamp: ${block.timestamp}`,
    `data_hash: ${block.data_hash}`,
    `previous_hash: ${block.previous_hash}`,
    `hash: ${block.hash}`,
  ].join("\n");
  blockCard.classList.remove("hidden");
}

function markFailure(stage, error) {
  setStage(stage, "error");
  showMessage(error.status === 422 ? "No face detected in that image." : error.message, true);
}

async function runPipeline() {
  if (!selectedFile) return;
  resetUi();
  runButton.disabled = true;
  runButton.textContent = "Running...";

  try {
    setStage("face", "running");
    const face = await postImage("/api/face/scan");
    renderFace(face);
    setStage("face", "done");

    setStage("search", "running");
    let searchResult;
    try {
      searchResult = await parseResponse(await fetch(`/api/search/${face.face_id}`, { method: "POST" }));
      renderMatch(searchResult);
      setStage("search", "done");
    } catch (error) {
      setStage("search", "error");
      if (error.status === 502) renderSearchError(error);
      showMessage(error.status === 502 ? "Search did not return a usable public match." : error.message, true);
      return;
    }

    setStage("chain", "running");
    const block = await parseResponse(await fetch(`/api/chain/commit/${searchResult.search_id}`, { method: "POST" }));
    renderBlock(block);
    setStage("chain", "done");
    showMessage("Pipeline complete.");
  } catch (error) {
    const stage = stages.face.classList.contains("done") ? "chain" : "face";
    markFailure(stage, error);
  } finally {
    runButton.disabled = false;
    runButton.textContent = "Run Pipeline";
  }
}

function useFile(file) {
  if (!file || !file.type.startsWith("image/")) return;
  selectedFile = file;
  preview.src = URL.createObjectURL(file);
  preview.style.display = "block";
  dropText.style.display = "none";
  runButton.disabled = false;
}

imageInput.addEventListener("change", () => useFile(imageInput.files[0]));
dropzone.addEventListener("dragover", (event) => {
  event.preventDefault();
  dropzone.classList.add("dragging");
});
dropzone.addEventListener("dragleave", () => dropzone.classList.remove("dragging"));
dropzone.addEventListener("drop", (event) => {
  event.preventDefault();
  dropzone.classList.remove("dragging");
  useFile(event.dataTransfer.files[0]);
});
runButton.addEventListener("click", runPipeline);

verifyButton.addEventListener("click", async () => {
  if (currentBlockIndex === null) return;
  verifyBadge.classList.add("hidden");
  const result = await parseResponse(await fetch(`/api/chain/verify/${currentBlockIndex}`));
  verifyBadge.textContent = result.valid ? "✓ VALID" : "✗ MISMATCH";
  verifyBadge.className = `badge ${result.valid ? "valid" : "invalid"}`;
});

chainToggle.addEventListener("click", async () => {
  const opening = chainPanel.classList.contains("hidden");
  chainToggle.setAttribute("aria-expanded", String(opening));
  chainPanel.classList.toggle("hidden", !opening);
  if (!opening) return;

  const result = await parseResponse(await fetch("/api/chain/full"));
  chainPanel.innerHTML = "";
  result.chain.forEach((block) => {
    const row = document.createElement("div");
    row.className = "chain-row";
    row.textContent = `#${block.index} — ${block.hash} — ${result.valid ? "valid" : "invalid"}`;
    chainPanel.appendChild(row);
  });
});
