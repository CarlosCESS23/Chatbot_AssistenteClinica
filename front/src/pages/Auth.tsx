// Ficheiro: front/src/pages/Auth.tsx

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useNavigate } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";
import { Stethoscope, LogIn, UserPlus } from "lucide-react";
import apiClient from "../api/client";
import { jwtDecode } from "jwt-decode"; // Importe a biblioteca

// --- NOVO ---
// Interface para definir a estrutura do conteúdo do nosso token
interface DecodedToken {
  sub: string;
  role: 'admin' | 'funcionario';
  name: string;
  exp: number;
}
// --- FIM DO NOVO ---

const Auth = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [isLogin, setIsLogin] = useState(true);

  // Estados para o formulário de login
  const [loginEmail, setLoginEmail] = useState("admin@clinica.com");
  const [loginPassword, setLoginPassword] = useState("admin123");

  // Estados para o formulário de cadastro
  const [signupName, setSignupName] = useState("");
  const [signupEmail, setSignupEmail] = useState("");
  const [signupPassword, setSignupPassword] = useState("");

  // --- FUNÇÃO DE LOGIN ATUALIZADA ---
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    const formData = new URLSearchParams();
    formData.append("username", loginEmail);
    formData.append("password", loginPassword);

    try {
      const response = await apiClient.post("/token", formData, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      });

      const { access_token } = response.data;

      // 1. Descodificar o token para obter os dados do utilizador
      const decodedToken = jwtDecode<DecodedToken>(access_token);

      // 2. Guardar o token e os dados no localStorage
      localStorage.setItem("accessToken", access_token);
      localStorage.setItem("userRole", decodedToken.role);
      localStorage.setItem("userName", decodedToken.name);

      // 3. Redirecionar com base na 'role' vinda do token
      if (decodedToken.role === "admin") {
        navigate("/admin");
      } else {
        navigate("/funcionario");
      }

    } catch (error: any) {
      toast({
        title: "Falha no Login",
        description: error.response?.data?.detail || "Email ou senha incorretos.",
        variant: "destructive",
      });
    }
  };
  // --- FIM DA ATUALIZAÇÃO ---

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient.post("/funcionarios/signup", {
        nome: signupName,
        email: signupEmail,
        password: signupPassword,
      });
      toast({
        title: "Cadastro enviado!",
        description: "Seu cadastro foi enviado e aguarda aprovação do administrador.",
      });
      setIsLogin(true); // Volta para a tela de login
    } catch (error: any) {
      toast({
        title: "Erro no Cadastro",
        description: error.response?.data?.detail || "Não foi possível realizar o cadastro.",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-background via-accent/20 to-primary/10 p-4">
      <Card className="w-full max-w-md shadow-2xl">
        <CardHeader className="text-center">
            <div className="mx-auto bg-primary p-3 rounded-lg inline-block mb-4">
                <Stethoscope className="h-8 w-8 text-primary-foreground" />
            </div>
            <CardTitle className="text-2xl font-bold">{isLogin ? "Bem-vindo de volta!" : "Crie sua conta"}</CardTitle>
            <CardDescription>
            {isLogin ? "Acesse o painel com suas credenciais" : "Preencha os dados para se cadastrar"}
            </CardDescription>
        </CardHeader>
        <CardContent>
          {isLogin ? (
            <form onSubmit={handleLogin} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="login-email">Email</Label>
                <Input id="login-email" type="email" placeholder="admin@clinica.com" value={loginEmail} onChange={(e) => setLoginEmail(e.target.value)} required />
              </div>
              <div className="space-y-2">
                <Label htmlFor="login-password">Senha</Label>
                <Input id="login-password" type="password" placeholder="********" value={loginPassword} onChange={(e) => setLoginPassword(e.target.value)} required />
              </div>
              <Button type="submit" className="w-full">
                <LogIn className="mr-2 h-4 w-4" /> Entrar
              </Button>
            </form>
          ) : (
            <form onSubmit={handleSignup} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="signup-name">Nome Completo</Label>
                <Input id="signup-name" placeholder="Seu nome" value={signupName} onChange={(e) => setSignupName(e.target.value)} required />
              </div>
              <div className="space-y-2">
                <Label htmlFor="signup-email">Email</Label>
                <Input id="signup-email" type="email" placeholder="seu@email.com" value={signupEmail} onChange={(e) => setSignupEmail(e.target.value)} required />
              </div>
              <div className="space-y-2">
                <Label htmlFor="signup-password">Senha</Label>
                <Input id="signup-password" type="password" placeholder="********" value={signupPassword} onChange={(e) => setSignupPassword(e.target.value)} required />
              </div>
              <Button type="submit" className="w-full">
                <UserPlus className="mr-2 h-4 w-4" /> Cadastrar
              </Button>
            </form>
          )}
        </CardContent>
        <CardFooter>
            <Button variant="link" className="w-full" onClick={() => setIsLogin(!isLogin)}>
            {isLogin ? "Não tem uma conta? Cadastre-se" : "Já tem uma conta? Faça login"}
            </Button>
        </CardFooter>
      </Card>
    </div>
  );
};

export default Auth;