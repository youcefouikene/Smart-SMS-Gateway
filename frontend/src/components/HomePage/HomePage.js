import React from "react";
import { Link } from "react-router-dom";
import "./HomePage.css"; // We will create this CSS file next

const HomePage = () => {
  return (
    <div className="home-container">
      <div className="overlay"></div>
      <div className="content">
        <h1 className="title">Stay Connected to Your Classes</h1>
        <p className="subtitle">
          Receive SMS notifications for all important events 
          from your Google Agenda and Classroom so you never miss anything.
        </p>
        
        <div className="features">
          <div className="feature-item">
            <div className="feature-icon">📅</div>
            <h3>Event Reminders</h3>
            <p>Get notified about important events in your Google Agenda</p>
          </div>
          <div className="feature-item">
            <div className="feature-icon">📚</div>
            <h3>Google Classroom Alerts</h3>
            <p>Receive alerts for your deadlines in your Google Classroom</p>
          </div>
          <div className="feature-item">
            <div className="feature-icon">📱</div>
            <h3>Instant SMS</h3>
            <p>Notifications delivered directly to your phone</p>
          </div>
        </div>
        
        <div className="cta-buttons">
          <Link to="/register" className="btn btn-primary">
            Sign Up
          </Link>
          <Link to="/login" className="btn btn-secondary">
            Log In
          </Link>
        </div>
      </div>
    </div>
  );
};

export default HomePage;