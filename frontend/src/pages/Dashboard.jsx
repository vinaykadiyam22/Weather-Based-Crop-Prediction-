import { Link } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import axios from 'axios'
import { motion } from 'framer-motion'
import AppLayout from '../components/AppLayout'
import InteractiveMap from '../components/InteractiveMap'
import { FiDroplet, FiCloudRain, FiActivity, FiMapPin, FiTrendingUp } from 'react-icons/fi'
import './Dashboard.css'

function Dashboard({ user, onLogout, onUserUpdate }) {
  const { t } = useTranslation()
  const FEATURES = [
    { icon: FiDroplet, title: t('dashboard.soilAnalysis'), path: '/soil-analysis', desc: t('dashboard.soilAnalysisDesc') },
    { icon: FiActivity, title: t('dashboard.cropRecommendation'), path: '/crop-recommendation', desc: t('dashboard.cropRecommendationDesc') },
    { icon: FiCloudRain, title: t('dashboard.weatherAlerts'), path: '/weather', desc: t('dashboard.weatherAlertsDesc') },
    { icon: FiActivity, title: t('dashboard.diseaseDetection'), path: '/disease-detection', desc: t('dashboard.diseaseDetectionDesc') },
    { icon: FiMapPin, title: t('dashboard.soilType'), path: '/soil-detection', desc: t('dashboard.soilTypeDesc') },
    { icon: FiTrendingUp, title: t('dashboard.marketPrices'), path: '/market-prices', desc: t('dashboard.marketPricesDesc') },
  ]
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const res = await axios.get(`/api/weather/alerts/user/${user.id}?unread_only=true&limit=3`)
        const data = res.data
        setAlerts(Array.isArray(data) ? data : (data?.alerts || []))
      } catch {
        setAlerts([])
      } finally {
        setLoading(false)
      }
    }
    fetchAlerts()
  }, [user.id])

  return (
    <AppLayout user={user} onLogout={onLogout} onUserUpdate={onUserUpdate}>
      <div className="dashboard">
        <div className="container">
          <motion.div
            className="dashboard-hero"
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
          >
            <h1 className="dashboard-title">{t('dashboard.welcome', { name: user.name })}</h1>
            <p className="dashboard-subtitle">{user.location}</p>
            <p className="dashboard-tip">{t('dashboard.tip')}</p>
          </motion.div>

          <section className="map-section" style={{ margin: '2rem 0' }}>
            <h2 className="section-heading" style={{ marginBottom: '1rem' }}>{t('dashboard.regionAnalytics')}</h2>
            <InteractiveMap />
          </section>

          {alerts.length > 0 && (
            <motion.section
              className="alerts-section"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
            >
              <h2 className="section-heading">{t('dashboard.activeAlerts')}</h2>
              <div className="alerts-grid">
                {alerts.map((alert) => (
                  <Link
                    key={alert.id}
                    to={`/alert/${alert.id}`}
                    className={`alert-card severity-${alert.severity}`}
                  >
                    <span className="alert-badge">{alert.severity}</span>
                    <h3>{alert.title}</h3>
                    <p>{alert.description}</p>
                  </Link>
                ))}
              </div>
            </motion.section>
          )}

          <section className="features-section">
            <h2 className="section-heading">{t('dashboard.tools')}</h2>
            <div className="features-grid">
              {FEATURES.map((feat, i) => (
                <motion.div
                  key={feat.path}
                  initial={{ opacity: 0, y: 16 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 + i * 0.05 }}
                >
                  <Link to={feat.path} className="feature-card">
                    <div className="feature-icon">
                      <feat.icon size={24} />
                    </div>
                    <h3>{feat.title}</h3>
                    <p>{feat.desc}</p>
                  </Link>
                </motion.div>
              ))}
            </div>
          </section>
        </div>
      </div>
    </AppLayout>
  )
}

export default Dashboard
