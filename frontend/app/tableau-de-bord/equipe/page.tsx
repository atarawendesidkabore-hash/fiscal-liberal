"use client";

import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { api } from "@/lib/api";
import type { TeamMember } from "@/lib/types";

export default function EquipePage() {
  const [members, setMembers] = useState<TeamMember[]>([]);
  const [inviteEmail, setInviteEmail] = useState("");

  useEffect(() => {
    void api.teamMembers().then(setMembers);
  }, []);

  return (
    <section className="space-y-5">
      <Card>
        <CardHeader>
          <CardTitle>Gestion equipe</CardTitle>
          <CardDescription>Fonction reservee au plan Cabinet.</CardDescription>
        </CardHeader>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Inviter un collaborateur</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="space-y-2">
            <Label htmlFor="invite">Email collaborateur</Label>
            <Input id="invite" value={inviteEmail} onChange={(event) => setInviteEmail(event.target.value)} placeholder="fiscaliste@cabinet.fr" />
          </div>
          <Button type="button" onClick={() => setInviteEmail("")}>Envoyer l'invitation</Button>
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
                </tr>
              </thead>
              <tbody>
                {members.map((member) => (
                  <tr key={member.id} className="border-b">
                    <td className="py-2">{member.nom}</td>
                    <td className="py-2">{member.email}</td>
                    <td className="py-2 uppercase">{member.role}</td>
                    <td className="py-2">
                      <Badge variant={member.actif ? "success" : "outline"}>{member.actif ? "Actif" : "Suspendu"}</Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </section>
  );
}

