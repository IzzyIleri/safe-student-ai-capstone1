const API_URL = "http://127.0.0.1:5001/api/analyze";

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type !== "ANALYZE_EMAIL") {
    return false;
  }

  const body = new URLSearchParams();
  body.append("message", request.message || "");

  fetch(API_URL, {
    method: "POST",
    body: body
  })
    .then(async (res) => {
      const data = await res.json().catch(() => ({}));

      if (!res.ok) {
        sendResponse({
          ok: false,
          error: `Server returned ${res.status}`,
          data: data
        });
        return;
      }

      sendResponse({
        ok: true,
        data: data
      });
    })
    .catch((err) => {
      sendResponse({
        ok: false,
        error: err.message || "Fetch failed"
      });
    });

  return true;
});