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
  const [method, setMethod] = useState('email')
  const [identifier, setIdentifier] = useState('')
  const [otp, setOtp] = useState('')
  const [step, setStep] = useState('request')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  const handleRequestOTP = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setMessage('')
    setOtp('')
    try {
      const { data } = await axios.post('/api/auth/login/request-otp', { identifier, method })
      setMessage(data.otp 
        ? `Your OTP: ${data.otp}` 
        : `OTP sent via ${method}. Check your ${method === 'email' ? 'inbox' : 'messages'}.`)
      if (data.otp) setOtp(data.otp)
      setStep('verify')
    } catch (err) {
      const d = err.response?.data?.detail
      setError(typeof d === 'string' ? d : 'Failed to send OTP. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleVerifyOTP = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const { data } = await axios.post('/api/auth/login/verify-otp', { identifier, otp, method })
      onLogin(data)
      navigate('/dashboard')
    } catch (err) {
      const d = err.response?.data?.detail
      setError(typeof d === 'string' ? d : 'Invalid OTP. Please try again.')
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
          {message && <div className="alert alert-success">{message}</div>}

          {step === 'request' ? (
            <form onSubmit={handleRequestOTP}>
              <div className="form-group">
                <label className="form-label">{t('auth.loginMethod')}</label>
                <div className="method-selector">
                  <button
                    type="button"
                    className={`method-btn ${method === 'email' ? 'active' : ''}`}
                    onClick={() => setMethod('email')}
                  >
                    <FiMail style={{ marginRight: 6, verticalAlign: 'middle' }} />
                    {t('auth.email')}
                  </button>
                  <button
                    type="button"
                    className={`method-btn ${method === 'sms' ? 'active' : ''}`}
                    onClick={() => setMethod('sms')}
                  >
                    <FiPhone style={{ marginRight: 6, verticalAlign: 'middle' }} />
                    {t('auth.sms')}
                  </button>
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">
                  {method === 'email' ? t('auth.emailAddress') : t('auth.phoneNumber')}
                </label>
                <input
                  type={method === 'email' ? 'email' : 'tel'}
                  className="form-input"
                  value={identifier}
                  onChange={(e) => setIdentifier(e.target.value)}
                  placeholder={method === 'email' ? t('auth.emailPlaceholder') : t('auth.phonePlaceholder')}
                  required
                />
              </div>

              <button type="submit" className="btn btn-primary btn-block" disabled={loading}>
                {loading ? t('auth.sending') : t('auth.sendOtp')}
              </button>
            </form>
          ) : (
            <form onSubmit={handleVerifyOTP}>
              <div className="form-group">
                <label className="form-label">{t('auth.enterOtp')}</label>
                <input
                  type="text"
                  className="form-input otp-input"
                  value={otp}
                  onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                  placeholder={t('auth.otpPlaceholder')}
                  maxLength={6}
                  required
                />
                <span className="form-hint">{t('auth.otpSentTo')} {identifier}</span>
              </div>

              <button type="submit" className="btn btn-primary btn-block" disabled={loading}>
                {loading ? t('auth.verifying') : t('auth.verifySignIn')}
              </button>

              <button
                type="button"
                className="btn btn-outline btn-block"
                style={{ marginTop: 'var(--space-3)' }}
                onClick={() => setStep('request')}
              >
                {t('common.back')}
              </button>
            </form>
          )}

          <div className="auth-footer">
            <p>{t('auth.dontHaveAccount')} <Link to="/register">{t('auth.register')}</Link></p>
          </div>
        </div>
      </motion.div>
    </div>
  )
}

export default Login
