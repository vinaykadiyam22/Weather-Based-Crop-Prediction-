import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import axios from 'axios'
import { getEffectiveLanguage } from '../i18n'
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
        language: getEffectiveLanguage(user)
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
                        <div key={i} className="crop-card-enhanced">
                          <div className="crop-image-container">
                            <img 
                              src={crop.image ? `/src/assets/crops/${crop.image}` : `https://placehold.co/400x300/1e40af/ffffff?text=${crop.name}`} 
                              alt={crop.name} 
                              className="crop-image"
                            />
                            <div className="crop-score-badge">{crop.score}/10</div>
                          </div>
                          <div className="crop-info">
                            <h3>{crop.name}</h3>
                            <p className="local-name">{crop.local_name}</p>
                            <div className="crop-details">
                              <div className="detail-item">
                                <span className="param-label">{t('crop.duration')}</span>
                                <span className="param-value">{crop.growing_duration}</span>
                              </div>
                              <div className="detail-item">
                                <span className="param-label">{t('crop.minRainfall')}</span>
                                <span className="param-value">{crop.rainfall_min}mm</span>
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                    <div className="advisory-section" style={{ marginTop: 'var(--space-8)' }}>
                      <h3 style={{ marginBottom: 'var(--space-4)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                        🛡️ {t('common.aiAdvisory')}
                      </h3>
                      <AdvisoryMarkdown content={result.explanation} className="advisory-content" language={getEffectiveLanguage(user)} />
                    </div>

                    {/* Prediction Analysis Section */}
                    {result.analysis_context && (
                      <div className="prediction-analysis" style={{ marginTop: 'var(--space-8)', padding: 'var(--space-6)', background: 'rgba(255,255,255,0.03)', borderRadius: '16px', border: '1px solid rgba(255,255,255,0.08)' }}>
                        <h3 style={{ marginBottom: 'var(--space-4)', fontSize: '18px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                          📊 {t('crop.predictionAnalysis')}
                        </h3>
                        <div className="analysis-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem' }}>
                          <div className="analysis-card" style={{ padding: '1rem', background: 'rgba(255,255,255,0.02)', borderRadius: '12px' }}>
                            <h4 style={{ color: '#94a3b8', fontSize: '12px', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px' }}>{t('crop.soilFactor')}</h4>
                            <p style={{ margin: 0, fontWeight: 600 }}>{result.analysis_context.soil?.soil_type || formData.soil_type}</p>
                            <p style={{ margin: '4px 0 0', fontSize: '13px', color: '#64748b' }}>{t('crop.soilCondition')}: {result.analysis_context.soil?.soil_health || 'Normal'}</p>
                          </div>
                          <div className="analysis-card" style={{ padding: '1rem', background: 'rgba(255,255,255,0.02)', borderRadius: '12px' }}>
                            <h4 style={{ color: '#94a3b8', fontSize: '12px', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px' }}>{t('crop.weatherFactor')}</h4>
                            <p style={{ margin: 0, fontWeight: 600 }}>{result.analysis_context.weather?.season || 'Current Season'}</p>
                            <p style={{ margin: '4px 0 0', fontSize: '13px', color: '#64748b' }}>{t('crop.avgTemp')}: {result.analysis_context.weather?.temperature_c || formData.temperature || '--'}°C</p>
                          </div>
                          <div className="analysis-card" style={{ padding: '1rem', background: 'rgba(255,255,255,0.02)', borderRadius: '12px' }}>
                            <h4 style={{ color: '#94a3b8', fontSize: '12px', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px' }}>{t('crop.marketFactor')}</h4>
                            <p style={{ margin: 0, fontWeight: 600 }}>{t('crop.marketTrendStable')}</p>
                            <p style={{ margin: '4px 0 0', fontSize: '13px', color: '#64748b' }}>{t('crop.marketAnalysisDesc')}</p>
                          </div>
                        </div>
                      </div>
                    )}
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
