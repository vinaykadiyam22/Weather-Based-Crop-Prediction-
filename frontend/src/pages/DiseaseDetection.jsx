import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { getEffectiveLanguage } from '../i18n'
import { useDropzone } from 'react-dropzone'
import axios from 'axios'
import { motion } from 'framer-motion'
import AppLayout from '../components/AppLayout'
import AdvisoryMarkdown from '../components/AdvisoryMarkdown'
import { FiArrowLeft } from 'react-icons/fi'
import './FeaturePage.css'

function DiseaseDetection({ user, onLogout, onUserUpdate }) {
  const { t } = useTranslation()
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
    }
  })

  const handleAnalyze = async () => {
    if (!image) { setError(t('disease.uploadFirst')); return }
    setLoading(true)
    setError('')
    try {
      const fd = new FormData()
      fd.append('image', image)
      fd.append('user_id', user?.id || '')
      fd.append('language', getEffectiveLanguage(user))
      fd.append('send_email', 'true')
      const res = await axios.post('/api/disease/detect', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
      setResult(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Analysis failed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <AppLayout user={user} onLogout={onLogout} onUserUpdate={onUserUpdate}>
      <div className="feature-page">
        <div className="container">
          <Link to="/dashboard" className="back-link"><FiArrowLeft size={16} /> {t('common.back')}</Link>
          <div className="page-header">
            <h1 className="page-title">{t('disease.title')}</h1>
            <p className="page-subtitle">{t('disease.subtitle')}</p>
          </div>

          <div className="feature-content">
            <motion.div
              className="card"
              {...getRootProps()}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              style={{ cursor: 'pointer' }}
            >
              <input {...getInputProps()} />
              {preview ? (
                <div className="dropzone-content">
                  <img src={preview} alt="Preview" className="preview-image" />
                  <p className="dropzone-text">{t('disease.clickReplace')}</p>
                </div>
              ) : (
                <div className={`dropzone ${isDragActive ? 'active' : ''}`}>
                  <div className="dropzone-content">
                    <div className="dropzone-icon">📸</div>
                    <p className="dropzone-text">{isDragActive ? t('disease.dropHere') : t('disease.dragDrop')}</p>
                    <p className="dropzone-hint">{t('disease.jpgPng')}</p>
                  </div>
                </div>
              )}
            </motion.div>

            {image && !result && (
              <button onClick={handleAnalyze} className="btn btn-primary btn-lg" disabled={loading}>
                {loading ? t('disease.analyzing') : t('disease.analyze')}
              </button>
            )}

            {error && <div className="alert alert-danger">{error}</div>}

            {result && (
              <motion.div className="result-card" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
                <div className={`result-header ${result.is_healthy ? 'healthy' : 'diseased'}`}>
                  <h2>{result.is_healthy ? t('disease.healthyCrop') : t('disease.diseaseDetected')}</h2>
                  <span className="btn btn-secondary" style={{ border: 'none' }}>{(result.confidence * 100).toFixed(1)}% {t('common.confidence')}</span>
                </div>
                <div className="param-item" style={{ marginBottom: 'var(--space-4)' }}>
                  <span className="param-label">{t('disease.detectedCrop')}</span>
                  <span className="param-value">{result.crop_name || '—'}</span>
                </div>
                {!result.is_healthy && (
                  <div className="param-item" style={{ marginBottom: 'var(--space-4)' }}>
                    <span className="param-label">{t('disease.identifiedCondition')}</span>
                    <span className="param-value">{result.disease_name}</span>
                  </div>
                )}
                <div className="param-item" style={{ marginBottom: 'var(--space-4)' }}>
                  <span className="param-label">{t('disease.predictionAccuracy')}</span>
                  <span className="param-value">{(result.confidence * 100).toFixed(1)}%</span>
                </div>
                <div className="advisory-section">
                  <h3>{t('common.aiAdvisory')}</h3>
                  <AdvisoryMarkdown content={result.advisory} className="advisory-content" language={getEffectiveLanguage(user)} />
                </div>
                <button onClick={() => { setResult(null); setImage(null); setPreview(null); }} className="btn btn-outline" style={{ marginTop: 'var(--space-6)' }}>
                  {t('disease.analyzeAnother')}
                </button>
              </motion.div>
            )}
          </div>
        </div>
      </div>
    </AppLayout>
  )
}

export default DiseaseDetection
