// File: src/components/SMSNotificationSettings/Header.js
import React from "react";

const Header = ({ username, onSave, onLogout }) => {
  return (
    <div className="flex justify-between items-center mb-8">
      <div>
        <h1 className="text-xl font-semibold text-gray-800">
          SMS Notification Settings for Google Agenda
        </h1>
        <p className="text-sm text-gray-500">
          Welcome back, {username || "User"}!
        </p>
      </div>
      <div className="flex space-x-2">
        <button
          className="px-4 py-2 bg-teal-500 text-white rounded text-sm"
          onClick={onSave}
        >
          Save changes
        </button>
        <button 
          className="bg-red-500 text-white px-4 py-2 rounded" 
          onClick={onLogout}
        >
          Logout
        </button>
      </div>
    </div>
  );
};

export default Header;