// Update this page (the content is just a fallback if you fail to update the page)

import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";
import { Stethoscope, Users, Calendar, Shield, LogIn } from "lucide-react";

const Index = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-accent/20 to-primary/10">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-20">
        <div className="text-center max-w-3xl mx-auto">
          <div className="flex items-center justify-center gap-3 mb-6">
            <div className="p-4 bg-primary rounded-full">
              <Stethoscope className="h-12 w-12 text-primary-foreground" />
            </div>
          </div>
          <h1 className="text-5xl font-bold mb-6 text-foreground">
            TeleClinic
          </h1>
          <p className="text-xl text-muted-foreground mb-8">
            Sistema de Gestão para Clínicas
          </p>
          <p className="text-lg text-muted-foreground mb-10">
            Gerencie reservas do Telegram, equipe e atendimentos de forma eficiente e organizada.
          </p>
          <Button size="lg" onClick={() => navigate("/auth")} className="text-lg px-8 py-6">
            <LogIn className="mr-2 h-5 w-5" />
            Acessar Sistema
          </Button>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-8 mt-20">
          <div className="text-center p-6 bg-card rounded-lg border-2 shadow-lg hover:border-primary/50 transition-all">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-primary/10 rounded-full mb-4">
              <Shield className="h-8 w-8 text-primary" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Painel Administrativo</h3>
            <p className="text-muted-foreground">
              Controle total sobre aprovação de funcionários e gestão da equipe
            </p>
          </div>
          
          <div className="text-center p-6 bg-card rounded-lg border-2 shadow-lg hover:border-secondary/50 transition-all">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-secondary/10 rounded-full mb-4">
              <Calendar className="h-8 w-8 text-secondary" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Gestão de Reservas</h3>
            <p className="text-muted-foreground">
              Visualize e gerencie todas as reservas feitas via Telegram
            </p>
          </div>
          
          <div className="text-center p-6 bg-card rounded-lg border-2 shadow-lg hover:border-primary/50 transition-all">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-primary/10 rounded-full mb-4">
              <Users className="h-8 w-8 text-primary" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Notificações</h3>
            <p className="text-muted-foreground">
              Comunique-se com pacientes através do Telegram instantaneamente
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Index;
