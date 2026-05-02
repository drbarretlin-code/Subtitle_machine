import React, { useState, useEffect, useRef } from 'react';
import './App.css';

function App() {
  const [isRecording, setIsRecording] = useState(false);
  const [subtitles, setSubtitles] = useState([]);
  const [status, setStatus] = useState('等待連線');
  const [inputLang, setInputLang] = useState('auto');
  const [targetLang, setTargetLang] = useState('繁體中文');
  const socketRef = useRef(null);
  const audioContextRef = useRef(null);
  const processorRef = useRef(null);
  const streamRef = useRef(null);
  const scrollRef = useRef(null);

  useEffect(() => {
    const socket = new WebSocket('ws://localhost:8000/ws/audio');
    socket.binaryType = 'arraybuffer';
    
    socket.onopen = () => {
      setStatus('已連接伺服器');
      socket.send(JSON.stringify({ 
        type: 'config', 
        inputLang, 
        targetLang 
      }));
    };
    
    socket.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        setSubtitles(prev => {
          const index = prev.findIndex(s => s.id === data.id);
          if (index !== -1) {
            const newSubtitles = [...prev];
            newSubtitles[index] = data;
            return newSubtitles;
          } else {
            return [...prev, data];
          }
        });
      } catch (err) {
        console.error("解析伺服器訊息失敗:", err);
      }
    };
    
    socket.onclose = () => setStatus('連線中斷');
    socket.onerror = () => setStatus('連線錯誤');
    socketRef.current = socket;

    return () => socket.close();
  }, []);

  useEffect(() => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({ 
        type: 'config', 
        inputLang, 
        targetLang 
      }));
    }
  }, [inputLang, targetLang]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollLeft = scrollRef.current.scrollWidth;
    }
  }, [subtitles]);

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
          socketRef.current.send(inputData.buffer);
        }
      };
      
      source.connect(processor);
      processor.connect(audioContext.destination);
      processorRef.current = processor;
      
      setIsRecording(true);
      setStatus('正在監聽中');
    } catch (err) {
      console.error('無法啟動錄音:', err);
      setStatus('權限遭拒');
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
    setStatus('已停止');
  };

  return (
    <div className="container">
      <header className="header">
        <div className="controls">
          <select value={inputLang} onChange={(e) => setInputLang(e.target.value)}>
            <option value="auto">🎤 自動辨識</option>
            <option value="zh">繁體中文</option>
            <option value="en">English</option>
            <option value="ja">日本語</option>
            <option value="ko">한국어</option>
          </select>
          <span style={{color: 'rgba(255,255,255,0.3)', fontSize: '12px'}}>➔</span>
          <select value={targetLang} onChange={(e) => setTargetLang(e.target.value)}>
            <option value="繁體中文">繁體中文</option>
            <option value="英文">英文</option>
            <option value="日文">日文</option>
            <option value="韓文">韓文</option>
          </select>
        </div>
        <div className="status-badge">
          <div className={`status-dot ${isRecording ? 'active' : ''}`}></div>
          {status}
        </div>
      </header>

      <main className="subtitle-viewport" ref={scrollRef}>
        <div className="subtitle-list-horizontal">
          {subtitles.length === 0 && (
            <div className="empty-state">READY TO CAPTURE</div>
          )}
          {subtitles.map((sub, index) => (
            <div key={sub.id || index} className="subtitle-item-inline">
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
          {isRecording ? 'STOP' : 'START SESSION'}
        </button>
      </footer>
    </div>
  );
}

export default App;
