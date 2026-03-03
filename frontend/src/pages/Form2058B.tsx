import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api/client';

interface Item {
  id: number;
  nature: string;
  montant: number;
  article_cgi: string | null;
  commentaire: string;
}

export default function Form2058B() {
  const { exerciceId } = useParams();
  const navigate = useNavigate();
  const [items, setItems] = useState<Item[]>([]);
  const [total, setTotal] = useState(0);
  const [showForm, setShowForm] = useState(false);
  const [nature, setNature] = useState('');
  const [montant, setMontant] = useState(0);
  const [articleCgi, setArticleCgi] = useState('');
  const [commentaire, setCommentaire] = useState('');

  const load = () =>
    api.get(`/exercices/${exerciceId}/2058b`).then(r => {
      setItems(r.data.items);
      setTotal(r.data.total);
    });

  useEffect(() => { load(); }, [exerciceId]);

  const addItem = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.post(`/exercices/${exerciceId}/2058b/items`, {
      nature,
      montant,
      article_cgi: articleCgi || null,
      commentaire,
    });
    setNature(''); setMontant(0); setArticleCgi(''); setCommentaire('');
    setShowForm(false);
    load();
  };

  const deleteItem = async (itemId: number) => {
    await api.delete(`/exercices/${exerciceId}/2058b/items/${itemId}`);
    load();
  };

  const exportPDF = async () => {
    const resp = await api.post(`/exercices/${exerciceId}/export/pdf?formulaire=2058b`, null, {
      responseType: 'blob',
    });
    const url = window.URL.createObjectURL(new Blob([resp.data]));
    const a = document.createElement('a');
    a.href = url;
    a.download = `2058B_${exerciceId}.pdf`;
    a.click();
  };

  return (
    <div>
      <button className="btn btn-sm btn-secondary" onClick={() => navigate(-1)} style={{ marginBottom: 16 }}>
        ← Retour
      </button>
      <h2>Formulaire 2058-B — Détail des charges non déductibles</h2>

      <div className="actions-bar" style={{ marginTop: 16 }}>
        <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>+ Ajouter une charge</button>
        <button className="btn btn-secondary" onClick={exportPDF}>Export PDF</button>
      </div>

      {showForm && (
        <form className="card" onSubmit={addItem}>
          <h3>Nouvelle charge non déductible</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <div className="form-group">
              <label>Nature de la charge</label>
              <input value={nature} onChange={e => setNature(e.target.value)} required placeholder="Ex: Amende stationnement" />
            </div>
            <div className="form-group">
              <label>Montant (€)</label>
              <input type="number" step="0.01" value={montant || ''} onChange={e => setMontant(parseFloat(e.target.value) || 0)} required />
            </div>
            <div className="form-group">
              <label>Article CGI (optionnel)</label>
              <input value={articleCgi} onChange={e => setArticleCgi(e.target.value)} placeholder="Ex: Art. 39-2" />
            </div>
            <div className="form-group">
              <label>Commentaire</label>
              <input value={commentaire} onChange={e => setCommentaire(e.target.value)} />
            </div>
          </div>
          <button type="submit" className="btn btn-success" style={{ marginTop: 10 }}>Ajouter</button>
        </form>
      )}

      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <table className="fiscal-table">
          <thead>
            <tr>
              <th>Nature</th>
              <th style={{ width: 100 }}>Article CGI</th>
              <th style={{ width: 140 }}>Montant (€)</th>
              <th style={{ width: 200 }}>Commentaire</th>
              <th style={{ width: 80 }}>Action</th>
            </tr>
          </thead>
          <tbody>
            {items.map(item => (
              <tr key={item.id}>
                <td>{item.nature}</td>
                <td className="line-cgi">{item.article_cgi || '—'}</td>
                <td style={{ textAlign: 'right', fontFamily: 'Courier New' }}>
                  {item.montant.toLocaleString('fr-FR', { minimumFractionDigits: 2 })} €
                </td>
                <td style={{ fontSize: 12, color: '#636e72' }}>{item.commentaire}</td>
                <td>
                  <button className="btn btn-sm btn-danger" onClick={() => deleteItem(item.id)}>Suppr.</button>
                </td>
              </tr>
            ))}
            {items.length === 0 && (
              <tr><td colSpan={5} style={{ textAlign: 'center', color: '#636e72', padding: 20 }}>Aucune charge enregistrée</td></tr>
            )}
            <tr className="row-total">
              <td colSpan={2} style={{ fontWeight: 700 }}>TOTAL</td>
              <td style={{ textAlign: 'right', fontFamily: 'Courier New', fontWeight: 700 }}>
                {total.toLocaleString('fr-FR', { minimumFractionDigits: 2 })} €
              </td>
              <td colSpan={2}></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
