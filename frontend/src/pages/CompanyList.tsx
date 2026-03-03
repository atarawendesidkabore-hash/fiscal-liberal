import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';

interface Company {
  id: number;
  raison_sociale: string;
  forme_juridique: string;
  siren: string | null;
  capital_social: number;
}

export default function CompanyList() {
  const navigate = useNavigate();
  const [companies, setCompanies] = useState<Company[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    raison_sociale: '',
    forme_juridique: 'SELARL',
    siren: '',
    siret: '',
    code_ape: '',
    adresse: '',
    capital_social: 0,
  });

  const load = () => api.get('/companies').then(r => setCompanies(r.data));

  useEffect(() => { load(); }, []);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.post('/companies', form);
    setShowForm(false);
    setForm({ raison_sociale: '', forme_juridique: 'SELARL', siren: '', siret: '', code_ape: '', adresse: '', capital_social: 0 });
    load();
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <h2>Mes Sociétés</h2>
        <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
          + Nouvelle société
        </button>
      </div>

      {showForm && (
        <form className="card" onSubmit={submit}>
          <h3>Créer une société</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <div className="form-group">
              <label>Raison sociale</label>
              <input value={form.raison_sociale} onChange={e => setForm({ ...form, raison_sociale: e.target.value })} required />
            </div>
            <div className="form-group">
              <label>Forme juridique</label>
              <select value={form.forme_juridique} onChange={e => setForm({ ...form, forme_juridique: e.target.value })}>
                <option>SELARL</option>
                <option>SELAS</option>
                <option>SAS</option>
                <option>SARL</option>
                <option>EI</option>
                <option>EURL</option>
              </select>
            </div>
            <div className="form-group">
              <label>SIREN</label>
              <input value={form.siren} onChange={e => setForm({ ...form, siren: e.target.value })} maxLength={9} />
            </div>
            <div className="form-group">
              <label>Capital social (€)</label>
              <input type="number" value={form.capital_social} onChange={e => setForm({ ...form, capital_social: parseFloat(e.target.value) || 0 })} />
            </div>
            <div className="form-group" style={{ gridColumn: '1 / -1' }}>
              <label>Adresse</label>
              <input value={form.adresse} onChange={e => setForm({ ...form, adresse: e.target.value })} />
            </div>
          </div>
          <button type="submit" className="btn btn-success" style={{ marginTop: 10 }}>Créer</button>
        </form>
      )}

      <div className="card-grid">
        {companies.map(c => (
          <div key={c.id} className="card" style={{ cursor: 'pointer' }} onClick={() => navigate(`/companies/${c.id}/exercices`)}>
            <h3>{c.raison_sociale}</h3>
            <p style={{ color: '#636e72', fontSize: 14 }}>
              {c.forme_juridique} {c.siren && `— ${c.siren}`}
            </p>
            {c.capital_social > 0 && (
              <p style={{ fontSize: 13, marginTop: 8 }}>
                Capital : {c.capital_social.toLocaleString('fr-FR')} €
              </p>
            )}
            <div style={{ marginTop: 12, display: 'flex', gap: 8 }}>
              <button className="btn btn-sm btn-secondary" onClick={(e) => { e.stopPropagation(); navigate(`/dashboard/${c.id}`); }}>
                Dashboard
              </button>
            </div>
          </div>
        ))}
      </div>

      {companies.length === 0 && !showForm && (
        <div className="card" style={{ textAlign: 'center', color: '#636e72' }}>
          <p>Aucune société. Cliquez sur "+ Nouvelle société" pour commencer.</p>
        </div>
      )}
    </div>
  );
}
