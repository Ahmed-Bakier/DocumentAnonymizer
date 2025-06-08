import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { FaUpload, FaSearch, FaUserEdit, FaUserCheck, FaShieldAlt, FaEye } from 'react-icons/fa';
import './Homepage.css'; 

function Homepage() {
  useEffect(() => {
    // Animation for elements to fade in when scrolled into view
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('appear');
        }
      });
    }, { threshold: 0.1 });

    document.querySelectorAll('.animate-on-scroll').forEach(el => {
      observer.observe(el);
    });

    return () => {
      document.querySelectorAll('.animate-on-scroll').forEach(el => {
        observer.unobserve(el);
      });
    };
  }, []);

  return (
    <div className="homepage">
      {/* Header Hero Section */}
      <section className="hero-section">
        <div className="container">
          <div className="hero-content">
            <div className="hero-text animate-on-scroll">
              <div className="hero-tag">Güvenli Akademik Makale İnceleme Sistemi</div>
              <h1>
                Anonim Belge İncelemesi Artık Çok <span className="highlight">Kolay</span>
              </h1>
              <p>
                Akademik makalelerinizi güvenli ve anonim inceleme için yükleyin. Sistemimiz, yazar kimliklerini korurken adil değerlendirmeler sağlar.
              </p>
              <div className="hero-buttons">
                <Link to="/upload" className="btn primary-btn">
                  <FaUpload /> Makale Yükle
                </Link>
                <Link to="/status" className="btn outline-btn">
                  <FaSearch /> Başvuruyu Takip Et
                </Link>
              </div>
            </div>
            <div className="hero-image animate-on-scroll">
              <img src="/images/hero-image.webp" alt="Akademik Makale İnceleme" />
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="how-it-works">
        <div className="container">
          <h2 className="section-title animate-on-scroll">Nasıl Çalışır?</h2>
          <p className="section-subtitle animate-on-scroll">Güvenli belge anonimleştirme sistemimiz akademik inceleme sürecini kolaylaştırır</p>
          
          <div className="steps">
            <div className="step-card animate-on-scroll">
              <div className="step-icon">
                <FaUpload />
              </div>
              <h3>1. Makalenizi Gönderin</h3>
              <p>PDF belgenizi yükleyin ve benzersiz bir takip numarası almak için e-postanızı girin.</p>
            </div>
            
            <div className="step-card animate-on-scroll">
              <div className="step-icon">
                <FaShieldAlt />
              </div>
              <h3>2. Güvenli Anonimleştirme</h3>
              <p>Editörlerimiz makalenizi hakemlere göndermeden önce tüm kimlik bilgilerini kaldırır.</p>
            </div>
            
            <div className="step-card animate-on-scroll">
              <div className="step-icon">
                <FaEye />
              </div>
              <h3>3. Uzman İncelemesi</h3>
              <p>Hakemler, makalenizi yazar kimliğine değil, içeriğine göre değerlendirir.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Why Choose Us Section */}
      <section className="why-choose-us">
        <div className="container">
          <div className="why-choose-content">
            <div className="why-image animate-on-scroll">
              <img src="/images/why-choose-us.jpg" alt="Neden Sistemimizi Tercih Etmelisiniz?" />
            </div>
            
            <div className="why-text animate-on-scroll">
              <h2 className="section-title">Neden Sistemimizi Tercih Etmelisiniz?</h2>
              <p>Platformumuz, en son anonimleştirme teknolojisi sayesinde adil, tarafsız değerlendirmeler sağlar.</p>
              
              <ul className="feature-list">
                <li>
                  <span className="check-icon">✓</span>
                  Tamamen anonimleştirilmiş yazar bilgileri
                </li>
                <li>
                  <span className="check-icon">✓</span>
                  Güvenli belge yönetimi ve depolama
                </li>
                <li>
                  <span className="check-icon">✓</span>
                  Kolaylaştırılmış değerlendirme süreci
                </li>
                <li>
                  <span className="check-icon">✓</span>
                  Başvuru durumunun kolay takibi
                </li>
                <li>
                  <span className="check-icon">✓</span>
                  Yazarlar ve editörler arasında basit iletişim
                </li>
              </ul>
              
              <Link to="/upload" className="btn primary-btn">
                Hemen Başlayın <span className="arrow">→</span>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Roles Section */}
      <section className="roles-section">
        <div className="container">
          <h2 className="section-title animate-on-scroll">Süreçteki Her Rol İçin</h2>
          <p className="section-subtitle animate-on-scroll">Platformumuz yazarlar, hakemler ve yöneticilerin ihtiyaçlarına hizmet eder</p>
          
          <div className="navigation-cards">
            <Link to="/author" className="card animate-on-scroll">
              <div className="card-icon">
                <FaUpload size={40} />
              </div>
              <h2>Yazar Paneli</h2>
              <p>Kayıt olmadan makale yükleyin, başvurularınızı takip edin ve geri bildirim alın.</p>
            </Link>

            <Link to="/editor" className="card animate-on-scroll">
              <div className="card-icon">
                <FaUserEdit size={40} />
              </div>
              <h2>Editör Paneli</h2>
              <p>Makaleleri yönetin ve hakem atamaları yapın.</p>
            </Link>

            <Link to="/reviewer" className="card animate-on-scroll">
              <div className="card-icon">
                <FaUserCheck size={40} />
              </div>
              <h2>Hakem Paneli</h2>
              <p>Anonim makaleleri değerlendirin.</p>
            </Link>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="container">
          <h2 className="section-title animate-on-scroll">Makaleyi Göndermeye Hazır mısınız?</h2>
          <p className="section-subtitle animate-on-scroll">Platformumuzla adil, güvenli ve verimli bir akademik değerlendirme süreci yaşayın.</p>
          
          <div className="cta-buttons animate-on-scroll">
            <Link to="/upload" className="btn primary-btn">
              <FaUpload /> Makale Yükle
            </Link>
            <Link to="/status" className="btn outline-btn">
              <FaSearch /> Başvuruyu Takip Et
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}

export default Homepage;