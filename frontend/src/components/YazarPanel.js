import React, { useState } from 'react';
import ArticleUpload from './ArticleUpload';
import ArticleStatus from './ArticleStatus';
import ArticleRevise from './ArticleRevise';
import YazarMessages from './YazarMessages';
import './YazarPanel.css'; // Import the dedicated CSS

function YazarPanel() {
  const [activeTab, setActiveTab] = useState('upload');

  return (
    <div className="yazar-panel">
      <h2>Yazar Paneli</h2>
      <div className="tab-buttons">
        <button
          className={`tab-button ${activeTab === 'upload' ? 'active' : ''}`}
          onClick={() => setActiveTab('upload')}
        >
          Makale Yükle
        </button>
        <button
          className={`tab-button ${activeTab === 'status' ? 'active' : ''}`}
          onClick={() => setActiveTab('status')}
        >
          Makale Durumu
        </button>
        <button
          className={`tab-button ${activeTab === 'revise' ? 'active' : ''}`}
          onClick={() => setActiveTab('revise')}
        >
          Makale Revize
        </button>
        <button
          className={`tab-button ${activeTab === 'messages' ? 'active' : ''}`}
          onClick={() => setActiveTab('messages')}
        >
          Mesajlar
        </button>
      </div>
      <div className="tab-content">
        {activeTab === 'upload' && <ArticleUpload />}
        {activeTab === 'status' && <ArticleStatus />}
        {activeTab === 'revise' && <ArticleRevise />}
        {activeTab === 'messages' && <YazarMessages />}
      </div>
    </div>
  );
}

export default YazarPanel;
