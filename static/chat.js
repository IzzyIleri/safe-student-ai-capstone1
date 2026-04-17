(function () {
  const chatLog = document.getElementById("chatLog");
  const chatForm = document.getElementById("chatForm");
  const chatInput = document.getElementById("chatInput");
  const chatHint = document.getElementById("chatHint");

  function esc(s) {
    return (s || "").replace(/[&<>"']/g, (c) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
    }[c]));
  }

  function addMessage(role, label, text, metaClass = "") {
    const wrap = document.createElement("div");
    wrap.className = `msg ${role} ${metaClass}`.trim();

    wrap.innerHTML = `
      <div class="bubble">
        <div class="who">${esc(label)}</div>
        <div class="text">${esc(text)}</div>
      </div>
    `;

    chatLog.appendChild(wrap);
    chatLog.scrollTop = chatLog.scrollHeight;
  }

  function addRiskBanner(level, score) {
    const banner = document.createElement("div");
    banner.className = `riskbanner ${level.toLowerCase()}`;
    banner.innerHTML = `
      <span class="pill ${level.toLowerCase()}">${esc(level)} RISK</span>
      <span class="score">Score: <b>${esc(String(score))}/100</b></span>
    `;
    chatLog.appendChild(banner);
    chatLog.scrollTop = chatLog.scrollHeight;
  }

  chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const text = (chatInput.value || "").trim();
    if (!text) return;

    chatHint.textContent = "";
    addMessage("user", "You", text);
    chatInput.value = "";
    chatInput.focus();

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text })
      });

      const data = await res.json().catch(() => ({}));

      if (!res.ok) {
        addMessage("bot", "Bot", `Server error (${res.status}).`);
        return;
      }

      addRiskBanner(data.level, data.score);
      addMessage("bot", "Bot", data.reply, data.level.toLowerCase());
      addMessage("bot", "Bot", data.flags);

    } catch (err) {
      addMessage("bot", "Bot", "Network error. Is Flask running?");
    }
  });
})();