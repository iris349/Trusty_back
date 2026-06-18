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

    if (page === "community") {
  getPosts();
}
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

    getPosts();

  } catch (err) {

    result.textContent = "요청 실패: " + err.message;
  }
}

async function getPosts() {

  const result = document.getElementById("postsList");

  try {

    const res = await fetch(`${API_BASE}/community/post`);

    const data = await res.json();

    result.innerHTML = "";

    data.forEach(post => {

      result.innerHTML += `
  <div class="post-item">

    <h3 onclick="getPostDetail(${post.id})"
        style="cursor:pointer;color:blue;">

      ${post.title}

    </h3>

    <div id="detail-${post.id}">
    </div>

    <hr>

  </div>
`;
    });

  } catch(err) {

    result.innerHTML = "목록 조회 실패";

  }
}

async function getPostDetail(postId) {

  const detail =
    document.getElementById(`detail-${postId}`);

  if (detail.innerHTML !== "") {

    detail.innerHTML = "";

    return;
  }

  try {

    // 게시글 조회
    const postRes = await fetch(
      `${API_BASE}/community/post/${postId}`
    );

    const postData = await postRes.json();

    // 댓글 조회
    const commentRes = await fetch(
      `${API_BASE}/community/comment/${postId}`
    );

    const comments = await commentRes.json();

    let commentHtml = "";

    comments.forEach(comment => {

      commentHtml += `
        <div style="
          border-top:1px solid #ddd;
          padding:5px;
        ">
          ${comment.content}
        </div>
      `;

    });

    detail.innerHTML = `

      <div style="
        background:#f5f5f5;
        padding:10px;
        border-radius:8px;
        margin-top:10px;
      ">

        <p>${postData.content}</p>

        <small>
          작성자: ${postData.user_id}
        </small>

        <br>

        <small>
          작성일: ${postData.created_at}
        </small>

        <br><br>

        <button
          onclick="deletePost(${postData.id})"
        >
          삭제
        </button>

        <hr>

        <h4>댓글</h4>

        ${commentHtml}

        <textarea
          id="comment-input-${postId}"
          placeholder="댓글 입력"
        ></textarea>

        <br>

        <button
          onclick="createComment(${postId})"
        >
          댓글 작성
        </button>

      </div>

    `;

  } catch(err) {

    detail.innerHTML = "상세 조회 실패";

  }
}

async function deletePost(postId) {

  if (!confirm("정말 삭제하시겠습니까?")) {
    return;
  }

  try {

    const res = await fetch(
      `${API_BASE}/community/post/${postId}`,
      {
        method: "DELETE"
      }
    );

    const data = await res.json();

    alert(data.message);

    getPosts();

  } catch(err) {

    alert("삭제 실패");

  }
}

async function createComment(postId) {

  alert("댓글 버튼 클릭됨");

  const content =
    document.getElementById(
      `comment-input-${postId}`
    ).value;

  console.log(content);

  try {

    const res = await fetch(
      `${API_BASE}/community/comment`,
      {
        method: "POST",

        headers: {
          "Content-Type": "application/json"
        },

        body: JSON.stringify({
          post_id: postId,
          content: content
        })
      }
    );

    console.log(res.status);

    const data = await res.json();

    console.log(data);

    alert("댓글 저장 성공");

  } catch(err) {

    console.error(err);

    alert("댓글 작성 실패");

  }
}