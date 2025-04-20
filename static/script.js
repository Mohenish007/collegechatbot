document.addEventListener("DOMContentLoaded", () => {
  console.log("✅ JS Loaded");

  // 🎨 THEME TOGGLE
  const root = document.documentElement;
  const themeToggle = document.getElementById("theme-icon");

  const savedTheme = localStorage.getItem("chatTheme") || "dark";
  root.setAttribute("data-theme", savedTheme);
  updateThemeIcon(savedTheme);

  if (themeToggle) {
    themeToggle.addEventListener("click", () => {
      const current = root.getAttribute("data-theme") || "dark";
      const next = current === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      localStorage.setItem("chatTheme", next);
      updateThemeIcon(next);
      console.log(`🌗 Theme switched to: ${next}`);
    });
  }

  function updateThemeIcon(theme) {
    if (!themeToggle) return;
    themeToggle.className = theme === "dark"
      ? "fas fa-sun theme-toggle-btn"
      : "fas fa-moon theme-toggle-btn";
  }

  // 💬 CHATBOT SETUP
  const chatBox = document.getElementById("chat-box");
  const userInput = document.getElementById("user-input");
  const form = document.getElementById("chat-form");
  const emojiPicker = document.getElementById("emoji-picker");
  const emojiBtn = document.getElementById("emoji-btn");
  const micBtn = document.getElementById("mic-btn");

  if (!chatBox || !form || !userInput) {
    console.error("❌ Chat elements not found!");
    return;
  }

  // 📝 Chat history
  let chatHistory = JSON.parse(localStorage.getItem("chatHistory")) || [];
  chatHistory.forEach(msg => appendMessage(msg.sender, msg.message));

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const message = userInput.value.trim();
    if (!message) return;

    appendMessage("user", message);
    saveMessage("user", message);
    userInput.value = "";

    const typing = document.createElement("div");
    typing.className = "bot-message typing-indicator";
    typing.innerHTML = `<div class="message"><span class="dot"></span><span class="dot"></span><span class="dot"></span></div>`;
    chatBox.appendChild(typing);
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
      const response = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message })
      });

      const data = await response.json();
      typing.remove();
      appendMessage("bot", data.response || "No reply received.");
      saveMessage("bot", data.response);
      //speakText(data.response);//
    } catch (error) {
      typing.remove();
      console.error("Fetch error:", error);
      appendMessage("bot", "⚠️ Error reaching the server.");
    }
  });

  function appendMessage(sender, message) {
    const msgWrapper = document.createElement("div");
    msgWrapper.className = `${sender}-message`;

    const msg = document.createElement("div");
    msg.className = "message";
    msg.textContent = message;

    msgWrapper.appendChild(msg);
    chatBox.appendChild(msgWrapper);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  function saveMessage(sender, message) {
    chatHistory.push({ sender, message });
    localStorage.setItem("chatHistory", JSON.stringify(chatHistory));
  }

  // 🔊 VOICE
  if (micBtn) {
    micBtn.addEventListener("click", startVoiceRecognition);
  }

  function startVoiceRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert("Speech recognition is not supported in this browser.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.start();
    micBtn.classList.add("mic-listening");

    void micBtn.offsetWidth;
    micBtn.classList.remove("mic-listening");
    micBtn.classList.add("mic-listening");

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript.trim();
      userInput.value = transcript;
      form.dispatchEvent(new Event("submit"));
    };

    recognition.onerror = () => micBtn.classList.remove("mic-listening");
    recognition.onend = () => micBtn.classList.remove("mic-listening");
  }

  function speakText(text) {
    if ('speechSynthesis' in window) {
      const speech = new SpeechSynthesisUtterance(text);
      speech.lang = "en-US";
      window.speechSynthesis.speak(speech);
    }
  }

  // 😄 EMOJI PICKER
  const emojiData = {
    faces: ["😀", "😁", "😂", "😍", "😎", "😢", "😭", "😡", "🤔", "😇", "🥳", "😴"],
    gestures: ["👋", "👍", "👏", "🤝", "🙏", "🙌", "💪", "🖖", "✌️"],
    objects: ["🎓", "💻", "📱", "📚", "🏫", "🧠", "💡", "🎯", "✏️"]
  };

  const emojiMap = {
    ":smile:": "😀", ":laughing:": "😂", ":heart_eyes:": "😍", ":sunglasses:": "😎",
    ":cry:": "😭", ":angry:": "😡", ":brain:": "🧠", ":graduation_cap:": "🎓",
    ":book:": "📚", ":lightbulb:": "💡", ":muscle:": "💪", ":pray:": "🙏"
  };

  function renderEmojis() {
    for (let category in emojiData) {
      const grid = document.querySelector(`.emoji-grid.${category}`);
      emojiData[category].forEach(e => {
        const span = document.createElement("span");
        span.textContent = e;
        grid?.appendChild(span);
      });
    }
  }

  renderEmojis();

  document.querySelectorAll(".emoji-grid").forEach(grid => {
    grid.addEventListener("click", e => {
      if (e.target.textContent) {
        userInput.value += e.target.textContent;
        userInput.focus();
        emojiPicker?.classList.add("hidden");
      }
    });
  });

  document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      const cat = btn.getAttribute("data-category");
      document.querySelectorAll(".emoji-grid").forEach(grid => grid.classList.add("hidden"));
      document.querySelector(`.emoji-grid.${cat}`)?.classList.remove("hidden");
    });
  });

  document.getElementById("emoji-search")?.addEventListener("input", e => {
    const val = e.target.value.toLowerCase();
    document.querySelectorAll(".emoji-grid").forEach(grid => {
      [...grid.children].forEach(emoji => {
        emoji.style.display = emoji.textContent.includes(val) ? "inline-block" : "none";
      });
    });
  });

  emojiBtn?.addEventListener("click", () => {
    emojiPicker?.classList.toggle("hidden");
    document.getElementById("emoji-search").value = "";
  });

  userInput?.addEventListener("input", () => {
    const words = userInput.value.split(" ");
    const last = words[words.length - 1];
    if (last.startsWith(":") && last.endsWith(":")) {
      const match = emojiMap[last];
      if (match) {
        words[words.length - 1] = match;
        userInput.value = words.join(" ");
      }
    }
  });
});

