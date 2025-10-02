import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { useNavigate } from "react-router-dom";
import { LogOut, Calendar, Clock, MessageSquare, Stethoscope, AlertCircle, Send } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

// Dados simulados de reservas
const bookingsData = [
  { id: 1, patient: "Carlos Oliveira", time: "14:00", date: "2025-10-05", type: "Consulta Geral", status: "confirmado", telegram: "@carlos_o" },
  { id: 2, patient: "Fernanda Rocha", time: "15:30", date: "2025-10-05", type: "Exame de Sangue", status: "confirmado", telegram: "@fer_rocha" },
  { id: 3, patient: "Roberto Alves", time: "16:00", date: "2025-10-06", type: "Retorno", status: "pendente", telegram: "@roberto_alves" },
  { id: 4, patient: "Juliana Martins", time: "09:00", date: "2025-10-06", type: "Consulta Especialista", status: "confirmado", telegram: "@ju_martins" },
  { id: 5, patient: "Marcos Paulo", time: "10:30", date: "2025-10-07", type: "Exame de Imagem", status: "confirmado", telegram: "@marcospaulo" },
];

const Funcionario = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const userName = localStorage.getItem("userName") || "Funcionário";
  const [bookings] = useState(bookingsData);
  const [message, setMessage] = useState("");
  const [selectedBooking, setSelectedBooking] = useState<typeof bookingsData[0] | null>(null);

  const handleSendMessage = () => {
    if (message.trim() && selectedBooking) {
      toast({
        title: "Mensagem enviada!",
        description: `Notificação enviada para ${selectedBooking.patient} no Telegram (${selectedBooking.telegram})`,
      });
      setMessage("");
      setSelectedBooking(null);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("userRole");
    localStorage.removeItem("userName");
    navigate("/auth");
  };

  const getStatusBadge = (status: string) => {
    if (status === "confirmado") {
      return <Badge className="bg-secondary text-secondary-foreground">Confirmado</Badge>;
    }
    return <Badge variant="outline">Pendente</Badge>;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-accent/20 to-primary/10">
      {/* Header */}
      <header className="bg-card border-b shadow-sm sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-secondary rounded-lg">
              <Stethoscope className="h-6 w-6 text-secondary-foreground" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-foreground">Painel do Funcionário</h1>
              <p className="text-sm text-muted-foreground">TeleClinic Sistema</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <Button variant="ghost" onClick={() => navigate("/perfil")}>
              <Avatar className="h-8 w-8 mr-2">
                <AvatarImage src="" />
                <AvatarFallback className="bg-secondary text-secondary-foreground">
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
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              Reservas de Pacientes
            </CardTitle>
            <CardDescription>
              Consulte as reservas feitas via Telegram e notifique os pacientes quando necessário
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {bookings.map((booking) => (
                <div
                  key={booking.id}
                  className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-5 border-2 rounded-lg hover:border-primary/50 transition-all hover:shadow-md bg-card"
                >
                  <div className="flex-1 space-y-2">
                    <div className="flex items-start gap-3">
                      <Avatar className="h-10 w-10">
                        <AvatarImage src="" />
                        <AvatarFallback className="bg-primary text-primary-foreground">
                          {booking.patient.charAt(0)}
                        </AvatarFallback>
                      </Avatar>
                      <div className="flex-1">
                        <h3 className="font-semibold text-foreground text-lg">{booking.patient}</h3>
                        <p className="text-sm text-muted-foreground">{booking.type}</p>
                        <p className="text-xs text-muted-foreground mt-1">Telegram: {booking.telegram}</p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
                    <div className="text-right">
                      <div className="flex items-center gap-2 text-sm font-medium mb-1">
                        <Clock className="h-4 w-4 text-primary" />
                        {booking.time}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {new Date(booking.date).toLocaleDateString("pt-BR", { 
                          day: "2-digit", 
                          month: "long",
                          year: "numeric" 
                        })}
                      </div>
                      <div className="mt-2">{getStatusBadge(booking.status)}</div>
                    </div>
                    
                    <Dialog>
                      <DialogTrigger asChild>
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => setSelectedBooking(booking)}
                        >
                          <MessageSquare className="mr-2 h-4 w-4" />
                          Notificar
                        </Button>
                      </DialogTrigger>
                      <DialogContent>
                        <DialogHeader>
                          <DialogTitle className="flex items-center gap-2">
                            <AlertCircle className="h-5 w-5 text-primary" />
                            Enviar Notificação ao Paciente
                          </DialogTitle>
                          <DialogDescription>
                            Envie uma mensagem via Telegram para {booking.patient}
                          </DialogDescription>
                        </DialogHeader>
                        <div className="space-y-4 pt-4">
                          <div className="p-3 bg-accent/50 rounded-lg">
                            <p className="text-sm font-medium">Paciente: {booking.patient}</p>
                            <p className="text-sm text-muted-foreground">Telegram: {booking.telegram}</p>
                            <p className="text-sm text-muted-foreground">
                              Agendamento: {new Date(booking.date).toLocaleDateString("pt-BR")} às {booking.time}
                            </p>
                          </div>
                          <div className="space-y-2">
                            <label className="text-sm font-medium">Mensagem</label>
                            <Textarea
                              placeholder="Digite sua mensagem aqui... Ex: Confirmação de consulta, reagendamento, informações importantes, etc."
                              value={message}
                              onChange={(e) => setMessage(e.target.value)}
                              rows={4}
                            />
                          </div>
                          <Button 
                            onClick={handleSendMessage} 
                            className="w-full"
                            disabled={!message.trim()}
                          >
                            <Send className="mr-2 h-4 w-4" />
                            Enviar via Telegram
                          </Button>
                        </div>
                      </DialogContent>
                    </Dialog>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
};

export default Funcionario;
