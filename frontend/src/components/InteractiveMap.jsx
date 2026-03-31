import { useEffect, useRef, useState, useCallback } from 'react';
import axios from 'axios';

// ─── Leaflet CDN loader ───────────────────────────────────────────────────────
function loadLeafletFromCDN() {
  return new Promise((resolve) => {
    if (window.L) { resolve(window.L); return; }
    if (!document.querySelector('#leaflet-css')) {
      const link = document.createElement('link');
      link.id = 'leaflet-css'; link.rel = 'stylesheet';
      link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
      document.head.appendChild(link);
    }
    if (!document.querySelector('#leaflet-js')) {
      const script = document.createElement('script');
      script.id = 'leaflet-js';
      script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
      script.onload = () => resolve(window.L);
      document.body.appendChild(script);
    } else {
      const iv = setInterval(() => { if (window.L) { clearInterval(iv); resolve(window.L); } }, 100);
    }
  });
}

// ─── Info Panel ───────────────────────────────────────────────────────────────
const Row = ({ icon, label, value }) => (
  <div style={{ display: 'flex', justifyContent: 'space-between', padding: '5px 0', borderBottom: '1px solid rgba(0,0,0,0.06)', fontSize: '13px', gap: '8px', lineHeight: 1.7 }}>
    <span style={{ color: '#64748b' }}>{icon} {label}</span>
    <strong style={{ color: '#0f172a', textAlign: 'right' }}>{value}</strong>
  </div>
);

const InfoPanel = ({ data, loading }) => {
  if (loading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '300px', gap: '14px', color: '#64748b' }}>
        <div style={{ width: '36px', height: '36px', border: '3px solid #e2e8f0', borderTopColor: '#10b981', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />
        <p style={{ margin: 0, fontSize: '13px', textAlign: 'center' }}>Fetching real soil & weather…</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '300px', color: '#94a3b8', textAlign: 'center', padding: '20px' }}>
        <div style={{ fontSize: '52px', marginBottom: '14px' }}>🌍</div>
        <p style={{ margin: 0, fontSize: '14px', lineHeight: '1.8', color: '#64748b' }}>
          Click anywhere on the map to see the actual <strong style={{ color: '#8b5cf6' }}>soil type</strong>, live <strong style={{ color: '#3b82f6' }}>weather</strong>, and <strong style={{ color: '#10b981' }}>crops</strong> best suited for that exact location.
        </p>
      </div>
    );
  }

  const { location, weather, soil, crops } = data;

  return (
    <div key={`${location.lat}-${location.lon}`} style={{ animation: 'infoFade 0.2s ease' }}>
      {/* Location breadcrumb */}
      <div style={{ marginBottom: '16px', paddingBottom: '14px', borderBottom: '2px solid #f1f5f9' }}>
        <div style={{ fontWeight: 700, fontSize: '15px', color: '#0f172a', marginBottom: '8px' }}>
          {location.country}
        </div>
        <div style={{ background: '#f8fafc', borderRadius: '8px', padding: '8px 10px', display: 'flex', flexDirection: 'column', gap: '3px' }}>
          {location.village && <div style={{ fontSize: '12px', color: '#0f172a', fontWeight: 600 }}>🏘️ {location.village}</div>}
          {location.mandal && <div style={{ fontSize: '12px', color: '#475569' }}>📍 {location.mandal}</div>}
          {location.district && <div style={{ fontSize: '12px', color: '#64748b' }}>🏙️ {location.district}</div>}
          {location.state && <div style={{ fontSize: '12px', color: '#94a3b8' }}>🗺️ {location.state}</div>}
          <div style={{ fontSize: '11px', color: '#cbd5e1', fontFamily: 'monospace', marginTop: '2px' }}>
            {location.lat.toFixed(5)}°, {location.lon.toFixed(5)}°
          </div>
        </div>
      </div>

      {/* Live Weather */}
      {weather?.success ? (
        <div style={{ marginBottom: '14px' }}>
          <div style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: '#3b82f6', marginBottom: '7px' }}>🌤️ Live Weather</div>
          <div style={{ background: '#eff6ff', borderRadius: '10px', padding: '10px 12px' }}>
            <Row icon="🌡️" label="Temperature" value={`${weather.temp}°C  (↑${weather.temp_max}° ↓${weather.temp_min}°)`} />
            <Row icon="☁️" label="Condition" value={weather.condition} />
            <Row icon="💧" label="Humidity" value={`${weather.humidity}%`} />
            <Row icon="🌧️" label="Rainfall Today" value={`${weather.rainfall}mm`} />
            <Row icon="💨" label="Wind" value={`${weather.wind_speed} km/h`} />
          </div>
        </div>
      ) : (
        <div style={{ marginBottom: '14px', background: '#f8fafc', borderRadius: '10px', padding: '10px 12px', fontSize: '12px', color: '#94a3b8', textAlign: 'center' }}>
          ⚠️ Weather data temporarily unavailable
        </div>
      )}

      {/* Soil - actual data for location */}
      <div style={{ marginBottom: '14px' }}>
        <div style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: '#8b5cf6', marginBottom: '7px' }}>🏔️ Soil Type</div>
        <div style={{ background: '#f5f3ff', borderRadius: '10px', padding: '10px 14px', fontSize: '13px', color: '#5b21b6', fontWeight: 500, lineHeight: 1.5 }}>
          {soil}
        </div>
      </div>

      {/* AI Crop Recommendations */}
      <div>
        <div style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: '#10b981', marginBottom: '4px' }}>🌱 Best Crops for This Location</div>
        <div style={{ fontSize: '11px', color: '#94a3b8', marginBottom: '9px' }}>Recommended based on soil type + live weather</div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '7px' }}>
          {(crops || []).map(c => (
            <span key={c} style={{ background: '#ecfdf5', color: '#065f46', padding: '5px 13px', borderRadius: '20px', fontSize: '12px', fontWeight: 600, border: '1px solid #6ee7b7' }}>
              {c}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
};

// ─── Main Component ───────────────────────────────────────────────────────────
const InteractiveMap = () => {
  const mapRef = useRef(null);
  const mapInstance = useRef(null);
  const markerRef = useRef(null);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [tooltip, setTooltip] = useState(null);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });

  const handleClick = useCallback(async (lat, lng) => {
    setLoading(true);
    setData(null);
    try {
      // Call the unified backend intelligence endpoint
      const res = await axios.post('/api/map/intelligence', { lat, lon: lng });
      setData(res.data);
    } catch (err) {
      console.error('[Map] Intelligence API failed:', err);
      setData(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (mapInstance.current || !mapRef.current) return;

    loadLeafletFromCDN().then(L => {
      if (mapInstance.current || !mapRef.current) return;

      const map = L.map(mapRef.current, {
        center: [20, 0], zoom: 2, scrollWheelZoom: true,
        minZoom: 2, maxZoom: 19, worldCopyJump: true,
      });

      L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
        attribution: '© OpenStreetMap © CARTO', subdomains: 'abcd', maxZoom: 19,
      }).addTo(map);

      const pulseIcon = L.divIcon({
        className: '',
        html: `<div style="width:16px;height:16px;background:#10b981;border:3px solid white;border-radius:50%;box-shadow:0 0 0 5px rgba(16,185,129,0.3);"></div>`,
        iconSize: [16, 16], iconAnchor: [8, 8],
      });

      map.on('click', (e) => {
        const { lat, lng } = e.latlng;
        if (markerRef.current) markerRef.current.remove();
        markerRef.current = L.marker([lat, lng], { icon: pulseIcon }).addTo(map);
        handleClick(lat, lng);
      });

      map.on('mousemove', (e) => {
        setMousePos({ x: e.originalEvent.clientX, y: e.originalEvent.clientY });
        const z = map.getZoom();
        const d = z < 6 ? 2 : z < 12 ? 4 : 6;
        setTooltip(`${e.latlng.lat.toFixed(d)}°, ${e.latlng.lng.toFixed(d)}°`);
      });
      map.on('mouseout', () => setTooltip(null));

      mapInstance.current = map;
    });

    return () => {
      if (mapInstance.current) { mapInstance.current.remove(); mapInstance.current = null; }
    };
  }, [handleClick]);

  return (
    <div style={{ display: 'flex', gap: '20px', alignItems: 'stretch' }}>
      <div style={{ flex: 1, position: 'relative' }}>
        <div ref={mapRef} style={{ height: '500px', width: '100%', borderRadius: '16px', boxShadow: '0 4px 24px rgba(0,0,0,0.12)', border: '1px solid #e2e8f0' }} />
        <div style={{ position: 'absolute', bottom: '12px', left: '12px', zIndex: 1000, background: 'rgba(255,255,255,0.92)', borderRadius: '8px', padding: '5px 10px', fontSize: '11px', color: '#64748b', pointerEvents: 'none', backdropFilter: 'blur(4px)' }}>
          🖱️ Click for real soil + weather crop recommendations
        </div>
        {tooltip && (
          <div style={{ position: 'fixed', left: mousePos.x + 14, top: mousePos.y - 38, background: 'rgba(15,23,42,0.85)', color: 'white', padding: '5px 10px', borderRadius: '8px', fontSize: '12px', fontFamily: 'monospace', pointerEvents: 'none', zIndex: 9999 }}>
            {tooltip}
          </div>
        )}
      </div>

      <div style={{ width: '300px', minWidth: '300px', background: 'white', borderRadius: '16px', padding: '20px', boxShadow: '0 4px 20px rgba(0,0,0,0.10)', border: '1px solid #e2e8f0', overflowY: 'auto', maxHeight: '500px', alignSelf: 'flex-start' }}>
        <InfoPanel data={data} loading={loading} />
      </div>

      <style>{`
        @keyframes infoFade { from { opacity:0; transform:translateY(5px); } to { opacity:1; transform:translateY(0); } }
        @keyframes spin { to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
};

export default InteractiveMap;
