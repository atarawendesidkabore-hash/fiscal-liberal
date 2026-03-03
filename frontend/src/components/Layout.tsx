import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import api from '../api/client';

export default function Layout({ children }: { children: React.ReactNode }) {
  const location = useLocation();
  const navigate = useNavigate();
  const [userName, setUserName] = useState('');

  useEffect(() => {
    api.get('/auth/me').then(r => setUserName(r.data.full_name)).catch(() => {});
  }, []);

  const logout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  return (
    <div className="layout">
      <aside className="sidebar">
        <h2>Fiscal Liberal</h2>
        <nav>
          <Link to="/" className={location.pathname === '/' ? 'active' : ''}>
            Sociétés
          </Link>
        </nav>
        <div className="user-info">
          {userName && <div>{userName}</div>}
          <button onClick={logout} className="btn btn-sm" style={{ marginTop: 8, background: 'rgba(255,255,255,0.1)', color: 'white', border: 'none' }}>
            Déconnexion
          </button>
        </div>
      </aside>
      <main className="main-content">{children}</main>
    </div>
  );
}
