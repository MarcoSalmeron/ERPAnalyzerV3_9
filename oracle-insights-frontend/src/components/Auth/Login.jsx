import React, { useState } from 'react';
import logoCondor from '../../images/logo_condor.png';
import { GoogleLogin } from '@react-oauth/google';

function Login({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    // Aquí va tu lógica de autenticación
    // Por ahora, llama onLogin() para pasar al dashboard
    onLogin();
  };

  return (
    <div className="h-screen w-screen flex items-center justify-center bg-oracle-dark">
      <div className="bg-oracle-surface border border-oracle-border rounded-xl p-8 w-full max-w-sm shadow-lg">
        <div className="flex items-center gap-3 mb-8 justify-center">
          <img src={logoCondor} alt="Logo" className="h-10 w-auto rounded-full" />
          <h1 className="text-xl font-semibold text-oracle-text">
            Ingeniería Condor <span className="text-oracle-accent">Insights</span>
          </h1>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <input
            type="text"
            placeholder="Usuario"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="bg-oracle-dark border border-oracle-border text-oracle-text rounded-lg px-4 py-2 focus:outline-none focus:border-oracle-accent"
          />
          <input
            type="password"
            placeholder="Contraseña"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="bg-oracle-dark border border-oracle-border text-oracle-text rounded-lg px-4 py-2 focus:outline-none focus:border-oracle-accent"
          />
          <button
            type="submit"
            className="bg-oracle-accent text-oracle-dark font-semibold py-2 rounded-lg hover:opacity-90 transition"
          >
            Iniciar sesión
          </button>
        </form>

        {/* Botón Google OAuth */}
        <div className="mt-4">
          <GoogleLogin
            onSuccess={async (credentialResponse) => {
              const res = await fetch('/api/auth/google', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ credential: credentialResponse.credential }),
              });
              if (res.ok) {
                const data = await res.json();
                localStorage.setItem('access_token', data.access_token);
                onLogin();
              } else {
                const err = await res.json();
                console.error('OAuth fallido:', err.detail);
                alert(`Error: ${err.detail}`); // o usa un estado de error en el UI
              }
            }}
            onError={() => console.error('Google login failed')}
          />
        </div>
      </div>
    </div>
  );
}

export default Login;
