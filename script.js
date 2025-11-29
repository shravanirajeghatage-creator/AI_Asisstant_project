document.addEventListener("DOMContentLoaded", () => {
    const userInput = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-btn");
    const micBtn = document.getElementById("mic-btn");
    const chatBox = document.getElementById("chat-box");
    const exportBtn = document.getElementById("exportBtn");
    const statusBar = document.getElementById("network-status");

    
// Function to update network status bar
function updateNetworkStatus() {
    if (navigator.onLine) {
        statusBar.textContent = "🟢 Online Mode — AI Chat Enabled";
        statusBar.classList.remove("offline");
    } else {
        statusBar.textContent = "🔴 Offline Mode — Local Commands Only";
        statusBar.classList.add("offline");
    }
}

// Run on page load
updateNetworkStatus();

// Listen for network changes
window.addEventListener("online", updateNetworkStatus);
window.addEventListener("offline", updateNetworkStatus);

    // ✅ Store chat messages
    const chatHistory = [];

    // Add a message to chatbox
    function addMessage(sender, message) {
        const isStatus = message.includes("🎤") || message.includes("⌛") || message.includes("⚠️") || message.includes("📝") || message.includes("✅");

        const msgDiv = document.createElement("div");

        if (isStatus) {
            msgDiv.classList.add("status");
            msgDiv.textContent = message;
        } else {
            msgDiv.classList.add("message", sender);
            const textDiv = document.createElement("div");
            textDiv.classList.add("text");
            textDiv.textContent = message;
            msgDiv.appendChild(textDiv);

            // ✅ Save to chatHistory
            chatHistory.push({
                sender: sender,
                text: message,
                time: new Date().toLocaleTimeString()
            });
        }

        chatBox.appendChild(msgDiv);
        chatBox.scrollTop = chatBox.scrollHeight;

        if (sender === "bot" && !isStatus) {
            speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(message);
            utterance.lang = "en-US";
            utterance.rate = 1.0;
            speechSynthesis.speak(utterance);
        }
    }

    // Send command to backend
    async function sendCommand(command) {
        addMessage("user", command);
        userInput.value = "";

        try {
            const response = await fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: command })
            });

            const data = await response.json();
            addMessage("bot", data.reply);
        } catch (error) {
            addMessage("bot", "⚠️ Error connecting to server.");
            console.error("Error:", error);
        }
    }

    // Send button click
    sendBtn.addEventListener("click", () => {
        const command = userInput.value.trim();
        if (command) sendCommand(command);
    });

    // Enter key press
    userInput.addEventListener("keypress", (event) => {
        if (event.key === "Enter") {
            const command = userInput.value.trim();
            if (command) sendCommand(command);
        }
    });

    // Microphone button
    micBtn.addEventListener("click", () => {
    if (!navigator.onLine) {
        addMessage("bot", "🌐 Offline Mode: Please type your command manually (voice unavailable).");
        return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        addMessage("bot", "⚠️ Your browser does not support voice recognition.");
        return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.start();
    micBtn.classList.add("listening");

    recognition.onstart = () => {
        addMessage("bot", "🎤 Listening...");
    };

    recognition.onspeechend = () => {
        recognition.stop();
        micBtn.classList.remove("listening");
        // (Removed the “recognizing...” message)
    };

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript.trim();
        sendCommand(transcript);
    };

    recognition.onerror = (event) => {
        micBtn.classList.remove("listening");
        addMessage("bot", "⚠️ Voice recognition error: " + event.error);
    };
});


    // ✅ Export Button (PDF with user-selected location + status messages)
    exportBtn.addEventListener("click", async () => {
        if (chatHistory.length === 0) {
            alert("No chat messages to export!");
            return;
        }

        // 📝 Step 1: Notify user
        addMessage("bot", "📝 Preparing your PDF...");

        // Load jsPDF library dynamically if not loaded
        if (typeof window.jspdf === "undefined") {
            await import("https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js");
        }

        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();

        let y = 10;
        doc.setFontSize(12);
        doc.text("AI Assistant Chat Export", 10, y);
        y += 10;

        chatHistory.forEach(msg => {
            const line = `[${msg.time}] ${msg.sender.toUpperCase()}: ${msg.text}`;
            const split = doc.splitTextToSize(line, 180);
            if (y + split.length * 6 > 280) {
                doc.addPage();
                y = 10;
            }
            doc.text(split, 10, y);
            y += split.length * 6;
        });

        const filename = `chat_export_${new Date().toISOString().slice(0,19).replace(/[:T]/g, "-")}.pdf`;

        try {
            const handle = await window.showSaveFilePicker({
                suggestedName: filename,
                types: [
                    {
                        description: "PDF Files",
                        accept: { "application/pdf": [".pdf"] },
                    },
                ],
            });

            const writable = await handle.createWritable();
            const pdfBytes = doc.output("arraybuffer");
            await writable.write(pdfBytes);
            await writable.close();

            // ✅ Step 2: Confirmation
            addMessage("bot", "✅ Chat exported successfully!");
        } catch (err) {
            if (err.name !== "AbortError") {
                console.error("Error saving file:", err);
                addMessage("bot", "⚠️ Failed to save PDF. Please try again.");
            }
        }
    });
});
