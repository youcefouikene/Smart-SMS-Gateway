import React, { useState, useEffect } from "react";
import { useNavigate, Link, useLocation } from "react-router-dom";
import { registerInit, registerComplete } from "../api/api";

const Register = () => {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [registrationId, setRegistrationId] = useState("");
  const [authUrl, setAuthUrl] = useState("");
  const [authCode, setAuthCode] = useState("");
  const [step, setStep] = useState(1); // 1: initial form, 2: Google authorization, 3: confirmation
  
  const navigate = useNavigate();
  const location = useLocation();

  // To retrieve the authorization code from the URL (if Google redirects to this page)
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const code = params.get("code");
    if (code && registrationId) {
      setAuthCode(code);
      setStep(3);
    }
  }, [location, registrationId]);

  const handleInitialSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (password !== confirmPassword) {
      setError("Passwords do not match!");
      return;
    }

    try {
      const response = await registerInit(username, email, password);
      setRegistrationId(response.registration_id);
      setAuthUrl(response.auth_url);
      setStep(2);
    } catch (err) {
      setError(err.response?.data?.detail || "Registration error. Please try again.");
    }
  };

  const handleCompleteSubmit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      await registerComplete(registrationId, authCode);
      navigate("/login", { state: { message: "Registration successful! You can now log in." } });
    } catch (err) {
      setError(err.response?.data?.detail || "Error finalizing registration. Please try again.");
    }
  };

  // First step: initial registration form
  if (step === 1) {
    return (
      <div className="flex justify-center items-center min-h-screen bg-gray-100 p-4">
        <div className="w-full max-w-md bg-white rounded-lg shadow-md p-8">
          <h2 className="text-2xl font-bold text-center text-gray-800 mb-6">
            Registration
          </h2>

          {error && (
            <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6 rounded">
              <p className="text-red-700">{error}</p>
            </div>
          )}

          <form onSubmit={handleInitialSubmit} className="space-y-4">
            <div>
              <input
                type="text"
                placeholder="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                className="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
              />
            </div>

            <div>
              <input
                type="email"
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

            <div>
              <input
                type="password"
                placeholder="Confirm password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                className="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
              />
            </div>

            <button
              type="submit"
              className="w-full bg-teal-500 hover:bg-teal-600 text-white font-semibold py-3 px-4 rounded-md transition duration-300"
            >
              Continue
            </button>
          </form>

          <p className="text-center text-gray-600 mt-6">
            Already have an account? {" "}
            <Link
              to="/login"
              className="text-teal-500 hover:underline font-medium"
            >
              Login
            </Link>
          </p>
        </div>
      </div>
    );
  }

  // Second step: Google authorization
  if (step === 2) {
    return (
      <div className="flex justify-center items-center min-h-screen bg-gray-100 p-4">
        <div className="w-full max-w-md bg-white rounded-lg shadow-md p-8">
          <h2 className="text-2xl font-bold text-center text-gray-800 mb-6">
            Google Calendar Authorization
          </h2>

          {error && (
            <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6 rounded">
              <p className="text-red-700">{error}</p>
            </div>
          )}

          <div className="space-y-6">
            <p className="text-gray-600">
              To complete your registration, we need access to your Google Calendar.
            </p>
            
            <div className="flex flex-col items-center">
              <a 
                href={authUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-3 px-4 rounded-md transition duration-300 flex items-center"
              >
                <svg className="w-6 h-6 mr-2" fill="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12.545,10.239v3.821h5.445c-0.712,2.315-2.647,3.972-5.445,3.972c-3.332,0-6.033-2.701-6.033-6.033 s2.701-6.032,6.033-6.032c1.498,0,2.866,0.549,3.921,1.453l2.814-2.814C17.503,2.988,15.139,2,12.545,2 C7.021,2,2.543,6.477,2.543,12s4.478,10,10.002,10c8.396,0,10.249-7.85,9.426-11.748L12.545,10.239z"/>
                </svg>
                Sign in with Google
              </a>

              <div className="my-6 text-center">
                <p className="text-gray-500">After authorization, copy the code provided by Google below</p>
              </div>

              <form onSubmit={handleCompleteSubmit} className="w-full space-y-4">
                <input
                  type="text"
                  placeholder="Google authorization code"
                  value={authCode}
                  onChange={(e) => setAuthCode(e.target.value)}
                  required
                  className="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                />

                <button
                  type="submit"
                  className="w-full bg-teal-500 hover:bg-teal-600 text-white font-semibold py-3 px-4 rounded-md transition duration-300"
                >
                  Complete Registration
                </button>
              </form>
            </div>
          </div>

          <button
            onClick={() => setStep(1)}
            className="mt-6 w-full bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold py-2 px-4 rounded-md transition duration-300"
          >
            Back
          </button>
        </div>
      </div>
    );
  }

  // Third step: finalization with code (if component reuse)
  if (step === 3) {
    return (
      <div className="flex justify-center items-center min-h-screen bg-gray-100 p-4">
        <div className="w-full max-w-md bg-white rounded-lg shadow-md p-8">
          <h2 className="text-2xl font-bold text-center text-gray-800 mb-6">
            Complete Registration
          </h2>

          {error && (
            <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6 rounded">
              <p className="text-red-700">{error}</p>
            </div>
          )}

          <form onSubmit={handleCompleteSubmit} className="space-y-4">
            <div>
              <label className="block text-gray-700 mb-2">Google authorization code</label>
              <input
                type="text"
                value={authCode}
                onChange={(e) => setAuthCode(e.target.value)}
                required
                className="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
              />
            </div>

            <button
              type="submit"
              className="w-full bg-teal-500 hover:bg-teal-600 text-white font-semibold py-3 px-4 rounded-md transition duration-300"
            >
              Complete Registration
            </button>
          </form>

          <button
            onClick={() => setStep(2)}
            className="mt-6 w-full bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold py-2 px-4 rounded-md transition duration-300"
          >
            Back
          </button>
        </div>
      </div>
    );
  }
};

export default Register;