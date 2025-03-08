import Register from "./components/register";
import Login from "./components/login";
import React from "react";
import HomePage from "./components/HomePage/HomePage";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import SMSNotificationSettings from "./components/SMSNotificationSettings/index";

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
        <Route path="/settings" element={<SMSNotificationSettings />} />
      </Routes>
    </Router>
  );
};

export default App;