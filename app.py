# 🎤 음성 인식 버튼 (Q 키 또는 클릭으로 실행)
st.markdown("""
<div style='margin-top:-10px; margin-bottom:15px;'>
    <button id="voiceBtn" style="
        background-color:#A8E6CF;
        color:#004D40;
        border:none;
        border-radius:8px;
        padding:6px 14px;
        font-weight:800;
        cursor:pointer;
        font-family:'Noto Sans KR', sans-serif;
    ">🎤 음성으로 입력 (Q)</button>
</div>

<script>
const input = window.parent.document.querySelector('input[aria-label="🎯 주제"]');
const btn = window.parent.document.getElementById('voiceBtn');
let recognizing = false;
let recognition;

function startRecognition() {
  try {
    if (!('webkitSpeechRecognition' in window)) {
      alert("⚠️ 브라우저가 음성 인식을 지원하지 않습니다. Chrome을 사용해주세요.");
      return;
    }
    recognition = new webkitSpeechRecognition();
    recognition.lang = 'ko-KR';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = function() {
      recognizing = true;
      btn.innerText = "🎙️ 듣는 중... (다시 누르면 중지)";
      btn.style.backgroundColor = "#7CE0BE";
    };

    recognition.onresult = function(event) {
      const transcript = event.results[0][0].transcript;
      input.value = transcript;
      input.dispatchEvent(new Event('input', { bubbles: true }));
      recognizing = false;
      btn.innerText = "🎤 음성으로 입력 (Q)";
      btn.style.backgroundColor = "#A8E6CF";
    };

    recognition.onerror = function() {
      recognizing = false;
      btn.innerText = "🎤 음성으로 입력 (Q)";
      btn.style.backgroundColor = "#A8E6CF";
    };

    recognition.onend = function() {
      recognizing = false;
      btn.innerText = "🎤 음성으로 입력 (Q)";
      btn.style.backgroundColor = "#A8E6CF";
    };

    recognition.start();
  } catch (err) {
    alert("음성 인식 오류: " + err.message);
  }
}

// 클릭으로 시작/중지
btn.addEventListener('click', function() {
  if (recognizing) {
    recognition.stop();
    recognizing = false;
    btn.innerText = "🎤 음성으로 입력 (Q)";
    btn.style.backgroundColor = "#A8E6CF";
  } else {
    startRecognition();
  }
});

// 키보드 Q 로 실행
window.addEventListener('keydown', function(event) {
  if (event.key === 'q' || event.key === 'Q') {
    event.preventDefault();
    if (recognizing) {
      recognition.stop();
      recognizing = false;
      btn.innerText = "🎤 음성으로 입력 (Q)";
      btn.style.backgroundColor = "#A8E6CF";
    } else {
      startRecognition();
    }
  }
});
</script>
""", unsafe_allow_html=True)
