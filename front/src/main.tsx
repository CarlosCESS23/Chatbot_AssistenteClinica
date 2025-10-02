import { createRoot } from "react-dom/client";
import App from "./App.tsx";
import "./index.css";
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

import React from 'react';
import ReactDOM from 'react-dom/client';
import Auth from './pages/Auth';
import Admin from './pages/Admin';
import Funcionario from './pages/Funcionario';
import Perfil from './pages/Perfil';
import NotFound from './pages/NotFound';
import Index from './pages/Index';


ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/auth" element={<Auth />} />
        <Route path="/" element={<App />}>
          <Route index element={<Navigate to="/funcionario" replace />} />
          <Route path="inicio" element={<Index />} />
          <Route path="admin" element={<Admin />} />
          <Route path="funcionario" element={<Funcionario />} />
          <Route path="perfil" element={<Perfil />} />
        </Route>
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>,
);

createRoot(document.getElementById("root")!).render(<App />);

