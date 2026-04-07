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
      <div className="dashboard-social">
        <div className="container">
          <motion.div
            className="social-status-card"
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
          >
             <div className="user-avatar-circle">🌱</div>
             <div className="status-input-trigger">
                {t('dashboard.welcome', { name: user.name.split(' ')[0] })}! Check your latest agricultural updates...
             </div>
          </motion.div>

          <div className="social-feed">
             {/* Weather Feed Item */}
             <motion.div className="feed-item" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.1 }}>
                <div className="feed-header">
                   <FiCloudRain className="feed-icon weather" />
                   <div>
                      <h3 className="feed-title">{t('dashboard.weatherAlerts')}</h3>
                      <p className="feed-meta">{user.location} • Live Now</p>
                   </div>
                </div>
                <div className="feed-body">
                   <p>{t('dashboard.weatherAlertsDesc')}</p>
                   <Link to="/weather" className="feed-cta">{t('common.view')}</Link>
                </div>
             </motion.div>

             {/* Market Feed Item */}
             <motion.div className="feed-item" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}>
                <div className="feed-header">
                   <FiTrendingUp className="feed-icon market" />
                   <div>
                      <h3 className="feed-title">{t('dashboard.marketPrices')}</h3>
                      <p className="feed-meta">Current Season</p>
                   </div>
                </div>
                <div className="feed-body">
                   <p>{t('dashboard.marketPricesDesc')}</p>
                   <Link to="/market-prices" className="feed-cta blue">{t('common.view')}</Link>
                </div>
             </motion.div>

             {/* Tools Feed Item */}
             <motion.div className="feed-item" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }}>
                <div className="feed-header">
                   <FiActivity className="feed-icon tools" />
                   <div>
                      <h3 className="feed-title">{t('dashboard.tools')}</h3>
                      <p className="feed-meta">AI-Powered Analysis</p>
                   </div>
                </div>
                <div className="feed-body tools-list">
                    <Link to="/crop-recommendation" className="tool-chip">{t('dashboard.cropRecommendation')}</Link>
                    <Link to="/soil-analysis" className="tool-chip">{t('dashboard.soilAnalysis')}</Link>
                    <Link to="/disease-detection" className="tool-chip">{t('dashboard.diseaseDetection')}</Link>
                </div>
             </motion.div>
          </div>
          
          <section className="map-section-social">
            <h2 className="section-heading">{t('dashboard.regionAnalytics')}</h2>
            <div className="social-card-map">
               <InteractiveMap />
            </div>
          </section>
        </div>
      </div>
    </AppLayout>
  )
}

export default Dashboard
