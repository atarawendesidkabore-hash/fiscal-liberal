import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api/client';

const FIELDS = [
  { field: 'resultat_exercice', label: "Résultat de l'exercice" },
  { field: 'report_a_nouveau_anterieur', label: 'Report à nouveau antérieur' },
  { field: 'dividendes_distribues', label: 'Dividendes distribués' },
  { field: 'reserves_legales', label: 'Réserves légales' },
  { field: 'reserves_statutaires', label: 'Réserves statutaires' },
  { field: 'autres_reserves', label: 'Autres réserves' },
  { field: 'report_a_nouveau_nouveau', label: 'Report à nouveau (nouveau)' },
];

export default function Form2058C() {
  const { exerciceId } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState<any>(null);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    api.get(`/exercices/${exerciceId}/2058c`).then(r => setData(r.data));
  }, [exerciceId]);

  const updateField = (field: string, value: string) => {
    setData({ ...data, [field]: parseFloat(value) || 0 });
    setSaved(false);
  };

  const save = async () => {
    const resp = await api.put(`/exercices/${exerciceId}/2058c`, data);
    setData(resp.data);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const exportPDF = async () => {
    const resp = await api.post(`/exercices/${exerciceId}/export/pdf?formulaire=2058c`, null, {
      responseType: 'blob',
    });
    const url = window.URL.createObjectURL(new Blob([resp.data]));
    const a = document.createElement('a');
    a.href = url;
    a.download = `2058C_${exerciceId}.pdf`;
    a.click();
  };

  if (!data) return <p>Chargement...</p>;

  return (
    <div>
      <button className="btn btn-sm btn-secondary" onClick={() => navigate(-1)} style={{ marginBottom: 16 }}>
        ← Retour
      </button>
      <h2>Formulaire 2058-C — Affectation du résultat</h2>

      <div className="actions-bar" style={{ marginTop: 16 }}>
        <button className="btn btn-primary" onClick={save}>Sauvegarder</button>
        <button className="btn btn-secondary" onClick={exportPDF}>Export PDF</button>
        {saved && <span className="success-msg" style={{ padding: '8px 16px' }}>Sauvegardé</span>}
      </div>

      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <table className="fiscal-table">
          <thead>
            <tr>
              <th>Désignation</th>
              <th style={{ width: 180 }}>Montant (€)</th>
            </tr>
          </thead>
          <tbody>
            {FIELDS.map(f => (
              <tr key={f.field}>
                <td className="line-label">{f.label}</td>
                <td className="line-amount">
                  <input
                    type="number"
                    step="0.01"
                    value={data[f.field] || ''}
                    onChange={e => updateField(f.field, e.target.value)}
                    placeholder="0,00"
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
