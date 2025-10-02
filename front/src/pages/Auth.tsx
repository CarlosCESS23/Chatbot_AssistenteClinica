import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { UserPlus, LogIn, Stethoscope } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";

const Auth = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [loginData, setLoginData] = useState({ email: "", password: "" });
  const [signupData, setSignupData] = useState({
    name: "",
    age: "",
    birthDate: "",
    email: "",
    password: "",
  });

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    // Simulação de login (sem backend real)
    if (loginData.email && loginData.password) {
      // Simular role de admin se email contiver "admin"
      const isAdmin = loginData.email.includes("admin");
      localStorage.setItem("userRole", isAdmin ? "admin" : "funcionario");
      localStorage.setItem("userName", loginData.email.split("@")[0]);
      
      toast({
        title: "Login realizado com sucesso!",
        description: `Bem-vindo, ${isAdmin ? "Administrador" : "Funcionário"}!`,
      });
      
      navigate(isAdmin ? "/admin" : "/funcionario");
    }
  };

  const handleSignup = (e: React.FormEvent) => {
    e.preventDefault();
    // Simulação de cadastro (sem backend real)
    if (signupData.name && signupData.email && signupData.password) {
      toast({
        title: "Cadastro solicitado!",
        description: "Aguarde aprovação do administrador para acessar o sistema.",
      });
      setSignupData({ name: "", age: "", birthDate: "", email: "", password: "" });
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-accent/20 to-primary/10 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="flex items-center justify-center gap-2 mb-8">
          <div className="p-3 bg-primary rounded-full">
            <Stethoscope className="h-8 w-8 text-primary-foreground" />
          </div>
          <h1 className="text-3xl font-bold text-primary">TeleClinic</h1>
        </div>

        <Card className="shadow-xl border-2">
          <CardHeader>
            <CardTitle className="text-2xl text-center">Sistema de Gestão</CardTitle>
            <CardDescription className="text-center">
              Acesso exclusivo para funcionários da clínica
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="login" className="w-full">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="login" className="gap-2">
                  <LogIn className="h-4 w-4" />
                  Login
                </TabsTrigger>
                <TabsTrigger value="signup" className="gap-2">
                  <UserPlus className="h-4 w-4" />
                  Cadastro
                </TabsTrigger>
              </TabsList>

              <TabsContent value="login">
                <form onSubmit={handleLogin} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="login-email">Email</Label>
                    <Input
                      id="login-email"
                      type="email"
                      placeholder="seu.email@clinica.com"
                      value={loginData.email}
                      onChange={(e) => setLoginData({ ...loginData, email: e.target.value })}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="login-password">Senha</Label>
                    <Input
                      id="login-password"
                      type="password"
                      placeholder="••••••••"
                      value={loginData.password}
                      onChange={(e) => setLoginData({ ...loginData, password: e.target.value })}
                      required
                    />
                  </div>
                  <Button type="submit" className="w-full">
                    <LogIn className="mr-2 h-4 w-4" />
                    Entrar
                  </Button>
                </form>
              </TabsContent>

              <TabsContent value="signup">
                <form onSubmit={handleSignup} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="signup-name">Nome Completo</Label>
                    <Input
                      id="signup-name"
                      type="text"
                      placeholder="Seu nome completo"
                      value={signupData.name}
                      onChange={(e) => setSignupData({ ...signupData, name: e.target.value })}
                      required
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="signup-age">Idade</Label>
                      <Input
                        id="signup-age"
                        type="number"
                        placeholder="Ex: 30"
                        value={signupData.age}
                        onChange={(e) => setSignupData({ ...signupData, age: e.target.value })}
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="signup-birthdate">Data de Nascimento</Label>
                      <Input
                        id="signup-birthdate"
                        type="date"
                        value={signupData.birthDate}
                        onChange={(e) => setSignupData({ ...signupData, birthDate: e.target.value })}
                        required
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="signup-email">Email</Label>
                    <Input
                      id="signup-email"
                      type="email"
                      placeholder="seu.email@email.com"
                      value={signupData.email}
                      onChange={(e) => setSignupData({ ...signupData, email: e.target.value })}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="signup-password">Senha</Label>
                    <Input
                      id="signup-password"
                      type="password"
                      placeholder="••••••••"
                      value={signupData.password}
                      onChange={(e) => setSignupData({ ...signupData, password: e.target.value })}
                      required
                    />
                  </div>
                  <Button type="submit" className="w-full" variant="secondary">
                    <UserPlus className="mr-2 h-4 w-4" />
                    Solicitar Cadastro
                  </Button>
                </form>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Auth;
