import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { getEffectiveLanguage } from '../i18n'
import { useDropzone } from 'react-dropzone'
import axios from 'axios'
import { motion } from 'framer-motion'
import AppLayout from '../components/AppLayout'
import AdvisoryMarkdown from '../components/AdvisoryMarkdown'
import { FiArrowLeft, FiImage, FiList } from 'react-icons/fi'
import './FeaturePage.css'

const SOIL_TYPES = ['Clay', 'Sandy', 'Loamy', 'Silty', 'Peaty', 'Chalky', 'Red Soil', 'Black Soil', 'Alluvial']

function SoilTypeDetection({ user, onLogout, onUserUpdate }) {
  const { t } = useTranslation()
  const [mode, setMode] = useState('manual') // 'manual' | 'image'
  const [selectedSoilType, setSelectedSoilType] = useState('')
  const [location, setLocation] = useState(user?.location || '')
  const [image, setImage] = useState(null)
  const [preview, setPreview] = useState(null)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: { 'image/*': ['.jpeg', '.jpg', '.png'] },
    maxFiles: 1,
    onDrop: (files) => {
      const f = files[0]
      setImage(f)
      setPreview(f ? URL.createObjectURL(f) : null)
      setResult(null)
      setError('')
    },
  })

  const handleSelect = async () => {
    if (!selectedSoilType) { setError(t('soilType.selectSoilFirst')); return }
    setLoading(true)
    setError('')
    try {
      const res = await axios.post('/api/soil/select-type', { user_id: user.id, soil_type: selectedSoilType, location, language: getEffectiveLanguage(user) })
      setResult(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to get soil information')
    } finally {
      setLoading(false)
    }
  }

  const handleAnalyze = async () => {
    if (!image) { setError(t('soilType.uploadSoilFirst')); return }
    setLoading(true)
    setError('')
    try {
      const fd = new FormData()
      fd.append('image', image)
      fd.append('user_id', user?.id || '')
      fd.append('language', getEffectiveLanguage(user))
      fd.append('location', location)
      const res = await axios.post('/api/soil/detect-from-image', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
      setResult(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Soil detection failed.')
    } finally {
      setLoading(false)
    }
  }

  const formatCharacteristics = (ch) => {
    if (!ch) return {}
    const out = { ...ch }
    if (Array.isArray(out.best_for)) out.best_for = out.best_for.join(', ')
    return out
  }

  return (
    <AppLayout user={user} onLogout={onLogout} onUserUpdate={onUserUpdate}>
      <div className="feature-page">
        <div className="container">
          <Link to="/dashboard" className="back-link"><FiArrowLeft size={16} /> {t('common.back')}</Link>
          <div className="page-header">
            <h1 className="page-title">{t('soilType.title')}</h1>
            <p className="page-subtitle">{t('soilType.subtitle')}</p>
          </div>

          <div className="feature-content">
            <div className="mode-tabs" style={{ display: 'flex', gap: 'var(--space-3)', marginBottom: 'var(--space-6)' }}>
              <button
                type="button"
                className={`btn ${mode === 'manual' ? 'btn-primary' : 'btn-outline'}`}
                onClick={() => { setMode('manual'); setResult(null); setError(''); }}
              >
                <FiList size={16} style={{ marginRight: 6, verticalAlign: 'middle' }} />
                {t('soilType.selectManually')}
              </button>
              <button
                type="button"
                className={`btn ${mode === 'image' ? 'btn-primary' : 'btn-outline'}`}
                onClick={() => { setMode('image'); setResult(null); setError(''); setImage(null); setPreview(null); }}
              >
                <FiImage size={16} style={{ marginRight: 6, verticalAlign: 'middle' }} />
                {t('soilType.uploadImage')}
              </button>
            </div>

            {mode === 'manual' ? (
              <motion.div className="card" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                <h2 style={{ marginBottom: 'var(--space-6)' }}>{t('soilType.selectSoilType')}</h2>
                <div className="form-group">
                  <label className="form-label">{t('soil.soilType')}</label>
                  <select className="form-control" value={selectedSoilType} onChange={e => setSelectedSoilType(e.target.value)} disabled={loading}>
                    <option value="">— {t('common.select')} —</option>
                    {SOIL_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
                  </select>
                </div>
                <div className="form-group">
                  <label className="form-label">{t('soil.location')}</label>
                  <input type="text" className="form-control" value={location} onChange={e => setLocation(e.target.value)} placeholder={t('common.optional')} disabled={loading} />
                </div>
                {error && <div className="alert alert-danger">{error}</div>}
                <button onClick={handleSelect} className="btn btn-primary btn-lg" disabled={loading || !selectedSoilType}>
                  {loading ? t('soilType.loading') : t('soilType.getInformation')}
                </button>
              </motion.div>
            ) : (
              <>
                <motion.div className="card" {...getRootProps()} initial={{ opacity: 0 }} animate={{ opacity: 1 }} style={{ cursor: 'pointer' }}>
                  <input {...getInputProps()} />
                  {preview ? (
                    <div className="dropzone-content">
                      <img src={preview} alt="Soil preview" className="preview-image" />
                      <p className="dropzone-text">{t('disease.clickReplace')}</p>
                    </div>
                  ) : (
                    <div className={`dropzone ${isDragActive ? 'active' : ''}`}>
                      <div className="dropzone-content">
                        <div className="dropzone-icon">🪨</div>
                        <p className="dropzone-text">{isDragActive ? t('disease.dropHere') : t('soilType.dragDropSoil')}</p>
                        <p className="dropzone-hint">{t('disease.jpgPng')}</p>
                      </div>
                    </div>
                  )}
                </motion.div>
                {image && (
                  <div className="form-group">
                    <label className="form-label">{t('soil.location')}</label>
                    <input type="text" className="form-control" value={location} onChange={e => setLocation(e.target.value)} placeholder={t('common.optional')} disabled={loading} />
                  </div>
                )}
                {image && !result && (
                  <button onClick={handleAnalyze} className="btn btn-primary btn-lg" disabled={loading}>
                    {loading ? t('disease.analyzing') : t('soilType.detectSoilType')}
                  </button>
                )}
                {error && <div className="alert alert-danger">{error}</div>}
              </>
            )}

            {result && (
              <motion.div className="result-card" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
                <h2>Soil Type: {result.soil_type}</h2>
                {result.confidence && (
                  <p style={{ color: 'var(--color-text-secondary)', marginBottom: 'var(--space-4)' }}>
                    {t('common.confidence')}: {(result.confidence * 100).toFixed(1)}%
                  </p>
                )}
                <div className="soil-characteristics" style={{ marginTop: 'var(--space-6)' }}>
                  <h3>{t('soilType.characteristics')}</h3>
                  <div className="characteristics-grid">
                    {Object.entries(formatCharacteristics(result.characteristics)).map(([k, v]) => (
                      <div key={k} className="characteristic-item">
                        <span className="char-label">{k.replace(/_/g, ' ')}</span>
                        <span className="char-value">{Array.isArray(v) ? v.join(', ') : v}</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="advisory-section" style={{ marginTop: 'var(--space-6)' }}>
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

export default SoilTypeDetection
