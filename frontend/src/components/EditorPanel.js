import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import axios from "axios";
import { FaUserEdit, FaFilePdf, FaHome, FaList, FaDownload } from "react-icons/fa";
import "./EditorPanel.css"; // Özel CSS

function EditorPanel() {
  const [articles, setArticles] = useState([]);
  const [anonymizedArticles, setAnonymizedArticles] = useState([]);
  const [evaluatedArticles, setEvaluatedArticles] = useState([]);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // Anonimleştirme seçenekleri
  const [anonymizeName, setAnonymizeName] = useState(true);
  const [anonymizeContact, setAnonymizeContact] = useState(true);
  const [anonymizeAffiliation, setAnonymizeAffiliation] = useState(true);

  useEffect(() => {
    refreshArticles();
    fetchAnonymizedFiles();
    fetchEvaluatedArticles();
  }, []);

  // Tüm makaleleri çek
  const refreshArticles = () => {
    axios
      .get("http://127.0.0.1:8000/api/articles/")
      .then((response) => {
        setArticles(response.data);
      })
      .catch((err) => {
        console.error(err);
        setError("Makale listesi yenilenirken bir hata oluştu.");
      });
  };

  // Anonimleştirilmiş makaleleri çek
  const fetchAnonymizedFiles = () => {
    axios
      .get("http://127.0.0.1:8000/api/articles/anonymized/")
      .then((response) => {
        setAnonymizedArticles(response.data);
      })
      .catch((err) => {
        console.error(err);
        setError("Anonimleştirilmiş dosyalar yüklenirken hata oluştu.");
      });
  };

  // "evaluated" + "completed" durumundaki makaleleri çek
  const fetchEvaluatedArticles = () => {
    axios
      .get("http://127.0.0.1:8000/api/articles/evaluated/")
      .then((res) => {
        // Filtre: sadece evaluated veya completed
        const filtered = res.data.filter(
          (article) => article.status === "evaluated" || article.status === "completed"
        );
        // Eğer "completed" ise restored = true kabul edelim
        const updated = filtered.map((article) => ({
          ...article,
          restored: article.status === "completed" ? true : false,
        }));
        setEvaluatedArticles(updated);
      })
      .catch((err) => {
        console.error("Değerlendirilmiş dosyalar alınamadı", err);
      });
  };

  // Makale anonimleştirme
  const handleAnonymize = async (trackingNumber) => {
    try {
      await axios.post(
        `http://127.0.0.1:8000/api/articles/anonymize/${trackingNumber}/`,
        {
          anonymize_options: {
            name: anonymizeName,
            contact: anonymizeContact,
            affiliation: anonymizeAffiliation,
          },
        },
        { headers: { "Content-Type": "application/json" } }
      );
      setSuccess(`Makale (Takip No: ${trackingNumber}) başarıyla anonimleştirildi.`);
      refreshArticles();
      fetchAnonymizedFiles();
    } catch (err) {
      console.error(err);
      setError(`Makale (Takip No: ${trackingNumber}) anonimleştirilirken hata oluştu.`);
    }
  };

  // Hakeme atama
  const handleAssignReviewer = async (trackingNumber) => {
    try {
      await axios.post(`http://127.0.0.1:8000/api/articles/assign_reviewer/${trackingNumber}/`);
      setSuccess(`Makale (Takip No: ${trackingNumber}) bir hakeme atandı!`);
      refreshArticles();
    } catch (err) {
      console.error(err);
      setError(`Makale (Takip No: ${trackingNumber}) hakeme atanırken hata oluştu.`);
    }
  };

  // Restore Original (yazar bilgilerini geri yükleme)
  const handleRestoreOriginal = async (trackingNumber) => {
    try {
      await axios.post(`http://127.0.0.1:8000/api/articles/restore_original/${trackingNumber}/`);
      setSuccess(`Yazar bilgileri PDF'e başarıyla geri yüklendi!`);
      setEvaluatedArticles((prev) =>
        prev.map((art) =>
          art.tracking_number === trackingNumber
            ? { ...art, restored: true, status: "completed" }
            : art
        )
      );
    } catch (err) {
      console.error(err);
      setError("Yazar bilgileri geri yüklenirken hata oluştu.");
    }
  };

  // Yazara Gönder
  const handleSendToAuthor = async (trackingNumber) => {
    try {
      await axios.post(`http://127.0.0.1:8000/api/articles/send_to_author/${trackingNumber}/`);
      setSuccess(`Makale (Takip No: ${trackingNumber}) yazara gönderildi!`);
      setEvaluatedArticles((prev) =>
        prev.map((art) =>
          art.tracking_number === trackingNumber
            ? { ...art, status: "sent_to_author" }
            : art
        )
      );
    } catch (err) {
      console.error(err);
      setError("Makale yazara gönderilirken hata oluştu.");
    }
  };

  return (
    <div className="editor-panel">
      <h2>Editör Paneli</h2>

      {error && <p className="error-message">{error}</p>}
      {success && <p className="success-message">{success}</p>}

      {/* Anonimleştirme Seçenekleri */}
      <div className="anonymize-options">
        <h4>Anonimleştirme Seçenekleri:</h4>
        <label>
          <input
            type="checkbox"
            checked={anonymizeName}
            onChange={(e) => setAnonymizeName(e.target.checked)}
          />
          Yazar Ad-Soyad
        </label>
        <label>
          <input
            type="checkbox"
            checked={anonymizeContact}
            onChange={(e) => setAnonymizeContact(e.target.checked)}
          />
          Yazar iletişim bilgileri
        </label>
        <label>
          <input
            type="checkbox"
            checked={anonymizeAffiliation}
            onChange={(e) => setAnonymizeAffiliation(e.target.checked)}
          />
          Yazar kurum bilgileri
        </label>
      </div>

      {/* ÜST TABLO: Makale Listesi */}
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Takip Numarası</th>
              <th>E-posta</th>
              <th>Durum</th>
              <th>Hakem Ataması</th>
              <th>Anonimleştir</th>
              <th>Mesajlaş</th>
            </tr>
          </thead>
          <tbody>
            {articles.map((article) => (
              <tr key={article.tracking_number}>
                <td>{article.tracking_number}</td>
                <td>{article.email}</td>
                <td>{article.status}</td>
                <td>
                  {article.assigned_reviewer ? (
                    <div className="reviewer-info">
                      <strong>Hakem:</strong> {article.assigned_reviewer.name} (
                      {article.assigned_reviewer.email})
                    </div>
                  ) : (article.status === "anonymized" ||
                      (article.status === "revised" && article.anonymized_pdf_file)) ? (
                    <button
                      className="action-button assign-button"
                      onClick={() => handleAssignReviewer(article.tracking_number)}
                    >
                      <FaUserEdit /> Hakeme Ata
                    </button>
                  ) : (
                    <span>-</span>
                  )}
                </td>
                <td>
                  {(article.status === "uploaded" || article.status === "revised") && (
                    <button
                      className="action-button anonymize-button"
                      onClick={() => handleAnonymize(article.tracking_number)}
                    >
                      <FaFilePdf /> Anonimleştir
                    </button>
                  )}
                </td>
                <td>
                  <Link
                    to={`/editor/messages/${article.tracking_number}`}
                    className="action-button message-link"
                  >
                    Mesajlaş
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* ANONİMLEŞTİRİLMİŞ DOSYALAR */}
      <h3>Anonimleştirilmiş Dosyalar</h3>
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Makale Takip No</th>
              <th>İndir</th>
            </tr>
          </thead>
          <tbody>
            {anonymizedArticles.map((file, index) => (
              <tr key={index}>
                <td>{file.tracking_number}</td>
                <td>
                  <a
                    href={`http://127.0.0.1:8000/api/articles/anonymized/download/${file.tracking_number}/`}
                    download
                    className="action-button download-button"
                  >
                    <FaDownload /> İndir
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* ALT TABLO: Hakem Değerlendirmeli Dosyalar */}
      <h3>Hakem Değerlendirmeli Dosyalar</h3>
      <table className="evaluated-table">
        <thead>
          <tr>
            <th>Makale Takip No</th>
            <th>İşlem</th>
            <th>Yazara Gönder</th>
          </tr>
        </thead>
        <tbody>
          {evaluatedArticles.map((article) => (
            <tr key={article.id}>
              <td>{article.tracking_number}</td>
              <td>
                {article.status === "evaluated" && !article.restored ? (
                  <button
                    onClick={() => handleRestoreOriginal(article.tracking_number)}
                    className="restore-button"
                  >
                    Yazar Bilgilerini Geri Yükle
                  </button>
                ) : (
                  <a
                    href={`http://127.0.0.1:8000/api/articles/evaluated/download/${article.tracking_number}/`}
                    download
                    className="action-button download-button"
                  >
                    <FaDownload /> İndir ({article.status === "completed" ? "Completed" : "Restored"})
                  </a>
                )}
              </td>
              <td>
                {article.status !== "sent_to_author" ? (
                  <button
                    onClick={() => handleSendToAuthor(article.tracking_number)}
                    className="action-button send-to-author-button"
                  >
                    Yazara Gönder
                  </button>
                ) : (
                  <span>Gönderildi</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="links">
        <Link to="/editor/logs" className="link">
          <FaList /> Log Kayıtları
        </Link>
        <Link to="/" className="link">
          <FaHome /> Ana Sayfa’ya Dön
        </Link>
      </div>
    </div>
  );
}

export default EditorPanel;
