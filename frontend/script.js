// === Voice input using Web Speech API ===
function voice(id) {
  try {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = "en-US";
    recognition.start();

    recognition.onresult = e => {
      document.getElementById(id).value = e.results[0][0].transcript;
    };

    recognition.onerror = e => {
      alert("Voice recognition error: " + e.error);
    };
  } catch (err) {
    alert("Your browser does not support voice input.");
  }
}

// ================= EXISTING SEARCH (UNCHANGED) =================
function search() {
  const interest = document.getElementById("interest").value.trim();
  const skills = document.getElementById("skills").value.trim();
  const job = document.getElementById("job").value.trim();

  if (!interest && !skills && !job) {
    document.getElementById("results").innerHTML =
      "<p>Please enter at least Interest, Skills, or Job Title to search.</p>";
    return;
  }

  fetch("http://127.0.0.1:5000/search", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ interest, skills, job })
  })
    .then(r => r.json())
    .then(data => show(data))
    .catch(() => {
      document.getElementById("results").innerHTML =
        "<p>Error fetching results. Make sure backend is running.</p>";
    });
}

// ================= NEW HF + RULE BASED SEARCH =================
function hfSearch() {
  const query = document.getElementById("hfQuery").value.trim();

  if (!query) {
    document.getElementById("results").innerHTML =
      "<p>Please enter skills and/or interests for AI search.</p>";
    return;
  }

  document.getElementById("results").innerHTML =
    "<p>🤖 AI is analyzing skills & interests...</p>";

  fetch("http://127.0.0.1:5000/hf-search", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query })
  })
    .then(r => r.json())
    .then(data => showHF(data))
    .catch(() => {
      document.getElementById("results").innerHTML =
        "<p>Error connecting to AI engine.</p>";
    });
}

// ================= SHOW EXISTING RESULTS =================
function show(data) {
  const resultsDiv = document.getElementById("results");
  resultsDiv.innerHTML = "";

  if (!data || data.length === 0) {
    resultsDiv.innerHTML = "<p>No careers found.</p>";
    return;
  }

  data.forEach(c => {
    resultsDiv.innerHTML += renderCard(c);
  });
}

// ================= SHOW HF RESULTS =================
function showHF(data) {
  const resultsDiv = document.getElementById("results");
  resultsDiv.innerHTML = "<h2>🤖 AI Recommended Careers</h2>";

  if (!data || data.length === 0) {
    resultsDiv.innerHTML += "<p>No AI matches found.</p>";
    return;
  }

  data.forEach(c => {
    resultsDiv.innerHTML += renderCard(c);
  });
}

// ================= CARD TEMPLATE (REUSED) =================
function renderCard(c) {
  return `
    <div class="card">
      <h2>💼 ${c.name}</h2>
      <p>${c.overview || "No overview available."}</p>

      <h3>Advantages</h3>
      <ul>${(c.advantages || []).map(a => `<li>✔️ ${a}</li>`).join("")}</ul>

      <h3>Disadvantages</h3>
      <ul>${(c.disadvantages || []).map(d => `<li>❌ ${d}</li>`).join("")}</ul>

      <h3>Demand</h3>
      <p>${c.demand || "N/A"}</p>

      ${formatSkillsWithIcons(c.required_skills)}

      <button onclick='saveJob(${JSON.stringify(c)})'>💾 Save Job</button>
    </div>
  `;
}

// ================= FORMAT SKILLS =================
function formatSkillsWithIcons(skills) {
  if (!skills) return "";
  let html = "<h3>Required Skills:</h3><ul>";

  if (skills.basic?.length)
    html += `<li>🔹 <b>Basic:</b> ${skills.basic.join(", ")}</li>`;
  if (skills.intermediate?.length)
    html += `<li>🔹 <b>Intermediate:</b> ${skills.intermediate.join(", ")}</li>`;
  if (skills.advanced?.length)
    html += `<li>🔹 <b>Advanced:</b> ${skills.advanced.join(", ")}</li>`;
  if (skills.professional?.length)
    html += `<li>🔹 <b>Professional:</b> ${skills.professional.join(", ")}</li>`;

  html += "</ul>";
  return html;
}

// ================= LOCAL STORAGE =================
function saveJob(job) {
  let savedJobs = JSON.parse(localStorage.getItem("savedJobs") || "[]");
  if (!savedJobs.some(j => j.name === job.name)) {
    savedJobs.push(job);
    localStorage.setItem("savedJobs", JSON.stringify(savedJobs));
    alert(`${job.name} saved!`);
  } else {
    alert("Already saved.");
  }
}

function showSavedJobs() {
  const resultsDiv = document.getElementById("results");
  resultsDiv.innerHTML = "<h2>📝 My Saved Jobs</h2>";

  let savedJobs = JSON.parse(localStorage.getItem("savedJobs") || "[]");
  if (savedJobs.length === 0) {
    resultsDiv.innerHTML += "<p>No saved jobs.</p>";
    return;
  }

  savedJobs.forEach((c, i) => {
    resultsDiv.innerHTML += `
      <div class="card">
        <h2>${c.name}</h2>
        <p>${c.overview}</p>
        <button onclick="deleteJob(${i})">🗑️ Delete</button>
      </div>
    `;
  });
}

function deleteJob(index) {
  let savedJobs = JSON.parse(localStorage.getItem("savedJobs") || "[]");
  const removed = savedJobs.splice(index, 1);
  localStorage.setItem("savedJobs", JSON.stringify(savedJobs));
  alert(`${removed[0].name} removed`);
  showSavedJobs();
}

// ================= SIDEBAR =================
function loadDomains(domains) {
  const sidebar = document.querySelector(".sidebar ul");
  sidebar.innerHTML = "";
  domains.forEach(d => {
    sidebar.innerHTML += `<li onclick="document.getElementById('interest').value='${d}'; search();">${d}</li>`;
  });
}

// ================= RESET =================
function resetField(id) {
  document.getElementById(id).value = "";
  search();
}

// ================= DARK MODE =================
function toggleDarkMode() {
  document.body.classList.toggle("dark-mode");
  localStorage.setItem("darkMode", document.body.classList.contains("dark-mode"));
}

// ================= LOAD =================
const allDomains = [
  "Agriculture & Environmental Careers",
  "Business & Management",
  "Design & Creative Arts",
  "Education & Teaching",
  "Engineering",
  "Finance & Accounting",
  "Government & Public Services",
  "Healthcare & Medical",
  "Information Technology",
  "Media, Communication & Journalism",
  "Science & Research",
  "Skilled Trades & Vocational Careers"
];

window.onload = () => {
  loadDomains(allDomains);
  if (localStorage.getItem("darkMode") === "true") {
    document.body.classList.add("dark-mode");
  }
};