import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import { motion } from 'framer-motion'

function AdminLogin() {
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleLogin = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const { data } = await axios.post('/api/admin/login', { username, password })
      localStorage.setItem('admin_token', data.token)
      localStorage.setItem('admin_username', data.username)
      navigate('/admin/dashboard')
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid admin credentials')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      fontFamily: "'Inter', system-ui, sans-serif",
    }}>
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        style={{
          background: 'rgba(255,255,255,0.05)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(255,255,255,0.1)',
          borderRadius: '24px',
          padding: '48px',
          width: '100%',
          maxWidth: '420px',
          boxShadow: '0 24px 64px rgba(0,0,0,0.5)',
        }}
      >
        {/* Logo */}
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <div style={{ fontSize: '48px', marginBottom: '12px' }}>🛡️</div>
          <h1 style={{ margin: 0, fontSize: '24px', fontWeight: 800, color: 'white' }}>Admin Portal</h1>
          <p style={{ margin: '8px 0 0', color: '#94a3b8', fontSize: '14px' }}>Smart Crop Advisory System</p>
        </div>

        {error && (
          <div style={{ background: 'rgba(239,68,68,0.15)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: '10px', padding: '12px 16px', marginBottom: '20px', color: '#fca5a5', fontSize: '13px' }}>
            ⚠️ {error}
          </div>
        )}

        <form onSubmit={handleLogin}>
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: '#94a3b8', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.06em' }}>Username</label>
            <input
              type="text"
              value={username}
              onChange={e => setUsername(e.target.value)}
              placeholder="admin"
              required
              style={{
                width: '100%', padding: '14px 16px', borderRadius: '12px',
                border: '1px solid rgba(255,255,255,0.15)', background: 'rgba(255,255,255,0.08)',
                color: 'white', fontSize: '15px', outline: 'none', boxSizing: 'border-box',
              }}
            />
          </div>
          <div style={{ marginBottom: '28px' }}>
            <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: '#94a3b8', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.06em' }}>Password</label>
            <input
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              style={{
                width: '100%', padding: '14px 16px', borderRadius: '12px',
                border: '1px solid rgba(255,255,255,0.15)', background: 'rgba(255,255,255,0.08)',
                color: 'white', fontSize: '15px', outline: 'none', boxSizing: 'border-box',
              }}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            style={{
              width: '100%', padding: '15px', borderRadius: '12px', border: 'none',
              background: loading ? '#334155' : 'linear-gradient(135deg, #10b981, #059669)',
              color: 'white', fontSize: '15px', fontWeight: 700, cursor: loading ? 'not-allowed' : 'pointer',
              transition: 'all 0.2s',
            }}
          >
            {loading ? 'Signing in…' : '🔐 Sign In as Admin'}
          </button>
        </form>

        <p style={{ textAlign: 'center', marginTop: '24px', fontSize: '13px', color: '#475569' }}>
          ← <a href="/login" style={{ color: '#64748b', textDecoration: 'none' }}>Back to user login</a>
        </p>
      </motion.div>
    </div>
  )
}

export default AdminLogin
