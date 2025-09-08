from flask import Flask, request, jsonify, Response
import google.generativeai as genai
import random, difflib

app = Flask(__name__)

# -----------------------------
# Configure Gemini (replace with a valid key!)
# -----------------------------
genai.configure(api_key="AIzaSyDLrht-Clb5hT8eIL_61FOg974kYOR3gws")
model = genai.GenerativeModel("gemini-1.5-flash")

# -----------------------------
# Memory
# -----------------------------
chat_history = []

# -----------------------------
# Correction helper
# -----------------------------
def correct_word(user_input, expected_words):
    words = user_input.split()
    corrected = []
    for w in words:
        match = difflib.get_close_matches(w, expected_words, n=1, cutoff=0.8)
        corrected.append(match[0] if match else w)
    return " ".join(corrected)

expected_words = ["learn", "earn", "java", "python", "money", "future", "wisdom", "code", "review"]

# -----------------------------
# Chat Endpoint
# -----------------------------
@app.route("/chat", methods=["POST"])
def chat():
    global chat_history
    user_message = request.json["message"].strip()
    corrected_input = correct_word(user_message.lower(), expected_words)

    chat_history.append({"role": "user", "text": corrected_input})

    prompt = "\n".join([f"{m['role'].upper()}: {m['text']}" for m in chat_history[-10:]])
    try:
        response = model.generate_content(prompt)
        reply = response.text if response else "⚠️ Cosmic signal lost…"
    except Exception as e:
        reply = f"⚠️ Error: {str(e)}"

    chat_history.append({"role": "bot", "text": reply})
    return jsonify({"reply": reply, "corrected": corrected_input})

# -----------------------------
# Clear Chat Endpoint
# -----------------------------
@app.route("/clear", methods=["POST"])
def clear():
    global chat_history
    chat_history = []
    return jsonify({"status": "cleared"})

# -----------------------------
# Frontend
# -----------------------------
@app.route("/")
def index():
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8" />
        <title>🌌 Cosmic AI ✨</title>
        <style>
            body {font-family:'Segoe UI',sans-serif;background:linear-gradient(160deg,#0a0a2a,#1a1a4a);color:#e0e0ff;margin:0;height:100vh;display:flex;flex-direction:column;align-items:center;}
            h1 {margin:20px;color:#9fa8ff;text-shadow:0 0 10px #4a4aff;}
            #controls {margin:10px;width:90%;max-width:800px;text-align:right;}
            #chat {flex:1;width:90%;max-width:800px;padding:20px;overflow-y:auto;background:rgba(20,20,50,0.6);border-radius:15px;box-shadow:0 0 20px rgba(74,74,255,0.4);}
            .msg {margin:10px 0;max-width:70%;padding:12px 16px;border-radius:18px;line-height:1.4;display:inline-block;word-wrap:break-word;}
            .user {background:#00ff9d;color:#000;float:right;clear:both;border-bottom-right-radius:5px;}
            .bot {background:#2d2d6e;color:#e0e0ff;float:left;clear:both;border-bottom-left-radius:5px;}
            #input-area {width:90%;max-width:800px;display:flex;padding:15px;background:rgba(10,10,40,0.9);border-top:1px solid #444;}
            input {flex:1;padding:12px 15px;border-radius:25px;border:none;outline:none;font-size:16px;background:#1a1a4a;color:#fff;}
            button {margin-left:10px;padding:12px 20px;border:none;border-radius:25px;background:#4a4aff;color:white;cursor:pointer;font-weight:bold;transition:0.2s;}
            button:hover {background:#6a6aff;}
            #typing {margin:5px;color:#aaa;font-style:italic;}
        </style>
    </head>
    <body>
        <h1>🌌 Cosmic AI ✨</h1>
        <div id="controls">
            <button onclick="clearChat()">🗑️ Clear Chat</button>
        </div>
        <div id="chat"></div>
        <div id="typing"></div>
        <div id="input-area">
            <input type="text" id="userInput" placeholder="Ask me anything..." onkeypress="if(event.key==='Enter'){sendMessage();}" />
            <button onclick="sendMessage()">Send</button>
        </div>
        <script>
            async function sendMessage(){
                let input=document.getElementById("userInput");
                let message=input.value.trim();
                if(!message) return;
                let chatBox=document.getElementById("chat");
                let userMsg=document.createElement("div");
                userMsg.className="msg user"; userMsg.innerText=message;
                chatBox.appendChild(userMsg); chatBox.scrollTop=chatBox.scrollHeight; input.value="";
                document.getElementById("typing").innerText="Cosmic AI is thinking... 🌌";
                const response=await fetch("/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message:message})});
                const data=await response.json();
                document.getElementById("typing").innerText="";
                if(data.corrected && data.corrected.toLowerCase()!==message.toLowerCase()){
                    let correction=document.createElement("div");
                    correction.className="msg bot";
                    correction.innerHTML="<i>(Did you mean: "+data.corrected+"?)</i>";
                    chatBox.appendChild(correction);
                }
                let botMsg=document.createElement("div");
                botMsg.className="msg bot";
                let urlMatch=data.reply.match(/(https?:\\/\\/[^\\s]+)/g);
                if(urlMatch){
                    let textWithLinks=data.reply.replace(/(https?:\\/\\/[^\\s]+)/g,function(url){return '<a href="'+url+'" target="_blank" style="color:#ff9;">'+url+'</a>';});
                    botMsg.innerHTML=textWithLinks;
                } else {
                    let text=data.reply; botMsg.innerHTML=""; chatBox.appendChild(botMsg);
                    let i=0; function typeWriter(){if(i<text.length){botMsg.innerHTML+=text.charAt(i);i++;setTimeout(typeWriter,15);chatBox.scrollTop=chatBox.scrollHeight;}}
                    typeWriter(); return;
                }
                chatBox.appendChild(botMsg); chatBox.scrollTop=chatBox.scrollHeight;
            }
            async function clearChat(){await fetch("/clear",{method:"POST"});document.getElementById("chat").innerHTML="";}
        </script>
    </body>
    </html>
    """
    return Response(html,mimetype="text/html")

if __name__=="__main__":
    app.run(debug=True)
