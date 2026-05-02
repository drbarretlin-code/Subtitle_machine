import React, { useState, useEffect, useRef } from 'react';
import './App.css';

function App() {
  const [isRecording, setIsRecording] = useState(false);
  const [subtitles, setSubtitles] = useState([]);
  const [status, setStatus] = useState('等待連線...');
  const [inputLang, setInputLang] = useState('auto');
  const [targetLang, setTargetLang] = useState('繁體中文');
  const socketRef = useRef(null);
  const audioContextRef = useRef(null);
  const processorRef = useRef(null);
  const streamRef = useRef(null);
  const scrollRef = useRef(null);

  // 自動滾動到底部 (右側)
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollLeft = scrollRef.current.scrollWidth;
    }
  }, [subtitles]);

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
      const processor = audioContext.createScriptProcessor(2048, 1, 1);
      
      processor.onaudioprocess = (e) => {
        const inputData = e.inputBuffer.getChannelData(0);
        if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
          socketRef.current.send(JSON.stringify({ 
            type: 'config', 
            inputLang, 
            targetLang 
          }));
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
        <div className="controls">
          <select value={inputLang} onChange={(e) => setInputLang(e.target.value)}>
            <option value="auto">自動辨識</option>
            <option value="zh">中文</option>
            <option value="en">英文</option>
            <option value="ja">日文</option>
            <option value="ko">韓文</option>
            <option value="th">泰文</option>
          </select>
          <span>→</span>
          <select value={targetLang} onChange={(e) => setTargetLang(e.target.value)}>
            <option value="繁體中文">繁體中文</option>
            <option value="英文">英文</option>
            <option value="日文">日文</option>
          </select>
        </div>
        <div className="status-badge">{status}</div>
      </header>

      <main className="subtitle-viewport" ref={scrollRef}>
        <div className="subtitle-list-horizontal">
          {subtitles.length === 0 && (
            <div className="empty-state">等待說話...</div>
          )}
          {subtitles.map((sub, index) => (
            <div key={index} className="subtitle-item-inline">
              <span className="refined-text">{sub.refined}</span>
            </div>
          ))}
        </div>
      </main>

      <footer className="footer">
        <button 
          className={`record-btn ${isRecording ? 'recording' : ''}`}
          onClick={isRecording ? stopRecording : startRecording}
        >
          {isRecording ? 'STOP' : 'START'}
        </button>
      </footer>
    </div>
  );
}

export default App;
