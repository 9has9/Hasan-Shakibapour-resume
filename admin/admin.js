async function login() {
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();
    const result = document.getElementById("result");

    if (!username || !password) {
        result.innerText = "❌ نام کاربری و رمز عبور الزامی است";
        result.className = "error";
        return;
    }

    result.innerText = "در حال ورود...";
    result.className = "";

    try {
        const response = await fetch("http://127.0.0.1:8000/admin/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
        });

        if (!response.ok) throw new Error("login failed");

        const data = await response.json();

        // ذخیره توکن
        localStorage.setItem("access_token", data.access_token);

        result.innerText = "✅ ورود موفق";
        result.className = "success";

        // انتقال به داشبورد
        setTimeout(() => {
            window.location.href = "dashboard.html";
        }, 800);

    } catch (err) {
        result.innerText = "❌ نام کاربری یا رمز عبور اشتباه است";
        result.className = "error";
    }
}
