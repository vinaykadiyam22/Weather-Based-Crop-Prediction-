import { useParams, Link } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { getEffectiveLanguage } from '../i18n'
import axios from 'axios'
import { motion } from 'framer-motion'
import AppLayout from '../components/AppLayout'
import AdvisoryMarkdown from '../components/AdvisoryMarkdown'
import { FiArrowLeft } from 'react-icons/fi'
import './FeaturePage.css'

function AlertDetail({ user, onLogout, onUserUpdate }) {
  const { t } = useTranslation()
  const { id } = useParams()
  const [alert, setAlert] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    axios.get(`/api/weather/alerts/user/${user.id}`)
      .then(res => {
        const data = res.data
        const list = Array.isArray(data) ? data : (data?.alerts || [])
        const found = list.find(a => a.id === parseInt(id))
        if (found) {
          setAlert(found)
          axios.put(`/api/weather/alerts/${id}/read`)
        }
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [id, user.id])

  if (loading) {
    return (
      <AppLayout user={user} onLogout={onLogout} onUserUpdate={onUserUpdate}>
        <div className="loading-state"><div className="spinner" /></div>
      </AppLayout>
    )
  }

  if (!alert) {
    return (
      <AppLayout user={user} onLogout={onLogout} onUserUpdate={onUserUpdate}>
        <div className="container">
          <Link to="/dashboard" className="back-link"><FiArrowLeft size={16} /> {t('common.back')}</Link>
          <p>{t('alert.alertNotFound')}</p>
        </div>
      </AppLayout>
    )
  }

  return (
    <AppLayout user={user} onLogout={onLogout} onUserUpdate={onUserUpdate}>
      <div className="feature-page">
        <div className="container">
          <Link to="/dashboard" className="back-link"><FiArrowLeft size={16} /> {t('common.back')}</Link>
          <motion.div
            className="result-card"
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <div className="result-header">
              <h1>{alert.title}</h1>
              <span className={`btn btn-secondary severity-${alert.severity}`} style={{ border: 'none', textTransform: 'uppercase' }}>
                {alert.severity}
              </span>
            </div>
            <div className="alert-section" style={{ marginTop: 'var(--space-6)' }}>
              <h2 style={{ marginBottom: 'var(--space-2)' }}>{t('alert.whatsHappening')}</h2>
              <p>{alert.description}</p>
            </div>
            {alert.recommendations && (
              <div className="advisory-section" style={{ marginTop: 'var(--space-6)' }}>
                <h3>{t('common.aiAdvisory')}</h3>
                <AdvisoryMarkdown content={alert.recommendations} className="advisory-content" language={getEffectiveLanguage(user)} />
              </div>
            )}
            <p style={{ marginTop: 'var(--space-6)', fontSize: 'var(--text-sm)', color: 'var(--color-text-tertiary)' }}>
              {new Date(alert.created_at).toLocaleString()}
            </p>
          </motion.div>
        </div>
      </div>
    </AppLayout>
  )
}

export default AlertDetail
