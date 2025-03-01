import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { login } from "../api/api";

const Login = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate(); // Hook pour rediriger

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const userData = await login(username, password); // Récupère les infos utilisateur
      localStorage.setItem("user", JSON.stringify(userData)); // Stocke en local

      // Rediriger vers la page des paramètres de notifications SMS
      navigate("/settings"); 
    } catch (err) {
      setError("Échec de la connexion. Vérifiez vos identifiants.");
    }
  };

  return (
    <div>
      <h2>Connexion</h2>
      {error && <p style={{ color: "red" }}>{error}</p>}
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Nom d'utilisateur"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Mot de passe"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <button type="submit">Se connecter</button>
      </form>
      <p>Pas encore de compte ? <Link to="/register">S'inscrire</Link></p>
    </div>
  );
};

export default Login;
