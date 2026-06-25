const API_URL = "http://localhost:8000";

function log(msg) {
  const logBox = document.getElementById("log");
  logBox.textContent += `[${new Date().toLocaleTimeString()}] ${msg}\n`;
  logBox.scrollTop = logBox.scrollHeight;
}

async function load_diagram() {
  const filename = document.getElementById("filename").value;
  const reset = document.getElementById("reset").checked;

  try {
    const res = await fetch(`${API_URL}/diagram/loaddiagram`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({filename, reset})
    });

    if (!res.ok) throw await res.text();
    log(`Diagram loaded: ${filename}`);
  } catch (e) {
    log(`❌ Error loading diagram: ${e} ${filename}`);
  }
}

async function parse() {
  const command = document.getElementById("command").value;
  try {
    log(`Parsing: ${command}`);
    const res = await fetch(`${API_URL}/diagram/parse`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({command})
    });
    if (!res.ok) throw await res.text();
  } catch (e) {
    log(`❌ Error parsing command: ${e} ${command_str}`);
  }
}

async function run() {
  try {
    const res = await fetch(`${API_URL}/diagram/run`, { method: "POST" });
    if (!res.ok) {log(`Result: ${res.text}`); throw await res.text();}
    log("▶️ Diagram execution started.");
  } catch (e) {
    log(`❌ Error at run: ${e}`);
  }
}

async function shutdown() {
  try {
    const res = await fetch(`${API_URL}/diagram/shutdown`, { method: "POST" });
    if (!res.ok) throw await res.text();
    log("⏹ Diagram execution shut down.");
  } catch (e) {
    log(`❌ Error at shutdown : ${e}`);
  }
}
 
async function isRunning() {
  try {
    const res = await fetch(`${API_URL}/diagram/is_running`);
    const data = await res.json();
    const stateDiv = document.getElementById("state");
    log(`Is running: ${data.running}`);
    stateDiv.textContent = data.running;
    stateDiv.className = `state ${data.running}`;
  } catch {
    document.getElementById("state").textContent = "ERROR";
  }
}
 
setInterval(isRunning, 2000);
isRunning(); 