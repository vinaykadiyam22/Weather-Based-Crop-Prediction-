import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useTranslation } from 'react-i18next'
import { FiCloudRain, FiTrendingUp, FiDroplet, FiActivity, FiDollarSign, FiGlobe } from 'react-icons/fi'
import i18n, { SUPPORTED_LANGS, setStoredLanguage } from '../i18n'
import './Landing.css'

const fadeUp = { initial: { opacity: 0, y: 24 }, animate: { opacity: 1, y: 0 }, transition: { duration: 0.5 } }

function FeatureCard({ icon: Icon, title, description, delay }) {
  return (
    <motion.div
      className="feature-card"
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-50px" }}
      transition={{ duration: 0.4, delay }}
      whileHover={{ y: -4, transition: { duration: 0.2 } }}
    >
      <div className="feature-card-icon">
        {Icon && <Icon size={24} />}
      </div>
      <h3 className="feature-card-title">{title}</h3>
      <p className="feature-card-desc">{description}</p>
    </motion.div>
  )
}

function Landing() {
  const { t } = useTranslation()
  const currentLang = typeof window !== 'undefined' ? localStorage.getItem('app_language') || 'en' : 'en'

  const handleLanguageChange = (lang) => {
    setStoredLanguage(lang)
    i18n.changeLanguage(lang)
  }

  return (
    <div className="landing">
      <div className="landing-bg" aria-hidden="true" />

      <header className="landing-header">
        <div className="container">
          <div className="header-inner">
            <span className="logo">🌾 {t('brand')}</span>
            <nav className="header-nav">
              <select className="lang-select-inline" value={currentLang} onChange={(e) => handleLanguageChange(e.target.value)} aria-label={t('common.language')}>
                {SUPPORTED_LANGS.map((l) => <option key={l.code} value={l.code}>{l.label}</option>)}
              </select>
              <Link to="/about" className="btn btn-secondary">{t('nav.about')}</Link>
              <Link to="/login" className="btn btn-secondary">{t('nav.login')}</Link>
              <Link to="/register" className="btn btn-primary">{t('nav.getStarted')}</Link>
            </nav>
          </div>
        </div>
      </header>

      <section className="hero">
        <div className="container">
          <motion.div
            className="hero-content"
            initial={{ opacity: 0, y: 32 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <h1 className="hero-title">{t('landing.title')}</h1>
            <p className="hero-subtitle">{t('landing.subtitle')}</p>
            <div className="hero-actions">
              <Link to="/register" className="btn btn-primary btn-lg">{t('landing.startFree')}</Link>
              <Link to="/login" className="btn btn-outline btn-lg">{t('landing.signIn')}</Link>
            </div>
          </motion.div>
        </div>
      </section>

      <section className="features">
        <div className="container">
          <motion.h2 className="section-title" initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }}>
            {t('landing.everythingYouNeed')}
          </motion.h2>
          <div className="features-grid">
            <FeatureCard icon={FiCloudRain} title={t('landing.apLiveWeather')} description={t('landing.apLiveWeatherDesc')} delay={0} />
            <FeatureCard icon={FiDroplet} title={t('landing.soilAnalysis')} description={t('landing.soilAnalysisDesc')} delay={0.05} />
            <FeatureCard icon={FiActivity} title={t('landing.cropRecommendations')} description={t('landing.cropRecommendationsDesc')} delay={0.1} />
            <FeatureCard icon={FiTrendingUp} title={t('landing.diseaseDetection')} description={t('landing.diseaseDetectionDesc')} delay={0.15} />
            <FeatureCard icon={FiDollarSign} title={t('landing.apMandiPrices')} description={t('landing.apMandiPricesDesc')} delay={0.2} />
            <FeatureCard icon={FiGlobe} title={t('landing.multilingual')} description={t('landing.multilingualDesc')} delay={0.25} />
          </div>
        </div>
      </section>

      <section className="cta">
        <div className="container">
          <motion.div className="cta-card" initial={{ opacity: 0, y: 24 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}>
            <h2>{t('landing.ctaTitle')}</h2>
            <p>{t('landing.ctaSubtitle')}</p>
            <Link to="/register" className="btn btn-primary btn-lg">{t('landing.createAccount')}</Link>
          </motion.div>
        </div>
      </section>

      <footer className="landing-footer">
        <div className="container">
          <p>{t('landing.copyright')}</p>
        </div>
      </footer>
    </div>
  )
}

export default Landing
