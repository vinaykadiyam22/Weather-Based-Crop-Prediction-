import { Link, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import { FiMenu, FiX, FiLogOut } from 'react-icons/fi'
import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import axios from 'axios'
import i18n, { SUPPORTED_LANGS, setStoredLanguage, getStoredLanguage } from '../i18n'
import './AppLayout.css'

function AppLayout({ children, user, onLogout, onUserUpdate }) {
  const { t } = useTranslation()
  const location = useLocation()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const currentLang = i18n.language || user?.language || (typeof window !== 'undefined' ? getStoredLanguage() || 'en' : 'en')

  const handleLanguageChange = async (lang) => {
    if (user?.id && onUserUpdate) {
      try {
        const { data } = await axios.put(`/api/auth/user/${user.id}?language=${lang}`)
        onUserUpdate(data)
      } catch { /* ignore */ }
    }
    setStoredLanguage(lang)
    i18n.changeLanguage(lang)
  }

  const isActive = (path) => {
    if (path === '/dashboard') return location.pathname === '/dashboard'
    return location.pathname.startsWith(path)
  }

  return (
    <div className="app-layout">
      <header className="app-nav">
        <div className="nav-container">
          <Link to="/dashboard" className="nav-brand">
            <span className="brand-icon">🛡️</span>
            <span className="brand-text">{t('brand')} <small style={{fontSize: '0.6em', opacity: 0.7}}>v4.2.0</small></span>
          </Link>

          <nav className="nav-links">
            <Link to="/dashboard" className={`nav-link ${isActive('/dashboard') ? 'active' : ''}`}>
              {t('common.dashboard')}
            </Link>
          </nav>

          <div className="nav-actions">
            <div className="lang-selector">
              <span className="lang-label">{t('common.languageLabel')}</span>
              <select
                className="lang-select"
                value={currentLang}
                onChange={(e) => handleLanguageChange(e.target.value)}
                aria-label={t('common.languageLabel')}
                title={t('dashboard.tip')}
              >
                {SUPPORTED_LANGS.map((l) => (
                  <option key={l.code} value={l.code}>{l.label}</option>
                ))}
              </select>
            </div>
            <span className="user-name">{user?.name}</span>
            <button onClick={onLogout} className="btn btn-secondary btn-icon" aria-label={t('common.logout')}>
              <FiLogOut size={18} />
              {t('common.logout')}
            </button>
          </div>

          <button
            className="nav-toggle"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle menu"
            aria-expanded={mobileMenuOpen}
          >
            {mobileMenuOpen ? <FiX size={24} /> : <FiMenu size={24} />}
          </button>
        </div>

        {mobileMenuOpen && (
          <motion.div
            className="nav-mobile"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
          >
            <Link
              to="/dashboard"
              className={`nav-mobile-link ${isActive('/dashboard') ? 'active' : ''}`}
              onClick={() => setMobileMenuOpen(false)}
            >
              {t('common.dashboard')}
            </Link>
            <div className="lang-selector-mobile">
              <span className="lang-label">{t('common.languageLabel')}</span>
              <select
                className="lang-select-mobile"
                value={currentLang}
                onChange={(e) => handleLanguageChange(e.target.value)}
              >
                {SUPPORTED_LANGS.map((l) => (
                  <option key={l.code} value={l.code}>{l.label}</option>
                ))}
              </select>
            </div>
            <button onClick={() => { onLogout(); setMobileMenuOpen(false); }} className="nav-mobile-link nav-mobile-logout">
              {t('common.logout')}
            </button>
          </motion.div>
        )}
      </header>

      <main className="app-main">
        {children}
      </main>
      <footer className="app-footer-minimal">
        <div className="container">
          <p>© 2026 Standard Secure Portal • v4.2.0</p>
        </div>
      </footer>
    </div>
  )
}

export default AppLayout
