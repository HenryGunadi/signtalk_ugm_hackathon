# SignTalk

**SignTalk** is an AI-powered real-time video conferencing application that aims to bridge the communication gap between spoken language and sign language. It provides real-time speech-to-text and sign-language-to-text translation using custom AI models. This is currently an MVP focused on real-time communication infrastructure.

## 🚀 Features

- 🔊 **Speech-to-Text AI Model** *(WIP)*  
  Automatically transcribes spoken audio from video calls into readable text.

- 🧏‍♂️ **Sign Language to Text AI Model** *(WIP)*  
  Detects sign language from video frames and translates it into written text.

- 📹 **Real-Time Video Conferencing**  
  Built with custom WebRTC and WebSocket implementation—no third-party video APIs.

- 🌐 **Full Stack Integration**  
  Developed using a modern web stack for scalability and speed.

---

## 🛠 Tech Stack

### Frontend
- [Next.js](https://nextjs.org/) (React Framework)
- TypeScript

### Backend
- Python (for AI and backend logic)
- Supabase (authentication and database)
- Custom WebRTC & WebSocket implementation

### Machine Learning (Planned Integration)
- 🧠 **AI Speech Model** — For live speech-to-text transcription
- ✋ **AI Sign Language Model** — For video sign language recognition

---

## ⚙️ Implementation Details

- ✅ Custom-built **WebRTC** signaling and **WebSocket** communication with no reliance on third-party APIs.
- 🧪 Currently in **MVP stage**:  
  - WebRTC and WebSocket fully functional  
  - AI integration (speech and sign language models) is not yet implemented  
- 🧱 Modular architecture designed to integrate AI models smoothly in future iterations.

---

## 📌 Roadmap

- [x] Real-time video communication with WebRTC
- [x] Real-time signaling and messaging with WebSocket
- [ ] Integrate AI speech recognition model
- [ ] Integrate AI sign language recognition model
- [ ] Add user interface improvements
- [x] Deploy to production -> https://signtalkugmhackathon-production.up.railway.app

---

## 📂 Project Structure (High-Level)

