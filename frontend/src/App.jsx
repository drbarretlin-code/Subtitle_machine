import React, { useState, useEffect, useRef } from 'react';
import './App.css';

function App() {
  const [isRecording, setIsRecording] = useState(false);
  const [subtitles, setSubtitles] = useState([]);
  const [status, setStatus] = useState('等待連線...');
  const socketRef = useRef(null);
  const audioContextRef = useRef(null);
  const processorRef = useRef(null);
  const streamRef = useRef(null);

  useEffect(() => {
    // 初始化 WebSocket
    const ws = new WebSocket('ws://localhost:8000/ws/audio');
    ws.onopen = () => setStatus('已連接伺服器');
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setSubtitles((prev) => [...prev, data]);
    };
    ws.onclose = () => setStatus('連線已中斷');
    ws.onerror = () => setStatus('連線發生錯誤');
    socketRef.current = ws;

    return () => {
      ws.close();
    };
  }, []);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      
      const audioContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
      audioContextRef.current = audioContext;
      
      const source = audioContext.createMediaStreamSource(stream);
      const processor = audioContext.createScriptProcessor(4096, 1, 1);
      
      processor.onaudioprocess = (e) => {
        const inputData = e.inputBuffer.getChannelData(0);
        if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
          socketRef.current.send(inputData.buffer);
        }
      };
      
      source.connect(processor);
      processor.connect(audioContext.destination);
      processorRef.current = processor;
      
      setIsRecording(true);
      setStatus('正在監聽中...');
    } catch (err) {
      console.error('無法啟動錄音:', err);
      setStatus('錄音權限遭拒或不支援');
    }
  };

  const stopRecording = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
    }
    if (processorRef.current) {
      processorRef.current.disconnect();
    }
    if (audioContextRef.current) {
      audioContextRef.current.close();
    }
    setIsRecording(false);
    setStatus('已停止監聽');
  };

  return (
    <div className="container">
      <header className="header">
        <h1>AI 多語系即時字幕機</h1>
        <div className="status-badge">{status}</div>
      </header>

      <main className="subtitle-viewport">
        <div className="subtitle-list">
          {subtitles.length === 0 && (
            <div className="empty-state">準備就緒，請按開始進行辨識...</div>
          )}
          {subtitles.map((sub, index) => (
            <div key={index} className="subtitle-item">
              <div className="lang-tag">{sub.language.toUpperCase()}</div>
              <div className="content">
                <p className="raw-text">{sub.raw}</p>
                <p className="refined-text">{sub.refined}</p>
              </div>
            </div>
          ))}
        </div>
      </main>

      <footer className="footer">
        <button 
          className={`record-btn ${isRecording ? 'recording' : ''}`}
          onClick={isRecording ? stopRecording : startRecording}
        >
          {isRecording ? '停止監聽' : '開始監聽'}
        </button>
      </footer>
    </div>
  );
}

export default App;
