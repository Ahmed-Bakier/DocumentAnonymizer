import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import './ArticleUpload.css'; // Import the new CSS file
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faUpload, faHome, faSpinner, faCheck, faExclamationTriangle } from '@fortawesome/free-solid-svg-icons';

function ArticleUpload() {
  const [email, setEmail] = useState('');
  const [pdfFile, setPdfFile] = useState(null);
  const [fileName, setFileName] = useState('');
  const [trackingNumber, setTrackingNumber] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validate inputs
    if (!email || !pdfFile) {
      setError('Lütfen tüm alanları doldurun.');
      return;
    }

    if (!validateEmail(email)) {
      setError('Geçerli bir e-posta adresi girin.');
      return;
    }

    // Prepare form data
    const formData = new FormData();
    formData.append('email', email);
    formData.append('pdf_file', pdfFile);

    setIsLoading(true); // Start loading
    setError(''); // Clear previous errors
    setSuccess(''); // Clear previous success messages

    try {
      const response = await axios.post(
        'http://127.0.0.1:8000/api/upload/',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      
      setSuccess('Makaleniz başarıyla yüklendi!');
      setTrackingNumber(response.data.tracking_number);
      setIsLoading(false);
    } catch (err) {
      if (err.response) {
        console.error('Status Code:', err.response.status);
        console.error('Response Data:', err.response.data);
      } else if (err.request) {
        console.error('No response received:', err.request);
      } else {
        console.error('Error setting up request:', err.message);
      }
      setError('Makale yüklenirken bir hata oluştu. Lütfen tekrar deneyin.');
      setIsLoading(false);
    }
  };

  const validateEmail = (email) => {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.type === 'application/pdf') {
      setPdfFile(selectedFile);
      setFileName(selectedFile.name);
    } else {
      setPdfFile(null);
      setFileName('');
      setError('Lütfen sadece PDF dosyası yükleyin.');
    }
  };

  return (
    <div className="form-container">
      <h2>Makale Yükleme</h2>
      
      {error && (
        <div className="error-message">
          <FontAwesomeIcon icon={faExclamationTriangle} /> {error}
        </div>
      )}
      
      {success && (
        <div className="success-message">
          <FontAwesomeIcon icon={faCheck} /> {success}
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="email">E-posta Adresi:</label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="ornek@email.com"
            required
          />
        </div>
        
        <div className="form-group">
          <label>PDF Dosyası:</label>
          <div className={`file-upload-container ${fileName ? 'has-file' : ''}`}>
            <input
              type="file"
              accept="application/pdf"
              onChange={handleFileChange}
              required
            />
            <FontAwesomeIcon icon={faUpload} className="file-upload-icon" />
            <span className={`file-upload-text ${fileName ? 'file-selected' : ''}`}>
              {fileName ? fileName : 'PDF dosyanızı sürükleyin veya seçin'}
            </span>
          </div>
        </div>
        
        <button type="submit" className="submit-button" disabled={isLoading}>
          {isLoading ? (
            <>
              <FontAwesomeIcon icon={faSpinner} spin /> Yükleniyor...
            </>
          ) : (
            'Makale Yükle'
          )}
        </button>
      </form>
      
      {trackingNumber && (
        <div className="tracking-info">
          <FontAwesomeIcon icon={faCheck} /> Makale yüklendi. Takip Numarası: <strong>{trackingNumber}</strong>
        </div>
      )}
      
      <Link to="/" className="home-link">
        <FontAwesomeIcon icon={faHome} className="home-link-icon" /> Ana Sayfa'ya Dön
      </Link>
    </div>
  );
}

export default ArticleUpload;