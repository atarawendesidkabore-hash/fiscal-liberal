import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import api from '../api/client';

interface HistEntry {
  exercice_id: number;
  periode: string;
  statut: string;
  resultat_comptable: number;
  total_reintegrations: number;
  total_deductions: number;
  resultat_fiscal: number;
}

export default function Dashboard() {
  const { companyId } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    api.get(`/dashboard/${companyId}`).then(r => setData(r.data));
  }, [companyId]);

  if (!data) return <p>Chargement...</p>;

  const fmt = (v: number) => v.toLocaleString('fr-FR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' €';

  const dernier = data.dernier_exercice;

  return (
    <div>
      <button className="btn btn-sm btn-secondary" onClick={() => navigate('/')} style={{ marginBottom: 16 }}>
        ← Retour aux sociétés
      </button>
      <h2>Tableau de bord — {data.company.raison_sociale}</h2>
      <p style={{ color: '#636e72', marginBottom: 20 }}>
        {data.company.forme_juridique} {data.company.siren && `— SIREN ${data.company.siren}`}
      </p>

      {dernier ? (
        <>
          <div className="summary-grid">
            <div className="summary-card">
              <div className="label">Résultat comptable</div>
              <div className={`value ${dernier.resultat_comptable >= 0 ? 'neutral' : 'negative'}`}>
                {fmt(dernier.resultat_comptable)}
              </div>
            </div>
            <div className="summary-card">
              <div className="label">Réintégrations</div>
              <div className="value neutral">{fmt(dernier.total_reintegrations)}</div>
            </div>
            <div className="summary-card">
              <div className="label">Déductions</div>
              <div className="value neutral">{fmt(dernier.total_deductions)}</div>
            </div>
            <div className="summary-card">
              <div className="label">Résultat fiscal</div>
              <div className={`value ${dernier.resultat_fiscal >= 0 ? 'positive' : 'negative'}`}>
                {fmt(dernier.resultat_fiscal)}
              </div>
            </div>
          </div>

          {data.historique.length > 1 && (
            <div className="card">
              <h3>Évolution sur {data.historique.length} exercices</h3>
              <div style={{ width: '100%', height: 350, marginTop: 16 }}>
                <ResponsiveContainer>
                  <BarChart data={data.historique}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="periode" tick={{ fontSize: 11 }} />
                    <YAxis tick={{ fontSize: 11 }} />
                    <Tooltip formatter={(value: number) => fmt(value)} />
                    <Legend />
                    <Bar dataKey="resultat_comptable" fill="#74b9ff" name="Résultat comptable" />
                    <Bar dataKey="total_reintegrations" fill="#fdcb6e" name="Réintégrations" />
                    <Bar dataKey="resultat_fiscal" fill="#00b894" name="Résultat fiscal" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          <div className="card">
            <h3>Historique des exercices</h3>
            <table className="list-table">
              <thead>
                <tr>
                  <th>Période</th>
                  <th>Statut</th>
                  <th style={{ textAlign: 'right' }}>Rés. comptable</th>
                  <th style={{ textAlign: 'right' }}>Réintégrations</th>
                  <th style={{ textAlign: 'right' }}>Déductions</th>
                  <th style={{ textAlign: 'right' }}>Rés. fiscal</th>
                </tr>
              </thead>
              <tbody>
                {data.historique.map((h: HistEntry) => (
                  <tr key={h.exercice_id} onClick={() => navigate(`/exercices/${h.exercice_id}/2058a`)}>
                    <td>{h.periode}</td>
                    <td>{h.statut}</td>
                    <td style={{ textAlign: 'right', fontFamily: 'Courier New' }}>{fmt(h.resultat_comptable)}</td>
                    <td style={{ textAlign: 'right', fontFamily: 'Courier New' }}>{fmt(h.total_reintegrations)}</td>
                    <td style={{ textAlign: 'right', fontFamily: 'Courier New' }}>{fmt(h.total_deductions)}</td>
                    <td style={{ textAlign: 'right', fontFamily: 'Courier New', fontWeight: 700, color: h.resultat_fiscal >= 0 ? '#00b894' : '#d63031' }}>
                      {fmt(h.resultat_fiscal)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      ) : (
        <div className="card" style={{ textAlign: 'center', color: '#636e72' }}>
          <p>Aucun exercice fiscal. Créez votre premier exercice pour commencer.</p>
          <button className="btn btn-primary" style={{ marginTop: 16 }} onClick={() => navigate(`/companies/${companyId}/exercices`)}>
            Créer un exercice
          </button>
        </div>
      )}
    </div>
  );
}
