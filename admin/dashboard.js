const API_BASE = "http://localhost:8000";
const token = localStorage.getItem("access_token");

if (!token) { window.location.href = "login.html"; }

// دریافت درخواست‌ها
async function loadRequests() {
    const res = await fetch(`${API_BASE}/admin/requests`, {
        headers: { "Authorization": `Bearer ${token}` }
    });
    const data = await res.json();
    const table = document.getElementById("requestsTable");
    table.innerHTML = "";

    data.forEach(req => {
        table.innerHTML += `
            <tr>
                <td>${req.id}</td>
                <td>${req.name}</td>
                <td>${req.email}</td>
                <td>${req.description}</td>
                <td>
                    <select onchange="updateStatus(${req.id}, this.value)">
                        <option value="pending" ${req.status === "pending" ? "selected" : ""}>pending</option>
                        <option value="approved" ${req.status === "approved" ? "selected" : ""}>approved</option>
                        <option value="rejected" ${req.status === "rejected" ? "selected" : ""}>rejected</option>
                    </select>
                </td>
                <td>
                    <button class="delete-btn" onclick="deleteRequest(${req.id})">🗑</button>
                </td>
            </tr>
        `;
    });
}

// تغییر وضعیت
async function updateStatus(id, status) {
    const res = await fetch(`${API_BASE}/admin/requests/${id}`, {
        method: "PUT",
        headers: { "Authorization": `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify({ status })
    });

    if (res.ok) loadRequests();
    else alert("خطا در تغییر وضعیت");
}

// حذف
async function deleteRequest(id) {
    if (!confirm("حذف شود؟")) return;
    const res = await fetch(`${API_BASE}/admin/requests/${id}`, {
        method: "DELETE",
        headers: { "Authorization": `Bearer ${token}` }
    });
    if (res.ok) loadRequests();
}

// WebSocket آنلاین‌ها
const ws = new WebSocket("ws://localhost:8000/ws/online");
ws.onmessage = (event) => { document.getElementById("onlineCount").innerText = event.data.online_count; };

// خروج
function logout() {
    localStorage.removeItem("access_token");
    window.location.href = "login.html";
}

loadRequests();
