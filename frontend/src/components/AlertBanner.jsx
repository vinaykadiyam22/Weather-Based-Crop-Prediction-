import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import axios from 'axios'
import { motion, AnimatePresence } from 'framer-motion'
import { FiAlertTriangle, FiX } from 'react-icons/fi'
import './AlertBanner.css'

function AlertBanner({ user }) {
  const { t } = useTranslation()
  const [alerts, setAlerts] = useState([])
  const [dismissed, setDismissed] = useState([])

  useEffect(() => {
    if (!user?.id) return
    const fetch = async () => {
      try {
        const res = await axios.get(`/api/weather/alerts/${user.id}`)
        const data = res.data
        const list = Array.isArray(data) ? data : (data?.alerts || [])
        const recent = list.filter(a => {
          const d = new Date(a.created_at)
          const hours = (Date.now() - d) / (1000 * 60 * 60)
          return hours < 24 && !dismissed.includes(a.id)
        })
        setAlerts(recent)
      } catch {
        setAlerts([])
      }
    }
    fetch()
    const id = setInterval(fetch, 5 * 60 * 1000)
    return () => clearInterval(id)
  }, [user?.id, dismissed])

  const dismiss = (id) => {
    setDismissed(prev => [...prev, id])
    setAlerts(prev => prev.filter(a => a.id !== id))
  }

  if (alerts.length === 0) return null

  return (
    <div className="alert-banner-wrap">
      <AnimatePresence>
        {alerts.map(alert => (
          <motion.div
            key={alert.id}
            className={`alert-banner severity-${alert.severity}`}
            initial={{ opacity: 0, y: -16 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -16 }}
          >
            <div className="alert-banner-inner">
              <FiAlertTriangle className="alert-banner-icon" size={20} />
              <div className="alert-banner-text">
                <strong>{alert.title}</strong>
                <span>{alert.message || alert.description}</span>
              </div>
              <div className="alert-banner-actions">
                <Link to={`/alert/${alert.id}`} className="alert-banner-link">{t('alert.view')}</Link>
                <button onClick={() => dismiss(alert.id)} className="alert-banner-dismiss" aria-label="Dismiss">
                  <FiX size={18} />
                </button>
              </div>
            </div>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  )
}

export default AlertBanner
