const API_BASE = "http://127.0.0.1:8000";

const titles = {
  dashboard: ["대시보드", "회의 설명용 임시 UI입니다."],
  signup: ["회원가입", "FastAPI /auth/signup API와 연결됩니다."],
  login: ["로그인", "FastAPI /auth/login API와 연결됩니다."],
  me: ["내 정보", "JWT 토큰을 Authorization 헤더에 담아 /users/me를 호출합니다."],
  analysis: ["문자/메일 분석", "추후 LLM 분석 API와 연결할 화면 예시입니다."],
  lookup: ["신고 이력 조회", "추후 신고 이력 조회 API와 연결할 화면 예시입니다."],
  community: ["커뮤니티", "게시글 작성 테스트 화면입니다."]
};

document.querySelectorAll(".nav-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    const page = btn.dataset.page;

    document.querySelectorAll(".nav-btn").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".page").forEach((p) => p.classList.remove("active"));

    btn.classList.add("active");
    document.getElementById(page).classList.add("active");

    document.getElementById("pageTitle").innerText = titles[page][0];
    document.getElementById("pageDesc").innerText = titles[page][1];
  });
});

async function signup() {
  const result = document.getElementById("signupResult");

  try {
    const res = await fetch(`${API_BASE}/auth/signup`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        email: document.getElementById("signupEmail").value,
        password: document.getElementById("signupPassword").value,
        
      })
    });

    const data = await res.json();
    result.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    result.textContent = "요청 실패: " + err.message;
  }
}

async function login() {
  const result = document.getElementById("loginResult");

  try {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        email: document.getElementById("loginEmail").value,
        password: document.getElementById("loginPassword").value
      })
    });

    const data = await res.json();

    if (data.access_token) {
      localStorage.setItem("access_token", data.access_token);
    }

    result.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    result.textContent = "요청 실패: " + err.message;
  }
}

async function getMe() {
  const result = document.getElementById("meResult");
  const token = localStorage.getItem("access_token");

  if (!token) {
    result.textContent = "저장된 토큰이 없습니다. 먼저 로그인하세요.";
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/users/me`, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`
      }
    });

    const data = await res.json();
    result.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    result.textContent = "요청 실패: " + err.message;
  }
}

function logout() {
  localStorage.removeItem("access_token");
  document.getElementById("meResult").textContent = "토큰을 삭제했습니다.";
}

function mockAnalysis() {
  document.getElementById("analysisResult").classList.remove("hidden");
}

function mockLookup() {
  document.getElementById("lookupResult").textContent = JSON.stringify({
    status: "예시 결과",
    reported: true,
    count: 3,
    message: "해당 정보와 유사한 신고 이력이 있습니다."
  }, null, 2);
}

async function checkServer() {
  try {
    const res = await fetch(`${API_BASE}/`);
    const data = await res.json();
    document.getElementById("serverStatus").innerText = data.message || "API 연결 성공";
  } catch {
    document.getElementById("serverStatus").innerText = "API 연결 실패";
  }
}

checkServer();
async function createCommunityPost() {

  const result = document.getElementById("communityResult");

  try {

    const res = await fetch(`${API_BASE}/community/post`, {
      method: "POST",

      headers: {
        "Content-Type": "application/json"
      },

      body: JSON.stringify({
        title: document.getElementById("postTitle").value,
        content: document.getElementById("postContent").value
      })
    });

    const data = await res.json();

    result.textContent = JSON.stringify(data, null, 2);

  } catch (err) {

    result.textContent = "요청 실패: " + err.message;
  }
}