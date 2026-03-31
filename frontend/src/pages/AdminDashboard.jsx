import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import { motion, AnimatePresence } from 'framer-motion'

function AdminDashboard() {
  const navigate = useNavigate()
  const [users, setUsers] = useState([])
  const [stats, setStats] = useState({ total: 0, active: 0, inactive: 0, new_today: 0 })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [searchTerm, setSearchTerm] = useState('')

  const adminToken = localStorage.getItem('admin_token')
  const adminUsername = localStorage.getItem('admin_username')

  useEffect(() => {
    if (!adminToken) {
      navigate('/admin/login')
      return
    }
    fetchData()
  }, [adminToken, navigate])

  const fetchData = async () => {
    try {
      setLoading(true)
      const headers = { 'X-Admin-Token': adminToken }
      const [usersRes, statsRes] = await Promise.all([
        axios.get('/api/admin/users', { headers }),
        axios.get('/api/admin/users/stats', { headers })
      ])
      setUsers(usersRes.data)
      setStats(statsRes.data)
    } catch (err) {
      if (err.response?.status === 403) {
        localStorage.removeItem('admin_token')
        navigate('/admin/login')
      }
      setError('Failed to fetch user data')
    } finally {
      setLoading(false)
    }
  }

  const toggleUserStatus = async (userId) => {
    try {
      const headers = { 'X-Admin-Token': adminToken }
      await axios.post(`/api/admin/users/${userId}/toggle-active`, {}, { headers })
      // Update local state instead of refetching all
      setUsers(prev => prev.map(u => u.id === userId ? { ...u, is_active: !u.is_active } : u))
      // Update stats
      setStats(prev => {
        const user = users.find(u => u.id === userId)
        const isTurningActive = !user.is_active
        return {
          ...prev,
          active: isTurningActive ? prev.active + 1 : prev.active - 1,
          inactive: isTurningActive ? prev.inactive - 1 : prev.inactive + 1
        }
      })
    } catch (err) {
      alert('Failed to update user status')
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('admin_token')
    localStorage.removeItem('admin_username')
    navigate('/admin/login')
  }

  const filteredUsers = users.filter(u => 
    u.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
    u.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    u.phone.includes(searchTerm)
  )

  if (!adminToken) return null

  return (
    <div style={{
      minHeight: '100vh',
      background: '#0f172a',
      color: 'white',
      fontFamily: "'Inter', sans-serif",
      padding: '40px 20px',
    }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        {/* Header */}
        <header style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          marginBottom: '40px'
        }}>
          <div>
            <h1 style={{ margin: 0, fontSize: '32px', fontWeight: 800 }}>Admin Dashboard</h1>
            <p style={{ color: '#94a3b8', margin: '4px 0 0' }}>Welcome back, {adminUsername}</p>
          </div>
          <button 
            onClick={handleLogout}
            style={{
              padding: '10px 20px',
              borderRadius: '10px',
              border: '1px solid rgba(239,68,68,0.3)',
              background: 'rgba(239,68,68,0.1)',
              color: '#ef4444',
              cursor: 'pointer',
              fontWeight: 600,
              transition: 'all 0.2s'
            }}
          >
            Logout
          </button>
        </header>

        {/* Stats Grid */}
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
          gap: '20px',
          marginBottom: '40px'
        }}>
          {[
            { label: 'Total Users', value: stats.total, color: '#3b82f6' },
            { label: 'Active', value: stats.active, color: '#10b981' },
            { label: 'Inactive', value: stats.inactive, color: '#ef4444' },
            { label: 'New Today', value: stats.new_today, color: '#8b5cf6' },
          ].map((s, i) => (
            <div key={i} style={{
              background: 'rgba(255,255,255,0.05)',
              padding: '24px',
              borderRadius: '16px',
              border: '1px solid rgba(255,255,255,0.1)'
            }}>
              <p style={{ margin: 0, fontSize: '14px', color: '#94a3b8', fontWeight: 600 }}>{s.label}</p>
              <h3 style={{ margin: '8px 0 0', fontSize: '28px', color: s.color }}>{s.value}</h3>
            </div>
          ))}
        </div>

        {/* User Table Header */}
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          marginBottom: '20px'
        }}>
          <h2 style={{ fontSize: '20px', fontWeight: 700 }}>Management</h2>
          <div style={{ position: 'relative' }}>
            <input 
              type="text" 
              placeholder="Search users..." 
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
              style={{
                background: 'rgba(255,255,255,0.05)',
                border: '1px solid rgba(255,255,255,0.1)',
                borderRadius: '8px',
                padding: '10px 16px',
                color: 'white',
                width: '250px',
                outline: 'none'
              }}
            />
          </div>
        </div>

        {/* User Table */}
        <div style={{ 
          background: 'rgba(255,255,255,0.02)', 
          borderRadius: '16px', 
          border: '1px solid rgba(255,255,255,0.1)',
          overflow: 'hidden'
        }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ background: 'rgba(255,255,255,0.05)' }}>
                <th style={{ padding: '16px', color: '#94a3b8', fontWeight: 600 }}>User</th>
                <th style={{ padding: '16px', color: '#94a3b8', fontWeight: 600 }}>Contact</th>
                <th style={{ padding: '16px', color: '#94a3b8', fontWeight: 600 }}>Location</th>
                <th style={{ padding: '16px', color: '#94a3b8', fontWeight: 600 }}>Joined</th>
                <th style={{ padding: '16px', color: '#94a3b8', fontWeight: 600 }}>Status</th>
                <th style={{ padding: '16px', color: '#94a3b8', fontWeight: 600, textAlign: 'center' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan="6" style={{ padding: '40px', textAlign: 'center', color: '#64748b' }}>Loading records...</td></tr>
              ) : filteredUsers.length === 0 ? (
                <tr><td colSpan="6" style={{ padding: '40px', textAlign: 'center', color: '#64748b' }}>No users found</td></tr>
              ) : (
                filteredUsers.map((u) => (
                  <tr key={u.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                    <td style={{ padding: '16px' }}>
                      <div style={{ fontWeight: 600 }}>{u.name}</div>
                      <div style={{ fontSize: '12px', color: '#64748b' }}>ID: {u.id}</div>
                    </td>
                    <td style={{ padding: '16px' }}>
                      <div style={{ fontSize: '14px' }}>{u.email}</div>
                      <div style={{ fontSize: '14px', color: '#94a3b8' }}>{u.phone}</div>
                    </td>
                    <td style={{ padding: '16px', fontSize: '14px' }}>{u.location}</td>
                    <td style={{ padding: '16px', fontSize: '14px' }}>{new Date(u.created_at).toLocaleDateString()}</td>
                    <td style={{ padding: '16px' }}>
                      <span style={{
                        padding: '4px 8px',
                        borderRadius: '6px',
                        fontSize: '12px',
                        fontWeight: 700,
                        background: u.is_active ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)',
                        color: u.is_active ? '#10b981' : '#f87171'
                      }}>
                        {u.is_active ? 'ACTIVE' : 'INACTIVE'}
                      </span>
                    </td>
                    <td style={{ padding: '16px', textAlign: 'center' }}>
                      <button 
                        onClick={() => toggleUserStatus(u.id)}
                        style={{
                          padding: '6px 14px',
                          borderRadius: '8px',
                          border: 'none',
                          background: u.is_active ? '#ef4444' : '#10b981',
                          color: 'white',
                          cursor: 'pointer',
                          fontWeight: 700,
                          fontSize: '13px',
                          transition: 'all 0.2s',
                          boxShadow: '0 4px 12px rgba(0,0,0,0.2)'
                        }}
                      >
                        {u.is_active ? 'Deactivate' : 'Activate'}
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default AdminDashboard
