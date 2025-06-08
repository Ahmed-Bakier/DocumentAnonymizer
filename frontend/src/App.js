import React from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import Homepage from './components/Homepage';
import ArticleUpload from './components/ArticleUpload';
import ArticleStatus from './components/ArticleStatus';
import EditorPanel from './components/EditorPanel';
import ReviewerPanel from './components/ReviewerPanel';
import ReviewerEvaluation from './components/ReviewerEvaluation';
import LogRecords from './components/LogRecords';
import Yazar from './components/YazarPanel';
import EditorMessages from './components/EditorMessages';
import './App.css'; // Import global styles for the app

function App() {
  return (
    <BrowserRouter>
      <div className="app">
        {/* Navigation Bar */}
        <nav className="navbar">
          <Link to="/" className="nav-link">Ana Sayfa</Link>
          <Link to="/upload" className="nav-link">Makale Yükleme</Link>
          <Link to="/status" className="nav-link">Makale Durumu</Link>
          <Link to="/editor" className="nav-link">Editör Paneli</Link>
          <Link to="/reviewer" className="nav-link">Hakem Paneli</Link>
        </nav>

        {/* Main Content */}
        <div className="main-content">
          <Routes>
            <Route path="/" element={<Homepage />} />
            <Route path="/upload" element={<ArticleUpload />} />
            <Route path="/author" element={<Yazar />} />
            <Route path="/status" element={<ArticleStatus />} />
            <Route path="/editor" element={<EditorPanel />} />
            <Route path="/editor/logs" element={<LogRecords />} />
            <Route path="/reviewer" element={<ReviewerPanel />} />
            <Route path="/reviewer/evaluate/:id" element={<ReviewerEvaluation />} />
            <Route path="/editor" element={<EditorPanel />} />
            <Route path="/editor/messages/:trackingNumber" element={<EditorMessages />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;