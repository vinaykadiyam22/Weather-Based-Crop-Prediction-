import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useTranslation } from 'react-i18next'
import { FiTarget, FiUsers, FiCpu, FiHeart } from 'react-icons/fi'
import i18n, { SUPPORTED_LANGS, setStoredLanguage } from '../i18n'
import './Landing.css'

function About() {
  const { t } = useTranslation()
  const currentLang = typeof window !== 'undefined' ? localStorage.getItem('app_language') || 'en' : 'en'

  return (
    <div className="landing">
      <div className="landing-bg" aria-hidden="true" />

      <header className="landing-header">
        <div className="container">
          <div className="header-inner">
            <Link to="/" className="logo">🌾 {t('brand')}</Link>
            <nav className="header-nav">
              <select className="lang-select-inline" value={currentLang} onChange={(e) => { setStoredLanguage(e.target.value); i18n.changeLanguage(e.target.value); }} aria-label={t('common.language')}>
                {SUPPORTED_LANGS.map((l) => <option key={l.code} value={l.code}>{l.label}</option>)}
              </select>
              <Link to="/" className="btn btn-secondary">{t('nav.home')}</Link>
              <Link to="/login" className="btn btn-secondary">{t('nav.login')}</Link>
              <Link to="/register" className="btn btn-primary">{t('nav.getStarted')}</Link>
            </nav>
          </div>
        </div>
      </header>

      <section className="about-content" style={{ padding: 'var(--space-16) 0', maxWidth: 720, margin: '0 auto' }}>
        <div className="container">
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <h1 className="hero-title" style={{ marginBottom: 'var(--space-6)' }}>About Smart Crop Advisory</h1>
            <p className="hero-subtitle" style={{ marginBottom: 'var(--space-8)' }}>
              An AI-based Smart Agriculture Assistance System that helps farmers make data-driven decisions using AI, ML, APIs, and real-time data to improve crop yield, profit, and sustainability.
            </p>

            <div className="about-sections" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-8)' }}>
              <div className="about-card">
                <FiTarget size={28} style={{ color: 'var(--color-primary)', marginBottom: 'var(--space-3)' }} />
                <h2 style={{ fontSize: 'var(--text-xl)', marginBottom: 'var(--space-2)' }}>Purpose</h2>
                <p style={{ color: 'var(--color-text-secondary)', lineHeight: 1.7 }}>
                  To empower Indian farmers with AI-powered insights for soil analysis, crop recommendations, weather forecasting, market prices, and pest/disease detection—all in one platform.
                </p>
              </div>

              <div className="about-card">
                <FiUsers size={28} style={{ color: 'var(--color-primary)', marginBottom: 'var(--space-3)' }} />
                <h2 style={{ fontSize: 'var(--text-xl)', marginBottom: 'var(--space-2)' }}>How It Helps Farmers</h2>
                <ul style={{ color: 'var(--color-text-secondary)', lineHeight: 1.8, paddingLeft: 'var(--space-6)' }}>
                  <li>NPK & pH soil analysis with fertilizer recommendations</li>
                  <li>Smart crop suggestions based on soil, weather, season, and market</li>
                  <li>Real-time weather and climate risk alerts</li>
                  <li>Live mandi prices and price trends</li>
                  <li>AI-powered disease detection from crop/leaf images</li>
                  <li>Soil type identification (manual or image upload)</li>
                  <li>Multilingual support (Hindi, Tamil, Telugu, and more)</li>
                </ul>
              </div>

              <div className="about-card">
                <FiCpu size={28} style={{ color: 'var(--color-primary)', marginBottom: 'var(--space-3)' }} />
                <h2 style={{ fontSize: 'var(--text-xl)', marginBottom: 'var(--space-2)' }}>Technologies Used</h2>
                <p style={{ color: 'var(--color-text-secondary)', lineHeight: 1.7 }}>
                  React, FastAPI, PyTorch (MobileNetV2 for disease detection), Google Gemini AI, Open-Meteo Weather API, data.gov.in for market prices, SQLite/PostgreSQL.
                </p>
              </div>

              <div className="about-card support-card">
                <FiHeart size={28} style={{ color: 'var(--color-primary)', marginBottom: 'var(--space-3)' }} />
                <h2 style={{ fontSize: 'var(--text-xl)', marginBottom: 'var(--space-2)' }}>Support & Project Commitment</h2>
                <p style={{ color: 'var(--color-text-secondary)', lineHeight: 1.7, fontWeight: 500 }}>
                  If any help is needed, we will help. Our team is committed to supporting farmers and improving this platform.
                </p>
              </div>
            </div>

            <div style={{ marginTop: 'var(--space-12)', textAlign: 'center' }}>
              <Link to="/register" className="btn btn-primary btn-lg">{t('landing.createAccount')}</Link>
            </div>
          </motion.div>
        </div>
      </section>

      <footer className="landing-footer">
        <div className="container">
          <p>{t('landing.copyright')}</p>
        </div>
      </footer>
    </div>
  )
}

export default About
