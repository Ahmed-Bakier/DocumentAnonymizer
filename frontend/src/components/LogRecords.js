import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { FaFileAlt, FaArrowLeft, FaHome } from 'react-icons/fa';
import axios from 'axios';

function LogRecords() {
  const [logs, setLogs] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchLogs();
  }, []);

  const fetchLogs = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:8000/api/logs/');
      setLogs(response.data);
    } catch (err) {
      console.error(err);
      setError('Log kayıtları alınırken bir hata oluştu.');
    }
  };

  return (
    <div className="log-records">
      <h2>Log Kayıtları</h2>
      {error && <p style={{ color: 'red' }}>{error}</p>}

      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Makale</th>
              <th>İşlem</th>
              <th>Zaman</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log) => (
              <tr key={log.id}>
                <td>
                  <FaFileAlt className="log-icon" /> {log.article_tracking_number}
                </td>
                <td>{log.description}</td>
                <td>{new Date(log.timestamp).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="links">
        <Link to="/editor" className="link">
          <FaArrowLeft /> Editör Paneli’ne Dön
        </Link>
        <Link to="/" className="link">
          <FaHome /> Ana Sayfa’ya Dön
        </Link>
      </div>
    </div>
  );
}

export default LogRecords;
