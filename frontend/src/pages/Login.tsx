import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';

export default function Login() {
  const navigate = useNavigate();
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      if (isRegister) {
        await api.post('/auth/register', { email, password, full_name: fullName });
      }
      const form = new URLSearchParams();
      form.append('username', email);
      form.append('password', password);
      const resp = await api.post('/auth/login', form, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });
      localStorage.setItem('token', resp.data.access_token);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erreur de connexion');
    }
  };

  return (
    <div className="login-page">
      <form className="login-card" onSubmit={handleSubmit}>
        <h1>Fiscal Liberal</h1>
        <p className="subtitle">Suite fiscale 2058-A/B/C</p>
        {error && <div className="error-msg">{error}</div>}
        {isRegister && (
          <div className="form-group">
            <label>Nom complet</label>
            <input value={fullName} onChange={e => setFullName(e.target.value)} required />
          </div>
        )}
        <div className="form-group">
          <label>Email</label>
          <input type="email" value={email} onChange={e => setEmail(e.target.value)} required />
        </div>
        <div className="form-group">
          <label>Mot de passe</label>
          <input type="password" value={password} onChange={e => setPassword(e.target.value)} required />
        </div>
        <button type="submit" className="btn btn-primary">
          {isRegister ? "S'inscrire" : 'Se connecter'}
        </button>
        <p style={{ textAlign: 'center', marginTop: 16, fontSize: 14 }}>
          <span
            onClick={() => setIsRegister(!isRegister)}
            style={{ color: '#1e3a5f', cursor: 'pointer', textDecoration: 'underline' }}
          >
            {isRegister ? 'Déjà un compte ? Se connecter' : "Pas de compte ? S'inscrire"}
          </span>
        </p>
      </form>
    </div>
  );
}
