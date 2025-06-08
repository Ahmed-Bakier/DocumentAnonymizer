import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import axios from "axios";
import { FaFilePdf, FaHome, FaDownload } from "react-icons/fa";

function ReviewerPanel() {
  const [reviewers, setReviewers] = useState([]);
  const [selectedReviewer, setSelectedReviewer] = useState("");
  const [articles, setArticles] = useState([]);
  
  const [error, setError] = useState("");

  useEffect(() => {
    axios
      .get("http://127.0.0.1:8000/api/reviewers/")
      .then((response) => setReviewers(response.data))
      .catch(() => setError("Hakem listesi alınırken hata oluştu."));
  }, []);

  useEffect(() => {
    if (selectedReviewer) {
      axios
        .get(`http://127.0.0.1:8000/api/reviewer/articles/?reviewer=${selectedReviewer}`)
        .then((response) => setArticles(response.data))
        .catch(() => setError("Makaleler alınırken hata oluştu."));
    }
  }, [selectedReviewer]);

  
  const handleReviewerChange = (e) => {
    setSelectedReviewer(e.target.value);
    localStorage.setItem("selectedReviewerId", e.target.value);
    setArticles([]);
    setError("");
  };

  return (
    <div className="reviewer-panel">
      <h2>Hakem Paneli</h2>
      {error && <p className="error-message">{error}</p>}

      <div className="reviewer-select">
        <label htmlFor="reviewerDropdown">Hakem Seçin:</label>
        <select id="reviewerDropdown" value={selectedReviewer} onChange={handleReviewerChange}>
          <option value="">-- Hakem Seçiniz --</option>
          {reviewers.map((rev) => (
            <option key={rev.id} value={rev.id}>
              {rev.name} - ({rev.interests})
            </option>
          ))}
        </select>
      </div>

      <div className="articles-list">
        {articles.map((article) => (
          <div key={article.id} className="article-card">
            <div className="article-info">
              <FaFilePdf className="article-icon" />
              <p>Takip Numarası: {article.tracking_number}</p>
            </div>
            <a
              href={`http://127.0.0.1:8000/api/reviewer/download/${article.tracking_number}/`}
              target="_blank"
              rel="noopener noreferrer"
              className="download-button"
            >
              <FaDownload /> İndir
            </a>
            <Link to={`/reviewer/evaluate/${article.id}`} className="evaluate-link">
              Değerlendir
            </Link>
          </div>
        ))}
      </div>
        
      

      <div className="links">
        <Link to="/" className="link">
          <FaHome /> Ana Sayfa’ya Dön
        </Link>
      </div>
    </div>
  );
}

export default ReviewerPanel;
