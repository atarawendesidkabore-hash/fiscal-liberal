"use client";

import { Trash2, UserPlus } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import ConfirmDialog from "@/components/ui/confirm-dialog";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/lib/toast";
import { api } from "@/lib/api";
import type { Role, TeamMember } from "@/lib/types";

type PendingRemoval = {
  id: string;
  name: string;
} | null;

export default function EquipePage() {
  const [members, setMembers] = useState<TeamMember[]>([]);
  const [inviteNom, setInviteNom] = useState("");
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteRole, setInviteRole] = useState<Role>("fiscaliste");
  const [pendingRemoval, setPendingRemoval] = useState<PendingRemoval>(null);
  const { push } = useToast();

  useEffect(() => {
    const load = async () => {
      try {
        const data = await api.teamMembers();
        setMembers(data);
      } catch (error) {
        push({ title: "Chargement impossible", description: error instanceof Error ? error.message : "Erreur equipe", variant: "error" });
      }
    };
    void load();
  }, [push]);

  const canInvite = useMemo(() => inviteNom.trim().length > 1 && /\S+@\S+\.\S+/.test(inviteEmail), [inviteNom, inviteEmail]);

  const addMember = () => {
    if (!canInvite) {
      push({ title: "Invitation invalide", description: "Nom et email valides requis.", variant: "error" });
      return;
    }

    const next: TeamMember = {
      id: `local-${Date.now()}`,
      nom: inviteNom.trim(),
      email: inviteEmail.trim(),
      role: inviteRole,
      actif: true
    };

    setMembers((current) => [next, ...current]);
    setInviteNom("");
    setInviteEmail("");
    setInviteRole("fiscaliste");
    push({ title: "Invitation preparee", description: "Le collaborateur est ajoute a la liste locale.", variant: "success" });
  };

  const updateRole = (id: string, role: Role) => {
    setMembers((current) => current.map((member) => (member.id === id ? { ...member, role } : member)));
  };

  const toggleActive = (id: string) => {
    setMembers((current) =>
      current.map((member) =>
        member.id === id
          ? {
              ...member,
              actif: !member.actif
            }
          : member
      )
    );
  };

  const removeMember = () => {
    if (!pendingRemoval) return;
    setMembers((current) => current.filter((member) => member.id !== pendingRemoval.id));
    push({ title: "Collaborateur retire", description: `${pendingRemoval.name} a ete retire de l'equipe.`, variant: "success" });
    setPendingRemoval(null);
  };

  return (
    <section className="space-y-5">
      <Card>
        <CardHeader>
          <CardTitle>Gestion equipe</CardTitle>
          <CardDescription>Fonction reservee au plan Cabinet: ajout, role et activation des utilisateurs.</CardDescription>
        </CardHeader>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Inviter un collaborateur</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-4">
          <div className="space-y-2 md:col-span-1">
            <Label htmlFor="invite-nom">Nom</Label>
            <Input id="invite-nom" value={inviteNom} onChange={(event) => setInviteNom(event.target.value)} placeholder="Julie Martin" />
          </div>
          <div className="space-y-2 md:col-span-2">
            <Label htmlFor="invite-email">Email</Label>
            <Input id="invite-email" value={inviteEmail} onChange={(event) => setInviteEmail(event.target.value)} placeholder="fiscaliste@cabinet.fr" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="invite-role">Role</Label>
            <select
              id="invite-role"
              className="h-10 w-full rounded-md border bg-background px-3 text-sm"
              value={inviteRole}
              onChange={(event) => setInviteRole(event.target.value as Role)}
            >
              <option value="fiscaliste">Fiscaliste</option>
              <option value="client">Client</option>
              <option value="admin">Admin</option>
            </select>
          </div>
          <div className="md:col-span-4">
            <Button type="button" onClick={addMember} disabled={!canInvite}>
              <UserPlus className="mr-2 h-4 w-4" />
              Ajouter a l'equipe
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Membres actifs</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-muted-foreground">
                  <th className="pb-2">Nom</th>
                  <th className="pb-2">Email</th>
                  <th className="pb-2">Role</th>
                  <th className="pb-2">Etat</th>
                  <th className="pb-2 text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {members.map((member) => (
                  <tr key={member.id} className="border-b align-middle">
                    <td className="py-2">{member.nom}</td>
                    <td className="py-2">{member.email}</td>
                    <td className="py-2">
                      <select
                        className="h-9 rounded-md border bg-background px-2 text-xs uppercase"
                        value={member.role}
                        onChange={(event) => updateRole(member.id, event.target.value as Role)}
                        aria-label={`Role de ${member.nom}`}
                      >
                        <option value="admin">Admin</option>
                        <option value="fiscaliste">Fiscaliste</option>
                        <option value="client">Client</option>
                      </select>
                    </td>
                    <td className="py-2">
                      <Badge variant={member.actif ? "success" : "outline"}>{member.actif ? "Actif" : "Suspendu"}</Badge>
                    </td>
                    <td className="py-2 text-right">
                      <div className="inline-flex gap-2">
                        <Button type="button" variant="outline" size="sm" onClick={() => toggleActive(member.id)}>
                          {member.actif ? "Suspendre" : "Reactiver"}
                        </Button>
                        <Button
                          type="button"
                          variant="destructive"
                          size="sm"
                          onClick={() => setPendingRemoval({ id: member.id, name: member.nom })}
                        >
                          <Trash2 className="mr-1 h-3.5 w-3.5" /> Retirer
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      <ConfirmDialog
        open={Boolean(pendingRemoval)}
        title="Retirer ce collaborateur ?"
        description={pendingRemoval ? `${pendingRemoval.name} perdra l'acces au dossier cabinet.` : ""}
        confirmLabel="Retirer"
        onCancel={() => setPendingRemoval(null)}
        onConfirm={removeMember}
      />
    </section>
  );
}
