// src/components/YazarMessages.js
import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import './Messages.css';

function YazarMessages({ trackingNumber: propTrackingNumber }) {
  // Use a local state for tracking number if not provided via props
  const [localTrackingNumber, setLocalTrackingNumber] = useState('');
  // Determine effective tracking number from prop or local state
  const effectiveTrackingNumber = propTrackingNumber || localTrackingNumber;

  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Function to fetch messages based on the effective tracking number
  const handleFetchMessages = useCallback(async () => {
    if (!effectiveTrackingNumber) {
      setError('Tracking number is required.');
      return;
    }
    setError('');
    setSuccess('');
    try {
      const response = await axios.get('http://127.0.0.1:8000/api/message/list/', {
        params: { tracking_number: effectiveTrackingNumber },
      });
      setMessages(response.data);
    } catch (err) {
      console.error(err);
      setError('Error fetching messages.');
    }
  }, [effectiveTrackingNumber]);

  // Automatically fetch messages when the effective tracking number changes
  useEffect(() => {
    if (effectiveTrackingNumber) {
      handleFetchMessages();
    }
  }, [effectiveTrackingNumber, handleFetchMessages]);

  // Function to send a new message (only "yazar" can send)
  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!effectiveTrackingNumber) {
      setError('Tracking number is not provided.');
      return;
    }
    if (!newMessage) {
      setError('Message cannot be empty.');
      return;
    }
    setError('');
    setSuccess('');
    try {
      await axios.post('http://127.0.0.1:8000/api/message/create/', {
        tracking_number: effectiveTrackingNumber,
        sender: 'yazar', // Hardcoded so only the author sends from here
        message_text: newMessage,
      });
      setSuccess('Message sent successfully!');
      setNewMessage('');
      handleFetchMessages(); // Refresh messages after sending
    } catch (err) {
      console.error(err);
      setError('Error sending message.');
    }
  };

  return (
    <div className="messages-container">
      <h2 className="messages-header">Yazar Mesajları</h2>
      {error && <p className="error-message">{error}</p>}
      {success && <p className="success-message">{success}</p>}

      {/* NEW CODE START: Use .tracking-number-group instead of inline style */}
      {!propTrackingNumber && (
        <div className="tracking-number-group">
          <label>Takip Numarası: </label>
          <input
            type="text"
            value={localTrackingNumber}
            onChange={(e) => setLocalTrackingNumber(e.target.value)}
            placeholder="Takip numaranızı girin"
          />
          <button onClick={handleFetchMessages}>Mesajları Getir</button>
        </div>
      )}
      {/* NEW CODE END */}

      <div className="messages-list">
        {messages.length > 0 ? (
          messages.map((msg) => (
            <div key={msg.id} className="message-item">
              <span className="message-sender">
                {msg.sender === 'editor' ? 'Editör' : 'Yazar'}:
              </span>
              <span className="message-text"> {msg.message_text}</span>
              <span className="message-time">
                {new Date(msg.sent_at).toLocaleString()}
              </span>
            </div>
          ))
        ) : (
          <p>No messages yet.</p>
        )}
      </div>

      <form onSubmit={handleSendMessage} className="message-form">
        <textarea
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          placeholder="Mesajınızı yazın..."
        />
        <button type="submit">Gönder</button>
      </form>
    </div>
  );
}

export default YazarMessages;
