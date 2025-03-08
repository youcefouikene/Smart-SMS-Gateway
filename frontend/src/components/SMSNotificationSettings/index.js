// File: src/components/SMSNotificationSettings/index.js
// This is the main component that will import and compose all the other components
import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getUserSettings, saveSettings } from "../../api/api";
import Header from "./header";
import AgendaFieldsSection from "./agendaFieldsSection";
import PhoneNumberSection from "./phoneNumberSection";
import KeywordsSection from "./keywordsSection";
import { removeCountryCode } from "../../utils/phoneUtils";

const SMSNotificationSettings = () => {
  const navigate = useNavigate();
  
  // User state
  const [user, setUser] = useState(null);
  
  // States for fields to include in SMS
  const [selectedFields, setSelectedFields] = useState({
    summary: false,
    start: false,
    end: false,
    location:false,
    description: false,
    organizer: false,
  });
  
  // States for phone number
  const [phoneNumber, setPhoneNumber] = useState("");
  const [selectedCountry, setSelectedCountry] = useState(null);
  
  // States for keywords
  const [keywords, setKeywords] = useState([]);
  
  useEffect(() => {
    const storedUser = localStorage.getItem("user");
    if (storedUser) {
      const parsedUser = JSON.parse(storedUser);
      setUser(parsedUser);
  
      // Fetch updated settings from backend
      const fetchSettings = async () => {
        try {
          const updatedSettings = await getUserSettings(parsedUser.username);
          setUser((prevUser) => ({
            ...prevUser,
            settings: updatedSettings,
          }));
  
          // Initialize settings from updated data
          if (updatedSettings) {
            if (updatedSettings.phoneNumber) {
              setPhoneNumber(removeCountryCode(updatedSettings.phoneNumber));
            }
  
            if (updatedSettings.agendaFields && Array.isArray(updatedSettings.agendaFields)) {
              const fieldsState = {
                summary: updatedSettings.agendaFields.includes("summary"),
                start: updatedSettings.agendaFields.includes("start"),
                end: updatedSettings.agendaFields.includes("end"),
                location: updatedSettings.agendaFields.includes("location"),
                description: updatedSettings.agendaFields.includes("description"),
                organizer: updatedSettings.agendaFields.includes("organizer"),
              };
              setSelectedFields(fieldsState);
            }
  
            if (updatedSettings.keywords && Array.isArray(updatedSettings.keywords)) {
              setKeywords(updatedSettings.keywords);
            }
          }
        } catch (error) {
          console.error("Error fetching user settings:", error);
        }
      };
  
      fetchSettings();
    } else {
      navigate("/login");
      alert("You must be logged in to access this page!");
    }
  }, [navigate]);
  
  const handleLogout = () => {
    localStorage.removeItem("user");
    navigate("/login");
  };

  const saveTheSettings = async () => {
    const agendaFields = Object.keys(selectedFields).filter(
      (key) => selectedFields[key]
    );

    if (agendaFields.length === 0) {
      alert("Please select at least one agenda field.");
      return;
    }

    if (!phoneNumber.trim()) {
      alert("Please enter a phone number.");
      return;
    }

    const fullPhoneNumber = `${selectedCountry.code}${phoneNumber.trim()}`;

    try {
      const token = user.access_token;
      await saveSettings(fullPhoneNumber, agendaFields, token);
      console.log("Settings saved successfully!");
    } catch (error) {
      console.error("Error saving settings:", error);
      alert("Failed to save settings.");
    }
  };

  const handleFieldToggle = (field) => {
    setSelectedFields((prev) => ({
      ...prev,
      [field]: !prev[field],
    }));
  };

  return (
    <div className="flex h-full bg-gray-100">
      <div className="flex-1">
        <main className="mx-auto p-6">
          <div className="bg-white rounded-md shadow-sm p-6">
            <Header 
              username={user?.username}
              onSave={saveTheSettings}
              onLogout={handleLogout}
            />

            <AgendaFieldsSection 
              selectedFields={selectedFields} 
              onFieldToggle={handleFieldToggle} 
            />

            <PhoneNumberSection
              phoneNumber={phoneNumber}
              setPhoneNumber={setPhoneNumber}
              selectedCountry={selectedCountry}
              setSelectedCountry={setSelectedCountry}
            />

            <KeywordsSection
              keywords={keywords}
              setKeywords={setKeywords}
              userToken={user?.access_token}
            />
          </div>
        </main>
      </div>
    </div>
  );
};

export default SMSNotificationSettings;