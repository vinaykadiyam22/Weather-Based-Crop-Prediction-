import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import axios from 'axios'
import { motion } from 'framer-motion'
import { FiMail, FiLock, FiArrowRight } from 'react-icons/fi'
import './Auth.css'

function Login({ onLogin }) {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [identifier, setIdentifier] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleLogin = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      // Backend expects { identifier, password } where identifier is email or phone
      const { data } = await axios.post('/api/auth/login', { identifier, password })
      onLogin(data)
      navigate('/dashboard')
    } catch (err) {
      console.error('Login error:', err)
      const d = err.response?.data?.detail
      setError(typeof d === 'string' ? d : 'Invalid email/phone or password. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-overlay"></div>
      <motion.div
        className="auth-container"
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
      >
        <div className="auth-card premium-shadow">
          <div className="auth-header">
            <div className="auth-logo">
               <div className="logo-icon">🌱</div>
            </div>
            <h1 className="auth-title">{t('auth.welcomeBack')}</h1>
            <p className="auth-subtitle">{t('auth.signInSubtitle')}</p>
          </div>

          {error && (
            <motion.div 
              className="alert alert-danger"
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
            >
              {error}
            </motion.div>
          )}

          <form onSubmit={handleLogin} className="auth-form">
            <div className="form-group">
              <label className="form-label">{t('auth.emailAddress')} / {t('auth.phoneNumber')}</label>
              <div className="input-with-icon">
                <FiMail className="input-icon" />
                <input
                  type="text"
                  className="form-input"
                  value={identifier}
                  onChange={(e) => setIdentifier(e.target.value)}
                  placeholder="farmer@example.com / +91..."
                  required
                  autoComplete="username"
                />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">{t('auth.password')}</label>
              <div className="input-with-icon">
                <FiLock className="input-icon" />
                <input
                  type="password"
                  className="form-input"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder={t('auth.passwordPlaceholder')}
                  required
                  autoComplete="current-password"
                />
              </div>
            </div>

            <button type="submit" className="btn btn-primary btn-block btn-lg" disabled={loading}>
              {loading ? (
                <span className="flex-center">
                  <div className="spinner-small"></div>
                  {t('auth.verifying')}
                </span>
              ) : (
                <span className="flex-center">
                  {t('auth.signIn')} <FiArrowRight style={{ marginLeft: '8px' }} />
                </span>
              )}
            </button>
          </form>

          <div className="auth-footer">
            <p className="footer-text">
              {t('auth.dontHaveAccount')} <Link to="/register" className="auth-link">{t('auth.register')}</Link>
            </p>
            <div className="footer-divider"></div>
            <Link to="/admin/login" className="admin-link">Admin Access</Link>
          </div>
        </div>
      </motion.div>
    </div>
  )
}

export default Login
