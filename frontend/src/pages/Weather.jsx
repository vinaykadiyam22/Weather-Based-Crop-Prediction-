import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import axios from 'axios'
import { motion } from 'framer-motion'
import AppLayout from '../components/AppLayout'
import { FiArrowLeft } from 'react-icons/fi'
import './FeaturePage.css'

const AP_DISTRICTS = ['Vijayawada', 'Visakhapatnam', 'Guntur', 'Kurnool', 'Nellore', 'Rajahmundry', 'Tirupati', 'Kakinada', 'Anantapur', 'Eluru', 'Ongole', 'Kadapa', 'Andhra Pradesh']

function Weather({ user, onLogout, onUserUpdate }) {
  const { t } = useTranslation()
  const [weather, setWeather] = useState(null)
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [district, setDistrict] = useState(user?.location || 'Andhra Pradesh')

  useEffect(() => {
    const loc = district || 'Andhra Pradesh'
    const load = async () => {
      try {
        const [wRes, syncRes] = await Promise.all([
          axios.post('/api/weather/current', { location: loc }),
          axios.post('/api/weather/sync-alerts', { user_id: user.id, location: loc }).catch(() => ({ data: { alerts: [] } }))
        ])
        setWeather(wRes.data)
        setAlerts(syncRes.data?.alerts || [])
      } catch {
        setAlerts([])
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [district, user.location, user.id])

  if (loading) {
    return (
      <AppLayout user={user} onLogout={onLogout} onUserUpdate={onUserUpdate}>
        <div className="loading-state"><div className="spinner" /></div>
      </AppLayout>
    )
  }

  return (
    <AppLayout user={user} onLogout={onLogout} onUserUpdate={onUserUpdate}>
      <div className="feature-page">
        <div className="container">
          <Link to="/dashboard" className="back-link"><FiArrowLeft size={16} /> {t('common.backToDashboard')}</Link>
          <div className="page-header">
            <h1 className="page-title">{t('weather.title')}</h1>
            <p className="page-subtitle">
              {t('weather.liveFor', { district })}
              <span className="live-badge" title="Real-time data from Open-Meteo"> {t('weather.liveBadge')}</span>
            </p>
            <select className="form-select" style={{ maxWidth: 220, marginTop: 'var(--space-2)' }} value={district} onChange={e => setDistrict(e.target.value)}>
              {AP_DISTRICTS.map(d => <option key={d} value={d}>{d}</option>)}
            </select>
          </div>

          <div className="feature-content">
            {weather?.main && (
              <motion.div
                className="weather-card"
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
              >
                <div className="weather-main">
                  <div className="temp-display">{Math.round(weather.main.temp)}°C</div>
                  <div className="weather-desc">{weather.weather?.[0]?.description || 'Clear'}</div>
                </div>
                <div className="weather-details">
                  <div className="detail-item"><span className="param-label">{t('weather.humidity')}</span><span className="param-value">{weather.main.humidity}%</span></div>
                  <div className="detail-item"><span className="param-label">{t('weather.wind')}</span><span className="param-value">{(weather.wind?.speed * 3.6 || 0).toFixed(1)} km/h</span></div>
                  <div className="detail-item"><span className="param-label">{t('weather.feelsLike')}</span><span className="param-value">{Math.round(weather.main.feels_like)}°C</span></div>
                </div>
              </motion.div>
            )}

            {alerts.length > 0 ? (
              <div>
                <h2 className="section-heading" style={{ marginBottom: 'var(--space-4)' }}>{t('weather.activeAlerts')}</h2>
                <div className="alerts-grid">
                  {alerts.map((alert, i) => (
                    <div key={i} className={`alert-card severity-${alert.severity}`}>
                      <span className="alert-badge">{alert.severity}</span>
                      <h3>{alert.title}</h3>
                      <p>{alert.description}</p>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="card" style={{ textAlign: 'center', padding: 'var(--space-12)' }}>
                <p style={{ color: 'var(--color-text-secondary)' }}>{t('weather.noAlerts')}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </AppLayout>
  )
}

export default Weather
