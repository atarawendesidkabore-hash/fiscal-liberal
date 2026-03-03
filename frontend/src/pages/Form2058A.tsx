import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api/client';

interface ValidationMsg {
  ligne: string;
  niveau: string;
  message: string;
  article_cgi?: string;
}

const LINES = {
  reintegrations: [
    { code: 'WB', field: 'wb_remuneration_exploitant', label: 'Rémunération du travail de l\'exploitant ou des associés' },
    { code: 'WC', field: 'wc_part_deductible', label: 'Part déductible à réintégrer' },
    { code: 'WD', field: 'wd_avantages_personnels', label: 'Avantages personnels non déductibles (hors amort.)' },
    { code: 'WE', field: 'we_amortissements_excessifs', label: 'Amortissements excédentaires (art. 39-4 CGI)', cgi: 'Art. 39-4' },
    { code: 'WF', field: 'wf_impot_societes', label: 'Impôt sur les sociétés' },
    { code: 'WG', field: 'wg_provisions_non_deductibles', label: 'Provisions non déductibles' },
    { code: 'WH', field: 'wh_amendes_penalites', label: 'Amendes et pénalités', cgi: 'Art. 39-2' },
    { code: 'WI', field: 'wi_charges_somptuaires', label: 'Dépenses somptuaires', cgi: 'Art. 39-4' },
    { code: 'WJ', field: 'wj_interets_excessifs', label: 'Intérêts excédentaires', cgi: 'Art. 212 bis' },
    { code: 'WK', field: 'wk_charges_payer_non_deduct', label: 'Charges à payer non déductibles' },
    { code: 'WL', field: 'wl_autres_reintegrations', label: 'Autres réintégrations' },
  ],
  deductions: [
    { code: 'WM', field: 'wm_quote_part_gie', label: 'Quote-part de résultat en GIE / sociétés de personnes' },
    { code: 'WN', field: 'wn_produits_participation', label: 'Produits nets de participations exonérés' },
    { code: 'WO', field: 'wo_plus_values_lt', label: 'Plus-values à long terme' },
    { code: 'WP', field: 'wp_loyers_excessifs', label: 'Fraction des loyers excédentaires' },
    { code: 'WQ', field: 'wq_reprises_provisions', label: 'Reprises de provisions non déductibles' },
    { code: 'WR', field: 'wr_autres_deductions', label: 'Autres déductions' },
  ],
};

const fmt = (v: number) => v.toLocaleString('fr-FR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' €';

export default function Form2058A() {
  const { exerciceId } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState<any>(null);
  const [validation, setValidation] = useState<ValidationMsg[]>([]);
  const [saved, setSaved] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get(`/exercices/${exerciceId}/2058a`).then(r => { setData(r.data); setLoading(false); });
  }, [exerciceId]);

  const updateField = (field: string, value: string) => {
    setData({ ...data, [field]: parseFloat(value) || 0 });
    setSaved(false);
  };

  const save = async () => {
    const resp = await api.put(`/exercices/${exerciceId}/2058a`, data);
    setData(resp.data);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const calculate = async () => {
    await save();
    const resp = await api.post(`/exercices/${exerciceId}/2058a/calculate`);
    setData((prev: any) => ({
      ...prev,
      ws_total_reintegrations: resp.data.ws_total_reintegrations,
      wt_total_deductions: resp.data.wt_total_deductions,
      wu_resultat_fiscal: resp.data.wu_resultat_fiscal,
    }));
  };

  const validate = async () => {
    await save();
    const resp = await api.post(`/exercices/${exerciceId}/2058a/validate`);
    setValidation(resp.data.messages);
  };

  const exportPDF = async () => {
    const resp = await api.post(`/exercices/${exerciceId}/export/pdf?formulaire=2058a`, null, {
      responseType: 'blob',
    });
    const url = window.URL.createObjectURL(new Blob([resp.data]));
    const a = document.createElement('a');
    a.href = url;
    a.download = `2058A_${exerciceId}.pdf`;
    a.click();
  };

  if (loading || !data) return <p>Chargement...</p>;

  const resultat = data.wu_resultat_fiscal || 0;

  return (
    <div>
      <button className="btn btn-sm btn-secondary" onClick={() => navigate(-1)} style={{ marginBottom: 16 }}>
        ← Retour
      </button>

      <h2>Formulaire 2058-A — Détermination du résultat fiscal</h2>

      {/* Summary cards */}
      <div className="summary-grid" style={{ marginTop: 16 }}>
        <div className="summary-card">
          <div className="label">Résultat comptable</div>
          <div className={`value ${data.wa_resultat_comptable >= 0 ? 'neutral' : 'negative'}`}>
            {fmt(data.wa_resultat_comptable || 0)}
          </div>
        </div>
        <div className="summary-card">
          <div className="label">Réintégrations</div>
          <div className="value neutral">{fmt(data.ws_total_reintegrations || 0)}</div>
        </div>
        <div className="summary-card">
          <div className="label">Déductions</div>
          <div className="value neutral">{fmt(data.wt_total_deductions || 0)}</div>
        </div>
        <div className="summary-card">
          <div className="label">Résultat fiscal</div>
          <div className={`value ${resultat >= 0 ? 'positive' : 'negative'}`}>
            {fmt(resultat)}
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="actions-bar">
        <button className="btn btn-primary" onClick={save}>Sauvegarder</button>
        <button className="btn btn-success" onClick={calculate}>Calculer</button>
        <button className="btn btn-secondary" onClick={validate}>Valider CGI</button>
        <button className="btn btn-secondary" onClick={exportPDF}>Export PDF</button>
        {saved && <span className="success-msg" style={{ padding: '8px 16px' }}>Sauvegardé</span>}
      </div>

      {/* Validation messages */}
      {validation.length > 0 && (
        <div style={{ marginBottom: 20 }}>
          {validation.map((v, i) => (
            <div key={i} className={`validation-msg ${v.niveau}`}>
              <strong>{v.ligne}</strong> — {v.message}
              {v.article_cgi && <span style={{ marginLeft: 8, fontSize: 11 }}>({v.article_cgi})</span>}
            </div>
          ))}
        </div>
      )}

      {/* Form table */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <table className="fiscal-table">
          <thead>
            <tr>
              <th style={{ width: 50 }}>Code</th>
              <th>Désignation</th>
              <th style={{ width: 100 }}>Art. CGI</th>
              <th style={{ width: 160 }}>Montant (€)</th>
            </tr>
          </thead>
          <tbody>
            {/* WA — Résultat comptable */}
            <tr style={{ background: '#e8f4fd' }}>
              <td className="line-code">WA</td>
              <td className="line-label" style={{ fontWeight: 700 }}>Résultat net comptable</td>
              <td className="line-cgi"></td>
              <td className="line-amount">
                <input
                  type="number"
                  step="0.01"
                  value={data.wa_resultat_comptable || ''}
                  onChange={e => updateField('wa_resultat_comptable', e.target.value)}
                  placeholder="0,00"
                />
              </td>
            </tr>

            {/* Section: Réintégrations */}
            <tr><td colSpan={4} className="section-header">RÉINTÉGRATIONS</td></tr>
            {LINES.reintegrations.map(line => (
              <tr key={line.code}>
                <td className="line-code">{line.code}</td>
                <td className="line-label">{line.label}</td>
                <td className="line-cgi">{line.cgi || ''}</td>
                <td className="line-amount">
                  <input
                    type="number"
                    step="0.01"
                    value={data[line.field] || ''}
                    onChange={e => updateField(line.field, e.target.value)}
                    placeholder="0,00"
                  />
                </td>
              </tr>
            ))}
            <tr className="row-total">
              <td className="line-code">WS</td>
              <td className="line-label">TOTAL DES RÉINTÉGRATIONS</td>
              <td></td>
              <td style={{ textAlign: 'right', fontFamily: 'Courier New', paddingRight: 12 }}>
                {fmt(data.ws_total_reintegrations || 0)}
              </td>
            </tr>

            {/* Section: Déductions */}
            <tr><td colSpan={4} className="section-header">DÉDUCTIONS</td></tr>
            {LINES.deductions.map(line => (
              <tr key={line.code}>
                <td className="line-code">{line.code}</td>
                <td className="line-label">{line.label}</td>
                <td className="line-cgi"></td>
                <td className="line-amount">
                  <input
                    type="number"
                    step="0.01"
                    value={data[line.field] || ''}
                    onChange={e => updateField(line.field, e.target.value)}
                    placeholder="0,00"
                  />
                </td>
              </tr>
            ))}
            <tr className="row-total">
              <td className="line-code">WT</td>
              <td className="line-label">TOTAL DES DÉDUCTIONS</td>
              <td></td>
              <td style={{ textAlign: 'right', fontFamily: 'Courier New', paddingRight: 12 }}>
                {fmt(data.wt_total_deductions || 0)}
              </td>
            </tr>

            {/* Résultat fiscal */}
            <tr className={`row-result ${resultat >= 0 ? 'benefice' : 'deficit'}`}>
              <td className="line-code">WU</td>
              <td className="line-label">RÉSULTAT FISCAL {resultat >= 0 ? '(Bénéfice)' : '(Déficit)'}</td>
              <td></td>
              <td style={{ textAlign: 'right', fontFamily: 'Courier New', paddingRight: 12, fontSize: 16 }}>
                {fmt(resultat)}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
