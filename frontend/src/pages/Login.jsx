import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import axios from 'axios'
import { motion } from 'framer-motion'
import { FiMail, FiPhone } from 'react-icons/fi'
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
      const { data } = await axios.post('/api/auth/login', { identifier, password })
      onLogin(data)
      navigate('/dashboard')
    } catch (err) {
      const d = err.response?.data?.detail
      setError(typeof d === 'string' ? d : 'Invalid credentials. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <motion.div
        className="auth-container"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <div className="auth-card">
          <h1 className="auth-title">{t('auth.welcomeBack')}</h1>
          <p className="auth-subtitle">{t('auth.signInSubtitle')}</p>

          {error && <div className="alert alert-danger">{error}</div>}

          <form onSubmit={handleLogin}>
            <div className="form-group">
              <label className="form-label">{t('auth.emailAddress')} / {t('auth.phoneNumber')}</label>
              <input
                type="text"
                className="form-input"
                value={identifier}
                onChange={(e) => setIdentifier(e.target.value)}
                placeholder={`${t('auth.emailPlaceholder')} / ${t('auth.phonePlaceholder')}`}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">{t('auth.password')}</label>
              <input
                type="password"
                className="form-input"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder={t('auth.passwordPlaceholder')}
                required
              />
            </div>

            <button type="submit" className="btn btn-primary btn-block" disabled={loading}>
              {loading ? t('auth.verifying') : t('auth.signIn')}
            </button>
          </form>

          <div className="auth-footer">
            <p>{t('auth.dontHaveAccount')} <Link to="/register">{t('auth.register')}</Link></p>
            <p style={{ marginTop: '12px', fontSize: '13px' }}>
                <Link to="/admin/login" style={{ opacity: 0.6 }}>Admin Login</Link>
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  )
}

export default Login
