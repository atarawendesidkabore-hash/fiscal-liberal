import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api/client';

interface Exercice {
  id: number;
  date_debut: string;
  date_fin: string;
  statut: string;
}

export default function ExerciceList() {
  const { companyId } = useParams();
  const navigate = useNavigate();
  const [exercices, setExercices] = useState<Exercice[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [dateDebut, setDateDebut] = useState('');
  const [dateFin, setDateFin] = useState('');

  const load = () =>
    api.get(`/exercices/by-company/${companyId}`).then(r => setExercices(r.data));

  useEffect(() => { load(); }, [companyId]);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.post('/exercices', {
      company_id: parseInt(companyId!),
      date_debut: dateDebut,
      date_fin: dateFin,
    });
    setShowForm(false);
    load();
  };

  const statusLabel = (s: string) => {
    if (s === 'brouillon') return { text: 'Brouillon', color: '#636e72' };
    if (s === 'valide') return { text: 'Validé', color: '#00b894' };
    return { text: 'Déposé', color: '#0984e3' };
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <div>
          <button className="btn btn-sm btn-secondary" onClick={() => navigate('/')} style={{ marginBottom: 8 }}>
            ← Retour aux sociétés
          </button>
          <h2>Exercices fiscaux</h2>
        </div>
        <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
          + Nouvel exercice
        </button>
      </div>

      {showForm && (
        <form className="card" onSubmit={submit}>
          <h3>Créer un exercice</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <div className="form-group">
              <label>Date début</label>
              <input type="date" value={dateDebut} onChange={e => setDateDebut(e.target.value)} required />
            </div>
            <div className="form-group">
              <label>Date fin</label>
              <input type="date" value={dateFin} onChange={e => setDateFin(e.target.value)} required />
            </div>
          </div>
          <button type="submit" className="btn btn-success" style={{ marginTop: 10 }}>Créer</button>
        </form>
      )}

      <div className="card">
        <table className="list-table">
          <thead>
            <tr>
              <th>Période</th>
              <th>Statut</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {exercices.map(ex => {
              const st = statusLabel(ex.statut);
              return (
                <tr key={ex.id}>
                  <td>{ex.date_debut} — {ex.date_fin}</td>
                  <td><span style={{ color: st.color, fontWeight: 600 }}>{st.text}</span></td>
                  <td>
                    <div style={{ display: 'flex', gap: 8 }}>
                      <button className="btn btn-sm btn-primary" onClick={() => navigate(`/exercices/${ex.id}/2058a`)}>
                        2058-A
                      </button>
                      <button className="btn btn-sm btn-secondary" onClick={() => navigate(`/exercices/${ex.id}/2058b`)}>
                        2058-B
                      </button>
                      <button className="btn btn-sm btn-secondary" onClick={() => navigate(`/exercices/${ex.id}/2058c`)}>
                        2058-C
                      </button>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        {exercices.length === 0 && (
          <p style={{ textAlign: 'center', color: '#636e72', padding: 20 }}>
            Aucun exercice. Cliquez sur "+ Nouvel exercice" pour commencer.
          </p>
        )}
      </div>
    </div>
  );
}
