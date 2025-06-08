import React, { useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';

function ArticleRevise() {
  const [trackingNumber, setTrackingNumber] = useState('');
  const [pdfFile, setPdfFile] = useState(null);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleRevise = async (e) => {
    e.preventDefault();
    if (!trackingNumber || !pdfFile) {
      setError('Takip numarası ve PDF dosyası gereklidir.');
      return;
    }
    setIsLoading(true);
    setError('');
    setSuccess('');
    try {
      const formData = new FormData();
      formData.append('tracking_number', trackingNumber);
      formData.append('pdf_file', pdfFile);

      await axios.post('http://127.0.0.1:8000/api/article/revise/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setSuccess('Makale revize edildi!');
    } catch (err) {
      console.error(err);
      setError('Makale revize edilirken bir hata oluştu.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="form-container">
      <h2>Makale Revize Et</h2>
      {error && <p className="error-message">{error}</p>}
      {success && <p className="success-message">{success}</p>}
      <form onSubmit={handleRevise}>
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
          <label>Yeni PDF Dosyası:</label>
          <input
            type="file"
            accept="application/pdf"
            onChange={(e) => setPdfFile(e.target.files[0])}
            required
          />
        </div>
        <button type="submit" className="submit-button" disabled={isLoading}>
          {isLoading ? 'Revize ediliyor...' : 'Revize Yükle'}
        </button>
      </form>
      <Link to="/" className="home-link">
        Ana Sayfa’ya Dön
      </Link>
    </div>
  );
}

export default ArticleRevise;
