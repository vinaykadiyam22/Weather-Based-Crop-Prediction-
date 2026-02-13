import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import axios from 'axios'
import { motion } from 'framer-motion'
import AppLayout from '../components/AppLayout'
import { FiArrowLeft } from 'react-icons/fi'
import './FeaturePage.css'

const POPULAR = ['Rice', 'Chilli', 'Cotton', 'Groundnut', 'Maize', 'Tomato', 'Onion', 'Turmeric']

function MarketPrices({ user, onLogout, onUserUpdate }) {
  const { t } = useTranslation()
  const [crop, setCrop] = useState('')
  const [prices, setPrices] = useState(null)
  const [seasonData, setSeasonData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [seasonLoading, setSeasonLoading] = useState(true)

  const [district, setDistrict] = useState(user?.location || 'Andhra Pradesh')
  const location = district || 'Andhra Pradesh'

  useEffect(() => {
    if (!location) return
    axios.post('/api/market/season-prices', { location })
      .then(res => setSeasonData(res.data))
      .catch(() => setSeasonData(null))
      .finally(() => setSeasonLoading(false))
  }, [location])

  const search = (name) => {
    const n = name || crop
    if (!n) return
    setLoading(true)
    axios.get(`/api/market/prices/${encodeURIComponent(n)}`, { params: { location } })
      .then(res => setPrices(res.data))
      .catch(() => { setPrices(null); alert('No price data found') })
      .finally(() => setLoading(false))
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    search(crop)
  }

  return (
    <AppLayout user={user} onLogout={onLogout} onUserUpdate={onUserUpdate}>
      <div className="feature-page">
        <div className="container">
          <Link to="/dashboard" className="back-link"><FiArrowLeft size={16} /> {t('common.back')}</Link>
          <div className="page-header">
            <h1 className="page-title">{t('market.title')}</h1>
            <p className="page-subtitle">
              {seasonData
                ? t('market.subtitleSeason', { season: seasonData.season, state: seasonData.state })
                : t('market.subtitleDefault')}
            </p>
            <select className="form-select" style={{ maxWidth: 220, marginTop: 'var(--space-2)' }} value={district} onChange={e => setDistrict(e.target.value)}>
              <option value="Andhra Pradesh">Andhra Pradesh</option>
              <option value="Vijayawada">Vijayawada</option>
              <option value="Guntur">Guntur</option>
              <option value="Visakhapatnam">Visakhapatnam</option>
              <option value="Kurnool">Kurnool</option>
              <option value="Nellore">Nellore</option>
              <option value="Rajahmundry">Rajahmundry</option>
              <option value="Kakinada">Kakinada</option>
            </select>
          </div>

          <div className="feature-content">
            {seasonLoading ? (
              <div className="loading-state"><div className="spinner" /></div>
            ) : seasonData?.crops?.length > 0 && (
              <motion.div className="card" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                <h2 className="section-heading" style={{ marginBottom: 'var(--space-4)' }}>
                  {t('market.seasonCrops', { season: seasonData.season, state: seasonData.state })}
                </h2>
                <div className="market-grid">
                  {seasonData.crops.map((c, i) => (
                    <div key={i} className="market-card">
                      <h3>{c.crop_name}</h3>
                      <div className="market-price">₹{c.latest_price?.toFixed(2) || '—'}/qtl</div>
                      {c.trend && (
                        <span className={`badge badge-${c.trend}`}>
                          {c.trend.toUpperCase()} {c.change_percent !== 0 && `(${c.change_percent > 0 ? '+' : ''}${c.change_percent}%)`}
                        </span>
                      )}
                      <button type="button" className="quick-btn" style={{ marginTop: 'var(--space-2)' }} onClick={() => { setCrop(c.crop_name); search(c.crop_name); }}>
                        {t('market.viewDetails')}
                      </button>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}

            <motion.div className="card" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
              <h3 style={{ marginBottom: 'var(--space-4)' }}>{t('market.searchAnyCrop')}</h3>
              <form onSubmit={handleSubmit} className="search-form">
                <input
                  type="text"
                  className="form-input"
                  value={crop}
                  onChange={e => setCrop(e.target.value)}
                  placeholder={t('market.cropPlaceholder')}
                  list="crops"
                />
                <datalist id="crops">{POPULAR.map(c => <option key={c} value={c} />)}</datalist>
                <button type="submit" className="btn btn-primary" disabled={loading}>
                  {loading ? t('common.searching') : t('common.search')}
                </button>
              </form>
              <div className="quick-links">
                {POPULAR.map(c => (
                  <button key={c} type="button" className="quick-btn" onClick={() => { setCrop(c); search(c); }}>
                    {c}
                  </button>
                ))}
              </div>
            </motion.div>

            {prices && (
              <motion.div className="result-card" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
                <div className="result-header">
                  <h2>{prices.crop_name}</h2>
                  {prices.latest_price && (
                    <span className="param-value">₹{prices.latest_price.toFixed(2)}/quintal</span>
                  )}
                </div>
                {prices.trend && (
                  <div className={`alert ${prices.trend === 'up' ? 'alert-success' : prices.trend === 'down' ? 'alert-danger' : 'alert-info'}`} style={{ marginBottom: 'var(--space-4)' }}>
                    {prices.trend.toUpperCase()} {prices.change_percent !== 0 && `(${prices.change_percent > 0 ? '+' : ''}${prices.change_percent.toFixed(1)}%)`}
                  </div>
                )}
                <h3 style={{ marginBottom: 'var(--space-4)' }}>{t('market.recentPrices')}</h3>
                <div className="grid grid-2">
                  {(prices.prices || []).slice(0, 10).map((p, i) => (
                    <div key={i} className="param-item">
                      <span className="param-label">{p.market}, {p.state}</span>
                      <span className="param-value">₹{p.price.toFixed(2)}</span>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}
          </div>
        </div>
      </div>
    </AppLayout>
  )
}

export default MarketPrices
