// ===== ارسال فرم درخواست =====
const form = document.getElementById("project-form");
const result = document.getElementById("form-result");
let sending = false;

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  if (sending) return;

  sending = true;
  result.innerText = "در حال ارسال...";
  result.className = "";

  const data = {
    name: document.getElementById("name").value.trim(),
    email: document.getElementById("email").value.trim(),
    title: document.getElementById("title").value.trim(),
    description: document.getElementById("description").value.trim(),
  };

  try {
    const response = await fetch("http://127.0.0.1:8000/requests", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    if (!response.ok) throw new Error("خطا در ارسال درخواست");

    result.innerText = "✅ درخواست با موفقیت ثبت شد";
    result.className = "success";
    form.reset();
  } catch (error) {
    result.innerText = "❌ خطا در ارتباط با سرور";
    result.className = "error";
  } finally {
    sending = false;
  }
});

// ===== نمایش کاربران آنلاین =====
const onlineCountEl = document.getElementById("online-count");
const ws = new WebSocket("ws://127.0.0.1:8000/ws/online");

ws.onopen = () => {
  console.log("✅ اتصال WebSocket برقرار شد");
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  onlineCountEl.textContent = data.online_count;
};

ws.onclose = () => {
  console.log("❌ اتصال WebSocket قطع شد، تلاش برای اتصال مجدد...");
  setTimeout(() => location.reload(), 3000); // ریفرش صفحه برای اتصال مجدد
};

ws.onerror = (err) => {
  console.error("WebSocket error:", err);
};
