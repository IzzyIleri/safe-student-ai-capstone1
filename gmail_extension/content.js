let lastEmailText = "";
let isScanning = false;

function createPanel() {
  if (document.getElementById("safe-student-panel")) return;

  const panel = document.createElement("div");
  panel.id = "safe-student-panel";
  panel.innerHTML = `
    <h3>SafeStudent AI</h3>
    <div id="risk-level">Waiting...</div>
    <div id="risk-score">Open an email in Gmail.</div>
    <div id="risk-flags"></div>
  `;
  document.body.appendChild(panel);
}

function setStatus(levelText, scoreText = "", flagsText = "") {
  createPanel();
  document.getElementById("risk-level").textContent = levelText;
  document.getElementById("risk-score").innerHTML = scoreText;
  document.getElementById("risk-flags").textContent = flagsText;
}

function updatePanel(level, score, flags) {
  const scoreText = `Score: <b>${score}/100</b>`;
  const flagsText = flags && flags.length
    ? `Flags: ${flags.join(" | ")}`
    : "Flags: None detected.";

  setStatus(`${level} RISK`, scoreText, flagsText);
}

function getEmailText() {
  const nodes = document.querySelectorAll(".a3s");
  let text = "";

  nodes.forEach((node) => {
    const current = (node.innerText || "").trim();
    if (current.length > text.length) {
      text = current;
    }
  });

  return text.trim();
}

function analyzeEmail() {
  if (isScanning) return;

  const emailText = getEmailText();
  if (!emailText || emailText.length < 20) return;
  if (emailText === lastEmailText) return;

  isScanning = true;
  lastEmailText = emailText;

  setStatus("SCANNING...", "Reading current Gmail message...", "");

  chrome.runtime.sendMessage(
    {
      type: "ANALYZE_EMAIL",
      message: emailText
    },
    (response) => {
      if (chrome.runtime.lastError) {
        setStatus(
          "ERROR",
          "Extension messaging failed.",
          chrome.runtime.lastError.message || "Unknown runtime error."
        );
        isScanning = false;
        return;
      }

      if (!response || !response.ok) {
        setStatus(
          "ERROR",
          "Could not connect to backend.",
          response?.error || "Check Flask and service worker."
        );
        isScanning = false;
        return;
      }

      const data = response.data || {};
      updatePanel(data.level || "LOW", data.score || 0, data.flags || []);
      isScanning = false;
    }
  );
}

function startWatching() {
  createPanel();

  const observer = new MutationObserver(() => {
    analyzeEmail();
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true
  });

  setInterval(analyzeEmail, 2500);
}

window.addEventListener("load", () => {
  setTimeout(startWatching, 3000);
});