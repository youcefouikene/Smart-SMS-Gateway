import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { login } from "../api/api";

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [welcomeScreen, setWelcomeScreen] = useState(false);
  const [loggedInUser, setLoggedInUser] = useState(null);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      const userData = await login(email, password);
      localStorage.setItem("user", JSON.stringify(userData));
      setLoggedInUser(userData);
      
      // Une fois les données récupérées, afficher l'écran de bienvenue
      setIsLoading(false);
      setWelcomeScreen(true);
      
      // Rediriger après 2 secondes
      setTimeout(() => {
        setWelcomeScreen(false);
        navigate("/settings");
      }, 2000);
      
    } catch (err) {
      setError("Login failed. Check your credentials.");
      setIsLoading(false);
    }
  };

  return (
    <div className="flex justify-center items-center min-h-screen bg-gray-100 p-4">
      {welcomeScreen ? (
        // Welcome screen - affiché uniquement après récupération des données
        <div className="fixed inset-0 bg-teal-500 flex flex-col items-center justify-center z-50">
          <div className="text-white text-3xl font-bold mb-6">Welcome {loggedInUser?.username || "User"} 👋 !</div>
          <div className="w-16 h-16 border-4 border-white border-t-transparent rounded-full animate-spin"></div>
        </div>
      ) : (
        // Login form
        <div className="w-full max-w-md bg-white rounded-lg shadow-md p-8">
          <h2 className="text-2xl font-bold text-center text-gray-800 mb-6">
            Login
          </h2>

          {error && (
            <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6 rounded">
              <p className="text-red-700">{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <input
                type="text"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
              />
            </div>

            <div>
              <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
              />
            </div>

            <button
              type="submit"
              className="w-full bg-teal-500 hover:bg-teal-600 text-white font-semibold py-3 px-4 rounded-md transition duration-300"
              disabled={isLoading}
            >
              {isLoading ? "Logging in..." : "Log in"}
            </button>
          </form>

          <p className="text-center text-gray-600 mt-6">
            Don't have an account yet? {" "}
            <Link
              to="/register"
              className="text-teal-500 hover:underline font-medium"
            >
              Sign up
            </Link>
          </p>
        </div>
      )}
    </div>
  );
};

export default Login;