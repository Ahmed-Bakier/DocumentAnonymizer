import React, { useEffect, useState, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import './Messages.css';

function EditorMessages() {
  const { trackingNumber } = useParams();
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Wrap fetchMessages in useCallback with trackingNumber as dependency
  const fetchMessages = useCallback(async () => {
    try {
      const response = await axios.get('http://127.0.0.1:8000/api/message/list/', {
        params: { tracking_number: trackingNumber },
      });
      setMessages(response.data);
    } catch (err) {
      setError('Mesajlar alınırken hata oluştu.');
    }
  }, [trackingNumber]);

  useEffect(() => {
    fetchMessages();
  }, [fetchMessages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!newMessage) {
      setError('Mesaj alanı boş olamaz.');
      return;
    }
    try {
      await axios.post('http://127.0.0.1:8000/api/message/create/', {
        tracking_number: trackingNumber,
        sender: 'editor',
        message_text: newMessage,
      });
      setSuccess('Mesaj gönderildi!');
      setNewMessage('');
      fetchMessages();
    } catch (err) {
      setError('Mesaj gönderilirken hata oluştu.');
    }
  };

  return (
    <div className="messages-container">
      <h2 className="messages-header">
        Mesajlar (Takip No: {trackingNumber})
      </h2>

      {error && <p className="error-message">{error}</p>}
      {success && <p className="success-message">{success}</p>}

      <div className="messages-list">
        {messages.map((msg) => (
          <div key={msg.id} className="message-item">
            <span className="message-sender">
              {msg.sender === 'editor' ? 'Editör' : 'Yazar'}:
            </span>
            <span className="message-text">{msg.message_text}</span>
            <span className="message-time">
              {new Date(msg.sent_at).toLocaleString()}
            </span>
          </div>
        ))}
      </div>

      <form onSubmit={handleSend} className="message-form">
        <textarea
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          placeholder="Mesajınızı yazın..."
        />
        <button type="submit">Gönder</button>
      </form>

      <Link to="/editor" className="back-link">
        Editör Paneline Dön
      </Link>
    </div>
  );
}

export default EditorMessages;
