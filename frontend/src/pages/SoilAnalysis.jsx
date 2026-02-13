import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import axios from 'axios'
import { getEffectiveLanguage } from '../i18n'
import { motion } from 'framer-motion'
import AppLayout from '../components/AppLayout'
import AdvisoryMarkdown from '../components/AdvisoryMarkdown'
import { FiArrowLeft } from 'react-icons/fi'
import './FeaturePage.css'

const SOIL_TYPES = ['Clay', 'Sandy', 'Loamy', 'Silty', 'Black Soil', 'Red Soil', 'Alluvial']

function SoilAnalysis({ user, onLogout, onUserUpdate }) {
  const { t } = useTranslation()
  const [formData, setFormData] = useState({
    soil_type: '',
    nitrogen: '',
    phosphorus: '',
    potassium: '',
    ph: '',
    organic_matter: '',
    location: user?.location || ''
  })
  const [result, setResult] = useState(null)
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showHistory, setShowHistory] = useState(false)

  useEffect(() => {
    if (user?.id) {
      axios.get(`/api/soil/history/${user.id}`)
        .then(res => setHistory(res.data.analyses || []))
        .catch(() => setHistory([]))
    }
  }, [user])

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const res = await axios.post('/api/soil/analyze', {
        user_id: user.id,
        soil_type: formData.soil_type || null,
        nitrogen: parseFloat(formData.nitrogen),
        phosphorus: parseFloat(formData.phosphorus),
        potassium: parseFloat(formData.potassium),
        ph: parseFloat(formData.ph),
        organic_matter: formData.organic_matter ? parseFloat(formData.organic_matter) : null,
        location: formData.location,
        language: getEffectiveLanguage(user)
      })
      setResult(res.data)
      axios.get(`/api/soil/history/${user.id}`).then(r => setHistory(r.data.analyses || []))
    } catch (err) {
      setError(err.response?.data?.detail || 'Analysis failed. Check your inputs.')
    } finally {
      setLoading(false)
    }
  }

  const getHealthColor = (h) => ({ good: '#059669', medium: '#d97706', poor: '#dc2626' }[h] || '#64748b')

  return (
    <AppLayout user={user} onLogout={onLogout} onUserUpdate={onUserUpdate}>
      <div className="feature-page">
        <div className="container">
          <Link to="/dashboard" className="back-link">
            <FiArrowLeft size={16} /> {t('common.backToDashboard')}
          </Link>
          <div className="page-header">
            <h1 className="page-title">{t('soil.title')}</h1>
            <p className="page-subtitle">{t('soil.subtitle')}</p>
          </div>

          {history.length > 0 && (
            <div style={{ marginBottom: 'var(--space-4)' }}>
              <button
                className="btn btn-secondary"
                onClick={() => setShowHistory(!showHistory)}
              >
                {showHistory ? t('common.hide') : t('soil.viewHistory')} {t('soil.history')} ({history.length})
              </button>
            </div>
          )}

          {showHistory && history.length > 0 && (
            <motion.div
              className="card"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              style={{ marginBottom: 'var(--space-6)' }}
            >
              <h2 style={{ marginBottom: 'var(--space-4)' }}>{t('soil.history')}</h2>
              <div className="grid grid-2">
                {history.map((a) => (
                  <div key={a.id} className="param-item">
                    <span className="param-label">{new Date(a.date).toLocaleDateString()}</span>
                    <span className="param-value">{a.soil_type || '—'} · {a.soil_health}</span>
                  </div>
                ))}
              </div>
            </motion.div>
          )}

          <div className="feature-content">
            <motion.div
              className="card"
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <h2 style={{ marginBottom: 'var(--space-6)' }}>{t('soil.soilParameters')}</h2>
              <form onSubmit={handleSubmit}>
                <div className="form-row">
                  <div className="form-group">
                    <label className="form-label">{t('soil.soilType')}</label>
                    <select name="soil_type" className="form-control" value={formData.soil_type} onChange={handleChange}>
                      <option value="">{t('soil.soilTypeOptional')}</option>
                      {SOIL_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">{t('soil.location')}</label>
                    <input type="text" name="location" className="form-control" value={formData.location} onChange={handleChange} placeholder={t('soil.fieldLocation')} />
                  </div>
                </div>
                <div className="form-row">
                  <div className="form-group">
                    <label className="form-label">{t('soil.nitrogen')}</label>
                    <input type="number" name="nitrogen" className="form-control" value={formData.nitrogen} onChange={handleChange} required step="0.1" />
                  </div>
                  <div className="form-group">
                    <label className="form-label">{t('soil.phosphorus')}</label>
                    <input type="number" name="phosphorus" className="form-control" value={formData.phosphorus} onChange={handleChange} required step="0.1" />
                  </div>
                  <div className="form-group">
                    <label className="form-label">{t('soil.potassium')}</label>
                    <input type="number" name="potassium" className="form-control" value={formData.potassium} onChange={handleChange} required step="0.1" />
                  </div>
                </div>
                <div className="form-row">
                  <div className="form-group">
                    <label className="form-label">{t('soil.phLevel')}</label>
                    <input type="number" name="ph" className="form-control" value={formData.ph} onChange={handleChange} required step="0.1" min="0" max="14" />
                  </div>
                  <div className="form-group">
                    <label className="form-label">{t('soil.organicMatter')}</label>
                    <input type="number" name="organic_matter" className="form-control" value={formData.organic_matter} onChange={handleChange} step="0.1" />
                  </div>
                </div>
                {error && <div className="alert alert-danger">{error}</div>}
                <button type="submit" className="btn btn-primary btn-lg" disabled={loading}>
                  {loading ? t('soil.analyzing') : t('soil.analyzeSoil')}
                </button>
              </form>
            </motion.div>

            {result && (
              <motion.div
                className="result-card"
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
              >
                <div className="result-header">
                  <h2>{t('soil.results')}</h2>
                  <span className="btn btn-secondary" style={{ backgroundColor: getHealthColor(result.soil_health), color: 'white', border: 'none' }}>
                    {result.soil_health}
                  </span>
                </div>
                <div className="soil-params">
                  <h3>{t('soil.parameters')}</h3>
                  <div className="params-grid">
                    {result.soil_parameters.soil_type && (
                      <div className="param-item"><span className="param-label">{t('soil.soilType')}</span><span className="param-value">{result.soil_parameters.soil_type}</span></div>
                    )}
                    <div className="param-item"><span className="param-label">N</span><span className="param-value">{result.soil_parameters.nitrogen} kg/ha</span></div>
                    <div className="param-item"><span className="param-label">P</span><span className="param-value">{result.soil_parameters.phosphorus} kg/ha</span></div>
                    <div className="param-item"><span className="param-label">K</span><span className="param-value">{result.soil_parameters.potassium} kg/ha</span></div>
                    <div className="param-item"><span className="param-label">pH</span><span className="param-value">{result.soil_parameters.ph}</span></div>
                  </div>
                </div>
                <div className="recommendations">
                  <h3>{t('soil.fertilizers')}</h3>
                  <ul className="fertilizer-list">
                    {result.fertilizer_recommendations.map((f, i) => <li key={i}>{f}</li>)}
                  </ul>
                </div>
                <div className="advisory-section">
                  <h3>{t('common.aiAdvisory')}</h3>
                  <AdvisoryMarkdown content={result.explanation} className="gemini-advisory advisory-content" language={getEffectiveLanguage(user)} />
                </div>
              </motion.div>
            )}
          </div>
        </div>
      </div>
    </AppLayout>
  )
}

export default SoilAnalysis
