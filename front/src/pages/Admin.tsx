import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { useNavigate } from "react-router-dom";
import { LogOut, UserPlus, UserMinus, User, Calendar, Clock, Stethoscope } from "lucide-react";

// Dados simulados
const pendingUsers = [
  { id: 1, name: "Maria Silva", age: 28, birthDate: "1996-03-15", email: "maria.silva@email.com" },
  { id: 2, name: "João Santos", age: 35, birthDate: "1989-07-22", email: "joao.santos@email.com" },
];

const activeStaff = [
  { id: 3, name: "Ana Costa", role: "Enfermeira", email: "ana.costa@clinica.com" },
  { id: 4, name: "Pedro Lima", role: "Recepcionista", email: "pedro.lima@clinica.com" },
  { id: 5, name: "Carla Mendes", role: "Técnica", email: "carla.mendes@clinica.com" },
];

const recentBookings = [
  { id: 1, patient: "Carlos Oliveira", time: "14:00", date: "2025-10-05", type: "Consulta Geral" },
  { id: 2, patient: "Fernanda Rocha", time: "15:30", date: "2025-10-05", type: "Exame" },
  { id: 3, patient: "Roberto Alves", time: "16:00", date: "2025-10-06", type: "Retorno" },
];

const Admin = () => {
  const navigate = useNavigate();
  const userName = localStorage.getItem("userName") || "Administrador";
  const [pending, setPending] = useState(pendingUsers);
  const [staff, setStaff] = useState(activeStaff);

  const handleApprove = (userId: number) => {
    const user = pending.find((u) => u.id === userId);
    if (user) {
      setStaff([...staff, { id: user.id, name: user.name, role: "Funcionário", email: user.email }]);
      setPending(pending.filter((u) => u.id !== userId));
    }
  };

  const handleReject = (userId: number) => {
    setPending(pending.filter((u) => u.id !== userId));
  };

  const handleRemoveStaff = (staffId: number) => {
    setStaff(staff.filter((s) => s.id !== staffId));
  };

  const handleLogout = () => {
    localStorage.removeItem("userRole");
    localStorage.removeItem("userName");
    navigate("/auth");
  };

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
            <Button variant="ghost" onClick={() => navigate("/perfil")}>
              <Avatar className="h-8 w-8 mr-2">
                <AvatarImage src="" />
                <AvatarFallback className="bg-primary text-primary-foreground">
                  {userName.charAt(0).toUpperCase()}
                </AvatarFallback>
              </Avatar>
              <span className="hidden sm:inline">{userName}</span>
            </Button>
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
              {pending.length === 0 ? (
                <p className="text-center text-muted-foreground py-8">
                  Nenhuma solicitação pendente
                </p>
              ) : (
                <div className="space-y-4">
                  {pending.map((user) => (
                    <div
                      key={user.id}
                      className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 border rounded-lg bg-accent/50"
                    >
                      <div className="flex-1">
                        <h3 className="font-semibold text-foreground">{user.name}</h3>
                        <div className="text-sm text-muted-foreground space-y-1 mt-1">
                          <p>Email: {user.email}</p>
                          <p>Idade: {user.age} anos • Nascimento: {new Date(user.birthDate).toLocaleDateString("pt-BR")}</p>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <Button size="sm" onClick={() => handleApprove(user.id)}>
                          Aprovar
                        </Button>
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={() => handleReject(user.id)}
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
                {staff.map((member) => (
                  <div
                    key={member.id}
                    className="flex items-center justify-between p-4 border rounded-lg hover:bg-accent/50 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <Avatar>
                        <AvatarImage src="" />
                        <AvatarFallback className="bg-secondary text-secondary-foreground">
                          {member.name.charAt(0)}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <p className="font-medium">{member.name}</p>
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          <Badge variant="secondary">{member.role}</Badge>
                          <span>{member.email}</span>
                        </div>
                      </div>
                    </div>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handleRemoveStaff(member.id)}
                    >
                      <UserMinus className="h-4 w-4 text-destructive" />
                    </Button>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Reservas Recentes */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="h-5 w-5" />
                Reservas Recentes (Telegram)
              </CardTitle>
              <CardDescription>
                Últimas reservas realizadas via bot do Telegram
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {recentBookings.map((booking) => (
                  <div
                    key={booking.id}
                    className="flex items-center justify-between p-4 border rounded-lg hover:bg-accent/50 transition-colors"
                  >
                    <div className="flex-1">
                      <p className="font-medium text-foreground">{booking.patient}</p>
                      <p className="text-sm text-muted-foreground">{booking.type}</p>
                    </div>
                    <div className="text-right">
                      <div className="flex items-center gap-2 text-sm font-medium">
                        <Clock className="h-4 w-4" />
                        {booking.time}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {new Date(booking.date).toLocaleDateString("pt-BR")}
                      </div>
                    </div>
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
