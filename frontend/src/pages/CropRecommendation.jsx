import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import axios from 'axios'
import { motion } from 'framer-motion'
import AppLayout from '../components/AppLayout'
import AdvisoryMarkdown from '../components/AdvisoryMarkdown'
import { FiArrowLeft } from 'react-icons/fi'
import './FeaturePage.css'

function CropRecommendation({ user, onLogout, onUserUpdate }) {
  const { t } = useTranslation()
  const [formData, setFormData] = useState({
    soil_type: '',
    location: user.location || '',
    season: '',
    temperature: ''
  })
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const res = await axios.post('/api/crop/recommend', {
        ...formData,
        temperature: formData.temperature ? parseFloat(formData.temperature) : null,
        user_id: user?.id || null,
        language: user?.language || 'en'
      })
      setResult(res.data)
    } catch {
      alert('Error getting recommendations. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <AppLayout user={user} onLogout={onLogout} onUserUpdate={onUserUpdate}>
      <div className="feature-page">
        <div className="container">
          <Link to="/dashboard" className="back-link"><FiArrowLeft size={16} /> {t('common.backToDashboard')}</Link>
          <div className="page-header">
            <h1 className="page-title">{t('crop.title')}</h1>
            <p className="page-subtitle">{t('crop.subtitle')}</p>
          </div>

          <div className="feature-content">
            {!result ? (
              <motion.div className="card" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                <form onSubmit={handleSubmit}>
                  <div className="form-group">
                    <label className="form-label">{t('crop.soilType')}</label>
                    <select className="form-select" value={formData.soil_type} onChange={e => setFormData({ ...formData, soil_type: e.target.value })} required>
                      <option value="">{t('common.select')}</option>
                      {['Clay', 'Sandy', 'Loamy', 'Silty', 'Red Soil', 'Black Soil', 'Alluvial'].map(s => <option key={s} value={s}>{s}</option>)}
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">{t('crop.location')}</label>
                    <input type="text" className="form-input" value={formData.location} onChange={e => setFormData({ ...formData, location: e.target.value })} placeholder={t('crop.locationPlaceholder')} required />
                  </div>
                  <div className="form-group">
                    <label className="form-label">{t('crop.season')}</label>
                    <select className="form-select" value={formData.season} onChange={e => setFormData({ ...formData, season: e.target.value })}>
                      <option value="">{t('crop.seasonOptional')}</option>
                      <option value="Kharif">{t('seasons.kharif')}</option>
                      <option value="Rabi">{t('seasons.rabi')}</option>
                      <option value="Summer">{t('seasons.summer')}</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">{t('crop.temperature')}</label>
                    <input type="number" className="form-input" value={formData.temperature} onChange={e => setFormData({ ...formData, temperature: e.target.value })} placeholder={t('common.optional')} />
                  </div>
                  <button type="submit" className="btn btn-primary btn-lg" disabled={loading}>
                    {loading ? t('crop.gettingRecommendations') : t('crop.getRecommendations')}
                  </button>
                </form>
              </motion.div>
            ) : (
              <motion.div className="result-card" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
                <h2>{t('crop.recommendedCrops')}</h2>
                {result.recommended_crops.length > 0 ? (
                  <>
                    <div className="crops-grid" style={{ marginTop: 'var(--space-6)' }}>
                      {result.recommended_crops.map((crop, i) => (
                        <div key={i} className="crop-card">
                          <h3>{crop.name}</h3>
                          <p className="local-name" style={{ color: 'var(--color-text-tertiary)', fontSize: 'var(--text-sm)' }}>{crop.local_name}</p>
                          <div className="crop-details">
                            <div><span className="param-label">{t('crop.duration')}</span><br /><span className="param-value">{crop.growing_duration}</span></div>
                            <div><span className="param-label">{t('crop.minRainfall')}</span><br /><span className="param-value">{crop.rainfall_min}mm</span></div>
                          </div>
                        </div>
                      ))}
                    </div>
                    <div className="advisory-section" style={{ marginTop: 'var(--space-6)' }}>
                      <h3>{t('common.aiAdvisory')}</h3>
                      <AdvisoryMarkdown content={result.explanation} className="advisory-content" language={user?.language} />
                    </div>
                  </>
                ) : (
                  <p style={{ marginTop: 'var(--space-4)' }}>{t('crop.noRecommendations')}</p>
                )}
                <button onClick={() => setResult(null)} className="btn btn-outline" style={{ marginTop: 'var(--space-6)' }}>{t('crop.tryDifferent')}</button>
              </motion.div>
            )}
          </div>
        </div>
      </div>
    </AppLayout>
  )
}

export default CropRecommendation
