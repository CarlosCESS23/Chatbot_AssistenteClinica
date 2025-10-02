// front/src/pages/Admin.tsx

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { useNavigate } from "react-router-dom";
import { LogOut, UserPlus, UserMinus, User, Calendar, Stethoscope } from "lucide-react";
import apiClient from "../api/client"; // Importar nosso cliente de API
import { useToast } from "@/hooks/use-toast";

// Definindo o tipo para um funcionário
interface Funcionario {
  id: number;
  nome: string;
  email: string;
  role: string;
  status: 'pending' | 'active';
}

const Admin = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const userName = localStorage.getItem("userName") || "Administrador";
  
  const [funcionarios, setFuncionarios] = useState<Funcionario[]>([]);
  
  // Função para carregar os dados da API
  const fetchFuncionarios = async () => {
    try {
      const response = await apiClient.get<Funcionario[]>("/admin/funcionarios");
      setFuncionarios(response.data);
    } catch (error) {
      toast({
        title: "Erro ao carregar funcionários",
        description: "Não foi possível buscar os dados da equipe.",
        variant: "destructive",
      });
    }
  };

  // Carregar os dados quando o componente montar
  useEffect(() => {
    fetchFuncionarios();
  }, []);

  const handleApprove = async (userId: number) => {
    try {
      await apiClient.post(`/admin/aprovar/${userId}`);
      toast({
        title: "Sucesso!",
        description: "Funcionário aprovado e movido para a equipe ativa.",
      });
      fetchFuncionarios(); // Recarrega a lista
    } catch (error) {
      toast({
        title: "Erro",
        description: "Não foi possível aprovar o funcionário.",
        variant: "destructive",
      });
    }
  };

  const handleRemove = async (userId: number) => {
    try {
      await apiClient.delete(`/admin/remover/${userId}`);
      toast({
        title: "Sucesso!",
        description: "O registro foi removido.",
      });
      fetchFuncionarios(); // Recarrega a lista
    } catch (error) {
      toast({
        title: "Erro",
        description: "Não foi possível remover o registro.",
        variant: "destructive",
      });
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("accessToken");
    localStorage.removeItem("userName");
    navigate("/auth");
  };

  const pendingUsers = funcionarios.filter(f => f.status === 'pending');
  const activeStaff = funcionarios.filter(f => f.status === 'active' && f.role === 'funcionario');

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-accent/20 to-primary/10">
      {/* Header */}
      <header className="bg-card border-b shadow-sm sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary rounded-lg">
              <Stethoscope className="h-6 w-6 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-foreground">Painel Administrativo</h1>
              <p className="text-sm text-muted-foreground">TeleClinic Sistema</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
             <span className="hidden sm:inline">{userName}</span>
            <Button variant="outline" onClick={handleLogout}>
              <LogOut className="mr-2 h-4 w-4" />
              Sair
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="grid gap-6">
          {/* Solicitações Pendentes */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <UserPlus className="h-5 w-5" />
                Solicitações de Cadastro Pendentes
              </CardTitle>
              <CardDescription>
                Aprove ou rejeite novos funcionários
              </CardDescription>
            </CardHeader>
            <CardContent>
              {pendingUsers.length === 0 ? (
                <p className="text-center text-muted-foreground py-8">
                  Nenhuma solicitação pendente
                </p>
              ) : (
                <div className="space-y-4">
                  {pendingUsers.map((user) => (
                    <div
                      key={user.id}
                      className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 border rounded-lg bg-accent/50"
                    >
                      <div className="flex-1">
                        <h3 className="font-semibold text-foreground">{user.nome}</h3>
                        <p className="text-sm text-muted-foreground mt-1">Email: {user.email}</p>
                      </div>
                      <div className="flex gap-2">
                        <Button size="sm" onClick={() => handleApprove(user.id)}>
                          Aprovar
                        </Button>
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={() => handleRemove(user.id)}
                        >
                          Rejeitar
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Funcionários Ativos */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="h-5 w-5" />
                Equipe Ativa
              </CardTitle>
              <CardDescription>
                Gerencie os funcionários aprovados
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {activeStaff.map((member) => (
                  <div
                    key={member.id}
                    className="flex items-center justify-between p-4 border rounded-lg hover:bg-accent/50 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <Avatar>
                        <AvatarImage src="" />
                        <AvatarFallback className="bg-secondary text-secondary-foreground">
                          {member.nome.charAt(0)}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <p className="font-medium">{member.nome}</p>
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          <Badge variant="secondary">{member.role}</Badge>
                          <span>{member.email}</span>
                        </div>
                      </div>
                    </div>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handleRemove(member.id)}
                    >
                      <UserMinus className="h-4 w-4 text-destructive" />
                    </Button>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
};

export default Admin;