import React, { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { FaStar, FaComment, FaArrowLeft, FaHome } from 'react-icons/fa';
import axios from 'axios';

function ReviewerEvaluation() {
  const { id } = useParams(); // makale id
  const navigate = useNavigate();
  const [score, setScore] = useState('');
  const [feedback, setFeedback] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // 🔑 localStorage’dan hakem ID'sini al (ReviewerPanel.js'ye eklediğini varsayarsak)
  const reviewerId = localStorage.getItem('selectedReviewerId');

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!score || !feedback || !reviewerId) {
      setError('Lütfen tüm alanları doldurun (puan, açıklama, hakem).');
      return;
    }

    if (score < 1 || score > 10) {
      setError('Puanlama 1 ile 10 arasında olmalıdır.');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      await axios.post(`http://127.0.0.1:8000/api/reviewer/evaluate/${id}/`, {
        reviewer_feedback: feedback,
        score: score,
        reviewer_id: reviewerId, // ✅ önemli
      });

      alert(`Makale ${id} başarıyla değerlendirildi!`);
      navigate('/reviewer');
    } catch (err) {
      setError('Değerlendirme gönderilirken bir hata oluştu.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="form-container">
      <h2>Hakem Değerlendirme Sayfası</h2>
      <p>Makale ID: {id}</p>
      {error && <p className="error-message">{error}</p>}
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>
            <FaStar /> Puanlama (1-10):
          </label>
          <input
            type="number"
            min="1"
            max="10"
            value={score}
            onChange={(e) => setScore(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label>
            <FaComment /> Açıklama:
          </label>
          <textarea
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            required
          />
        </div>
        <button type="submit" className="submit-button" disabled={isLoading}>
          {isLoading ? 'Gönderiliyor...' : 'Değerlendirme Gönder'}
        </button>
      </form>

      <div className="links">
        <Link to="/reviewer" className="link">
          <FaArrowLeft /> Hakem Paneli’ne Dön
        </Link>
        <Link to="/" className="link">
          <FaHome /> Ana Sayfa’ya Dön
        </Link>
      </div>
    </div>
  );
}

export default ReviewerEvaluation;
