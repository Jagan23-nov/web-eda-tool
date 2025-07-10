let lastCompiled = false;

async function compile() {
  const design = document.getElementById("design").value;
  const testbench = document.getElementById("testbench").value;

  document.getElementById("output").innerText = "Compiling...";

  try {
    const response = await fetch("/compile", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ design: design, testbench: testbench })
    });

    const result = await response.json();

    if (!response.ok) {
      document.getElementById("output").innerText = result.error || "Compilation failed.";
      lastCompiled = false;
    } else {
      document.getElementById("output").innerText = result.output || "Compiled successfully.";
      lastCompiled = true;
    }
  } catch (err) {
    document.getElementById("output").innerText = "Error connecting to server.";
    lastCompiled = false;
  }
}

async function runSim() {
  if (!lastCompiled) {
    document.getElementById("output").innerText = "Please compile first!";
    return;
  }

  document.getElementById("output").innerText = "Running simulation...";

  try {
    const response = await fetch("/run", { method: "GET" });
    const result = await response.json();

    if (!response.ok) {
      document.getElementById("output").innerText = result.error || "Simulation failed.";
    } else {
      document.getElementById("output").innerText = result.output || "Simulation complete.";
    }
  } catch (err) {
    document.getElementById("output").innerText = "Error connecting to server.";
  }
}

async function viewWave() {
  try {
    const response = await fetch("/waveform");
    const result = await response.json();

    if (!response.ok) {
      document.getElementById("waveformOutput").innerText = result.error || "Failed to fetch waveform.";
    } else {
      document.getElementById("waveformOutput").innerHTML =
        `<a href="${result.vcd_url}" target="_blank">Download/View dump.vcd</a>`;
    }
  } catch (err) {
    document.getElementById("waveformOutput").innerText = "Error connecting to server.";
  }
}
