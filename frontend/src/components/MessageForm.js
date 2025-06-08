import React, { useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';

function MessageForm() {
  const [trackingNumber, setTrackingNumber] = useState('');
  const [messageText, setMessageText] = useState('');
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!trackingNumber || !messageText) {
      setError('Takip numarası ve mesaj alanı gereklidir.');
      return;
    }
    setIsLoading(true);
    setError('');
    setSuccess('');
    try {
      const response = await axios.post('http://127.0.0.1:8000/api/message/create/', {
        tracking_number: trackingNumber,
        sender: 'yazar',  // Gönderen yazar olarak işaretlensin
        message_text: messageText,
      });
      setSuccess('Mesajınız gönderildi!');
    } catch (err) {
      console.error(err);
      setError('Mesaj gönderilirken bir hata oluştu.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="form-container">
      <h2>Editöre Mesaj Gönder</h2>
      {error && <p className="error-message">{error}</p>}
      {success && <p className="success-message">{success}</p>}
      <form onSubmit={handleSendMessage}>
        <div className="form-group">
          <label>Takip Numarası:</label>
          <input
            type="text"
            value={trackingNumber}
            onChange={(e) => setTrackingNumber(e.target.value)}
            placeholder="Makale takip numaranızı girin"
            required
          />
        </div>
        <div className="form-group">
          <label>Mesaj:</label>
          <textarea
            value={messageText}
            onChange={(e) => setMessageText(e.target.value)}
            placeholder="Editöre göndermek istediğiniz mesajı yazın"
            required
          />
        </div>
        <button type="submit" className="submit-button" disabled={isLoading}>
          {isLoading ? 'Gönderiliyor...' : 'Mesajı Gönder'}
        </button>
      </form>
      <Link to="/" className="home-link">
        Ana Sayfa’ya Dön
      </Link>
    </div>
  );
}

export default MessageForm;
