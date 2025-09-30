import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css'; // Vamos criar este arquivo para estilização

// URL da nossa API FastAPI
const API_URL = 'http://localhost:8000';

function App() {
  const [consultas, setConsultas] = useState([]);
  const [mensagem, setMensagem] = useState('');
  const [destinatario, setDestinatario] = useState(null); // Para saber para quem enviar a msg
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Efeito que busca os dados da API quando o componente é montado
  useEffect(() => {
    fetchConsultas();
  }, []);

  const fetchConsultas = () => {
    setLoading(true);
    axios.get(`${API_URL}/consultas`)
      .then(response => {
        setConsultas(response.data);
        setLoading(false);
      })
      .catch(error => {
        console.error("Erro ao buscar consultas!", error);
        setError('Não foi possível carregar os dados. O servidor backend está rodando?');
        setLoading(false);
      });
  };

  const handleAbrirModal = (consulta) => {
    setDestinatario(consulta);
    setMensagem(''); // Limpa a mensagem anterior
  };
  
  const handleFecharModal = () => {
    setDestinatario(null);
  };

  const handleEnviarNotificacao = () => {
    if (!mensagem || !destinatario) return;

    axios.post(`${API_URL}/notificar`, {
      telegram_id: destinatario.telegram_id,
      mensagem: mensagem
    })
    .then(response => {
      alert('Notificação enviada com sucesso!');
      handleFecharModal();
    })
    .catch(error => {
      console.error("Erro ao enviar notificação!", error);
      alert(`Erro: ${error.response?.data?.detail || 'Não foi possível enviar a notificação.'}`);
    });
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Painel da Clínica - Consultas Agendadas</h1>
        <button onClick={fetchConsultas} disabled={loading}>
          {loading ? 'Atualizando...' : 'Atualizar Lista'}
        </button>
      </header>
      
      <main>
        {error && <p className="error-message">{error}</p>}
        <table>
          <thead>
            <tr>
              <th>Data e Hora</th>
              <th>Paciente</th>
              <th>Clínica</th>
              <th>Zona</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            {consultas.map(consulta => (
              <tr key={consulta.id_agendamento}>
                <td>{new Date(consulta.data_hora).toLocaleString('pt-BR')}</td>
                <td>{consulta.nome_paciente}</td>
                <td>{consulta.nome_clinica}</td>
                <td>{consulta.zona_clinica}</td>
                <td>
                  <button onClick={() => handleAbrirModal(consulta)}>Notificar</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </main>

      {/* Modal de Notificação */}
      {destinatario && (
        <div className="modal-backdrop">
          <div className="modal">
            <h2>Enviar Notificação</h2>
            <p><strong>Paciente:</strong> {destinatario.nome_paciente}</p>
            <textarea 
              rows="4"
              value={mensagem}
              onChange={(e) => setMensagem(e.target.value)}
              placeholder="Digite sua mensagem aqui... (Ex: A sua consulta foi reagendada...)"
            />
            <div className="modal-actions">
              <button onClick={handleEnviarNotificacao}>Enviar</button>
              <button onClick={handleFecharModal} className="cancel-button">Cancelar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;