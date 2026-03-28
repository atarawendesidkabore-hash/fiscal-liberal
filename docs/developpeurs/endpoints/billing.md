# Endpoints de facturation

> API de facturation, webhooks et suivi d'utilisation.

**Statut** : En cours de developpement (prevue v3.1)

---

## Endpoints prevus

### GET /v2/billing/subscription

Obtenir les details de l'abonnement actuel.

```json
{
  "plan": "pro",
  "status": "active",
  "current_period_start": "2025-01-01T00:00:00Z",
  "current_period_end": "2025-02-01T00:00:00Z",
  "price_ht": 79.00,
  "currency": "EUR"
}
```

### GET /v2/billing/usage

Suivi de l'utilisation mensuelle.

```json
{
  "period": "2025-01",
  "calculations": 47,
  "calculations_limit": null,
  "ai_queries": 23,
  "users_active": 3,
  "users_limit": 5
}
```

### GET /v2/billing/invoices

Liste des factures.

```json
{
  "invoices": [
    {
      "id": "INV-2025-001",
      "date": "2025-01-01",
      "amount_ht": 79.00,
      "amount_ttc": 94.80,
      "status": "paid",
      "pdf_url": "/v2/billing/invoices/INV-2025-001/pdf"
    }
  ]
}
```

### POST /v2/billing/change-plan

Changer de formule d'abonnement.

```json
{
  "plan": "cabinet",
  "billing_cycle": "annual"
}
```

## Webhooks (prevus)

FiscIA Pro enverra des webhooks pour les evenements de facturation :

| Evenement | Description |
|-----------|-------------|
| `invoice.created` | Nouvelle facture generee |
| `invoice.paid` | Paiement recu |
| `invoice.failed` | Echec de paiement |
| `subscription.upgraded` | Upgrade de formule |
| `subscription.downgraded` | Downgrade de formule |
| `subscription.cancelled` | Resiliation |

### Format du webhook

```json
{
  "event": "invoice.paid",
  "timestamp": "2025-01-01T00:00:00Z",
  "data": {
    "invoice_id": "INV-2025-001",
    "amount_ttc": 94.80
  }
}
```

### Securite des webhooks

- Signature HMAC-SHA256 dans le header `X-FiscIA-Signature`
- Secret de verification configurable dans les parametres du cabinet

---

## Voir aussi

- [Facturation utilisateur](../../utilisateurs/facturation.md)
- [Gestion facturation admin](../../administration/gestion-facturation.md)
