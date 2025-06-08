import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { FaHome } from 'react-icons/fa';
import YazarMessages from './YazarMessages';
import './ArticleStatus.css';

function ArticleStatus() {
  const [trackingNumber, setTrackingNumber] = useState('');
  const [email, setEmail] = useState('');
  const [article, setArticle] = useState(null);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleQuery = async (e) => {
    e.preventDefault();

    if (!trackingNumber || !email) {
      setError('Lütfen tüm alanları doldurun.');
      return;
    }
    if (!validateEmail(email)) {
      setError('Geçerli bir e-posta adresi girin.');
      return;
    }

    setIsLoading(true);
    setError('');
    setArticle(null);

    try {
      const response = await axios.get('http://127.0.0.1:8000/api/status/', {
        params: {
          tracking_number: trackingNumber,
          email: email,
        },
      });
      setArticle(response.data);
    } catch (err) {
      if (err.response) {
        if (err.response.status === 404) {
          setError('Makale bulunamadı. Takip numarası veya e-posta hatalı olabilir.');
        } else {
          setError('Makale durumu sorgulanırken bir hata oluştu. (Kod: ' + err.response.status + ')');
        }
        console.error('Response Data:', err.response.data);
      } else if (err.request) {
        setError('Sunucudan yanıt alınamadı. Ağ bağlantınızı kontrol edin.');
        console.error('No response:', err.request);
      } else {
        setError('Sorgu hazırlanırken bir hata oluştu: ' + err.message);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const validateEmail = (email) => {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
  };

  return (
    <div className="status-page-container">
      {/* SOL SÜTUN */}
      <div className="status-left">
        <h2>Makale Durumu Sorgulama</h2>
        {error && <p className="error-message">{error}</p>}

        {/* Sorgulama Formu */}
        <form onSubmit={handleQuery} className="query-form">
          <div className="form-group">
            <label>Takip Numarası:</label>
            <input
              type="text"
              value={trackingNumber}
              onChange={(e) => setTrackingNumber(e.target.value)}
              placeholder="Takip numaranızı girin"
              required
            />
          </div>
          <div className="form-group">
            <label>E-posta:</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="E-posta adresinizi girin"
              required
            />
          </div>
          <button type="submit" className="submit-button" disabled={isLoading}>
            {isLoading ? 'Sorgulanıyor...' : 'Sorgula'}
          </button>
        </form>

        {/* Makale Bilgileri */}
        {article && (
          <div className="article-info">
            <h3>Makale Bilgileri</h3>
            <p>Takip Numarası: {article.tracking_number}</p>
            <p>Durum: {article.status}</p>
            
            {article.status === "sent_to_author" && article.evaluated_pdf_file && (
              <div className="download-section">
                <p>Makaleniz hakem değerlendirmesinden geçti ve size gönderildi.</p>
                <a
                  href={`http://127.0.0.1:8000/api/articles/evaluated/download/${article.tracking_number}/`}
                  download
                  className="download-button"
                >
                  Hakem Değerlendirmeli PDF’yi İndir
                </a>
              </div>
            )}
          </div>
        )}

        <Link to="/" className="home-link">
          <FaHome /> Ana Sayfa’ya Dön
        </Link>
      </div>

      {/* SAĞ SÜTUN */}
      <div className="status-right">
        {article ? (
          <YazarMessages trackingNumber={article.tracking_number} />
        ) : (
          <div className="no-article-message">
            <p>Lütfen makale durumunu sorguladıktan sonra mesajlaşma yapabilirsiniz.</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default ArticleStatus;
