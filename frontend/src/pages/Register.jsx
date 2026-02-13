import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import axios from 'axios'
import { motion } from 'framer-motion'
import './Auth.css'

function Register() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    location: 'Andhra Pradesh',
    language: 'te'
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      await axios.post('/api/auth/register', formData)
      alert('Registration successful! Please sign in.')
      navigate('/login')
    } catch (err) {
      const detail = err.response?.data?.detail
      const message = typeof detail === 'string'
        ? detail
        : Array.isArray(detail) && detail[0]?.msg
          ? detail[0].msg
          : 'Registration failed. Please try again.'
      setError(message)
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
          <h1 className="auth-title">{t('auth.createAccountTitle')}</h1>
          <p className="auth-subtitle">{t('auth.createAccountSubtitle')}</p>

          {error && <div className="alert alert-danger">{error}</div>}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">{t('auth.fullName')}</label>
              <input
                type="text"
                name="name"
                className="form-input"
                value={formData.name}
                onChange={handleChange}
                placeholder={t('auth.namePlaceholder')}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">{t('auth.emailAddress')}</label>
              <input
                type="email"
                name="email"
                className="form-input"
                value={formData.email}
                onChange={handleChange}
                placeholder={t('auth.emailPlaceholder')}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">{t('auth.phoneNumber')}</label>
              <input
                type="tel"
                name="phone"
                className="form-input"
                value={formData.phone}
                onChange={handleChange}
                placeholder={t('auth.phonePlaceholder')}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">{t('auth.locationLabel')}</label>
              <input
                type="text"
                name="location"
                className="form-input"
                value={formData.location}
                onChange={handleChange}
                placeholder={t('auth.locationPlaceholder')}
                list="ap-locations"
                required
              />
              <datalist id="ap-locations">
                <option value="Andhra Pradesh" />
                <option value="Vijayawada" />
                <option value="Visakhapatnam" />
                <option value="Guntur" />
                <option value="Kurnool" />
                <option value="Nellore" />
                <option value="Rajahmundry" />
                <option value="Tirupati" />
                <option value="Kakinada" />
                <option value="Anantapur" />
                <option value="Eluru" />
                <option value="Ongole" />
              </datalist>
            </div>

            <div className="form-group">
              <label className="form-label">{t('auth.languageLabel')}</label>
              <select name="language" className="form-select" value={formData.language} onChange={handleChange}>
                <option value="en">English</option>
                <option value="hi">हिन्दी (Hindi)</option>
                <option value="ta">தமிழ் (Tamil)</option>
                <option value="te">తెలుగు (Telugu)</option>
                <option value="bn">বাংলা (Bengali)</option>
                <option value="mr">मराठी (Marathi)</option>
                <option value="gu">ગુજરાતી (Gujarati)</option>
              </select>
            </div>

            <button type="submit" className="btn btn-primary btn-block" disabled={loading}>
              {loading ? t('auth.creatingAccount') : t('auth.createAccountBtn')}
            </button>
          </form>

          <div className="auth-footer">
            <p>{t('auth.alreadyHaveAccount')} <Link to="/login">{t('auth.signIn')}</Link></p>
          </div>
        </div>
      </motion.div>
    </div>
  )
}

export default Register
