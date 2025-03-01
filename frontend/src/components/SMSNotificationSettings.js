import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  Plus,
  Trash2,
  PlusCircle,
  MinusCircle,
} from "lucide-react";
import { addKeyword , removeKeyword , getUserSettings , addNotificationTime , deleteNotificationTime , saveSettings} from "../api/api";


const SMSNotificationSettings = () => {
  const navigate = useNavigate();
  
  //==============================================================================
  // ÉTATS (STATE MANAGEMENT)
  //==============================================================================
  
  // États utilisateur
  const [user, setUser] = useState(null);
  
  // États pour les champs à inclure dans le SMS
  const [selectedFields, setSelectedFields] = useState({
    title: false,
    date: false,
    description: true,
    priority: true,
  });
  
  // États pour le numéro de téléphone
  const [phoneNumber, setPhoneNumber] = useState("");
  const countryCodes = [
    { "name": "Algeria", "code": "+213" },
    { "name": "Tunisia", "code": "+216" },
    { "name": "Morocco", "code": "+212" },
    { "name": "France", "code": "+33" },
    { "name": "United States", "code": "+1" },
    { "name": "Belgium", "code": "+32" },
    { "name": "United Kingdom", "code": "+44" },
    { "name": "Germany", "code": "+49" }
  ]
  const [selectedCountry, setSelectedCountry] = useState(countryCodes[0]); // DZ par défaut
  
  // États pour les mots-clés et minuteries
  const [keywords, setKeywords] = useState([]);
  const [newKeyword, setNewKeyword] = useState("");
  const [newKeywordMinutes, setNewKeywordMinutes] = useState(15);
  const [newNotifMinutes, setNewNotifMinutes] = useState(0);
  
  

  //==============================================================================
  // HOOKS & EFFETS
  //==============================================================================
  
  useEffect(() => {
    const storedUser = localStorage.getItem("user");
    if (storedUser) {
      const parsedUser = JSON.parse(storedUser);
      setUser(parsedUser);
  
      // Récupérer les paramètres mis à jour depuis le backend
      const fetchSettings = async () => {
        try {
          const updatedSettings = await getUserSettings(parsedUser.username);
          setUser((prevUser) => ({
            ...prevUser,
            settings: updatedSettings,
          }));
  
          // Initialisation des paramètres à partir des données mises à jour
          if (updatedSettings) {
            if (updatedSettings.phoneNumber) {
              setPhoneNumber(updatedSettings.phoneNumber);
            }
  
            if (updatedSettings.agendaFields && Array.isArray(updatedSettings.agendaFields)) {
              const fieldsState = {
                title: updatedSettings.agendaFields.includes("title"),
                date: updatedSettings.agendaFields.includes("date"),
                description: updatedSettings.agendaFields.includes("description"),
                priority: updatedSettings.agendaFields.includes("priority"),
              };
              setSelectedFields(fieldsState);
            }
  
            if (updatedSettings.keywords && Array.isArray(updatedSettings.keywords)) {
              setKeywords(updatedSettings.keywords);
            }
          }
        } catch (error) {
          console.error("Erreur lors de la récupération des paramètres utilisateur :", error);
        }
      };
  
      fetchSettings();
    } else {
      navigate("/login");
      alert("Vous devez être connecté pour accéder à cette page !");
    }
  }, [navigate]);
  

  //==============================================================================
  // GESTIONNAIRES D'ÉVÉNEMENTS - GÉNÉRAL
  //==============================================================================
  
  const handleLogout = () => {
    localStorage.removeItem("user"); // ✅ Supprime les infos de l'utilisateur
    navigate("/login"); // Redirige vers la page de connexion
  };

  const saveTheSettings = async () => {
    const agendaFields = Object.keys(selectedFields).filter(
      (key) => selectedFields[key]
    );
    try {
      const token = user.access_token;
      
      await saveSettings(phoneNumber, agendaFields, token);
      
      console.log("Paramètres enregistrés avec succès !");
    } catch (error) {
      console.error("Erreur lors de l'enregistrement :", error);
      alert("Échec de l'enregistrement des paramètres.");
    }
  };
  

  //==============================================================================
  // GESTIONNAIRES D'ÉVÉNEMENTS - CHAMPS AGENDA
  //==============================================================================
  
  const handleFieldToggle = (field) => {
    setSelectedFields((prev) => ({
      ...prev,
      [field]: !prev[field],
    }));
  };


  //==============================================================================
  // GESTIONNAIRES D'ÉVÉNEMENTS - NUMERO DE TELEPHONE
  //==============================================================================

  const handlePhoneNumberChange = (e) => {
    let value = e.target.value.replace(/\D/g, ""); // Supprime tout sauf les chiffres
  
    if (value.startsWith("0")) {
      value = value.substring(1); // Enlève le zéro de début
    }
  
    setPhoneNumber(value);
  };

  //==============================================================================
  // GESTIONNAIRES D'ÉVÉNEMENTS - MOTS-CLÉS
  //==============================================================================
  
  const handleAddKeyword = async (e) => {
    e.preventDefault();
  
    if (newKeyword.trim() === "" || keywords.some((k) => k.text === newKeyword.trim())) {
      return;
    }
  
    try {
      const token = user.access_token;
      await addKeyword(newKeyword, newKeywordMinutes, token);
  
      // Si l'ajout réussit, mettre à jour l'état local
      setKeywords([
        ...keywords,
        { text: newKeyword.trim(), notificationTimes: [newKeywordMinutes] },
      ]);
      setNewKeyword("");
      setNewKeywordMinutes(15);
    } catch (error) {
      alert("Impossible d'ajouter le mot-clé, veuillez réessayer.");
    }
  };

  const handleRemoveKeyword = async (keywordText) => {
    try {
      await removeKeyword(keywordText, user.access_token); // Appelle l'API
      setKeywords(keywords.filter((k) => k.text !== keywordText)); // Met à jour l'état
    } catch (error) {
      alert("Erreur lors de la suppression du mot-clé !");
    }
  };
  //==============================================================================
  // GESTIONNAIRES D'ÉVÉNEMENTS - MINUTERIES DE NOTIFICATION
  //==============================================================================
  
  const handleAddNotificationTime = async (keywordText) => {
    try {
      const token = user.access_token; 
      if (!token) {
        alert("Vous devez être connecté pour modifier les notifications.");
        return;
      }
  
      await addNotificationTime(keywordText, newNotifMinutes, token);
  
      // Mettre à jour localement les notifications après la mise à jour réussie
      setKeywords((prevKeywords) =>
        prevKeywords.map((k) =>
          k.text === keywordText
            ? { ...k, notificationTimes: [...k.notificationTimes, newNotifMinutes] }
            : k
        )
      );
    } catch (error) {
      alert("Impossible d'ajouter le temps de notification. Veuillez réessayer.");
    }
  };
  

  const handleRemoveNotificationTime = async (keywordText, index) => {
    if (!user || !user.access_token) {
      alert("Vous devez être connecté pour effectuer cette action.");
      return;
    }
  
    const notificationTime = keywords.find(k => k.text === keywordText)?.notificationTimes[index];
    console.log(notificationTime);
  
    if (notificationTime === undefined) return; // Vérification supplémentaire
  
    try {
      await deleteNotificationTime(keywordText, notificationTime, user.access_token);
      
      // Mise à jour locale après suppression côté serveur
      setKeywords(
        keywords.map((k) =>
          k.text === keywordText
            ? {
                ...k,
                notificationTimes: k.notificationTimes.filter((_, i) => i !== index),
              }
            : k
        )
      );
    } catch (error) {
      alert("Erreur lors de la suppression du temps de notification.");
    }
  };
  

  const handleNotificationTimeChange = (keywordText, index, minutes) => {
    setKeywords(
      keywords.map((k) => {
        if (k.text === keywordText) {
          const newTimes = [...k.notificationTimes];
          newTimes[index] = minutes;
          return { ...k, notificationTimes: newTimes };
        }
        return k;
      })
    );
  };

  //==============================================================================
  // RENDU UI
  //==============================================================================
  
  return (
    <div className="flex h-full bg-gray-100">
      {/* Main Content */}
      <div className="flex-1">
        <main className="mx-auto p-6">
          <div className="bg-white rounded-md shadow-sm p-6">
            {/* En-tête et boutons d'action */}
            <div className="flex justify-between items-center mb-8">
              <div>
                <h1 className="text-xl font-semibold text-gray-800">
                  SMS Notification Settings
                </h1>
                <p className="text-sm text-gray-500">Welcome back, {user?.username}!</p>
              </div>
              <div className="flex space-x-2">
                <button
                  className="px-4 py-2 bg-teal-500 text-white rounded text-sm"
                  onClick={saveTheSettings}
                >
                  Save
                </button>
                <button className="bg-red-500 text-white px-4 py-2 rounded" onClick={handleLogout}>
                  Logout
                </button>
                
              </div>
            </div>

            {/* Section: Sélection des champs à inclure dans le SMS */}
            <div className="mb-8">
              <h2 className="text-md font-medium mb-2">
                Select Event Fields to Include in SMS
              </h2>
              <p className="text-sm text-gray-500 mb-4">
                Choose the event details to include in the SMS:
              </p>

              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="title"
                    checked={selectedFields.title}
                    onChange={() => handleFieldToggle("title")}
                    className="w-4 h-4 rounded border-gray-300 text-teal-500 focus:ring-0 focus:ring-offset-0"
                  />
                  <label htmlFor="title" className="ml-2 text-sm text-gray-700">
                    Title
                  </label>
                </div>
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="date"
                    checked={selectedFields.date}
                    onChange={() => handleFieldToggle("date")}
                    className="w-4 h-4 rounded border-gray-300 text-teal-500 focus:ring-0 focus:ring-offset-0"
                  />
                  <label htmlFor="date" className="ml-2 text-sm text-gray-700">
                    Date
                  </label>
                </div>
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="description"
                    checked={selectedFields.description}
                    onChange={() => handleFieldToggle("description")}
                    className="w-4 h-4 rounded border-gray-300 text-teal-500 focus:ring-0 focus:ring-offset-0"
                  />
                  <label
                    htmlFor="description"
                    className="ml-2 text-sm text-gray-700"
                  >
                    Description
                  </label>
                </div>
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="priority"
                    checked={selectedFields.priority}
                    onChange={() => handleFieldToggle("priority")}
                    className="w-4 h-4 rounded border-gray-300 text-teal-500 focus:ring-0 focus:ring-offset-0"
                  />
                  <label
                    htmlFor="priority"
                    className="ml-2 text-sm text-gray-700"
                  >
                    Priority
                  </label>
                </div>
              </div>
            </div>

            {/* Section: Numéro de téléphone pour les notifications */}
            <div className="mb-8">
              <h2 className="text-md font-medium mb-2">
                Phone Number to Receive Notifications
              </h2>
              <p className="text-sm text-gray-500 mb-4">
                Phone number to receive SMS alerts:
              </p>

              <div className="mt-1">
                <div className="flex flex-col">
                  <label className="text-xs text-gray-500 mb-1">Phone number</label>
                  <div className="relative">
                    <div className="flex">
                      {/* Dropdown pour le choix du pays */}
                      <select
                        className="border border-gray-300 rounded-l bg-white px-3 py-2 text-gray-600 text-sm focus:ring-teal-500 focus:border-teal-500"
                        value={selectedCountry.code}
                        onChange={(e) =>
                          setSelectedCountry(
                            countryCodes.find((c) => c.code === e.target.value)
                          )
                        }
                      >
                        {countryCodes.map((country) => (
                          <option key={country.code} value={country.code}>
                            {country.name} {country.code}
                          </option>
                        ))}
                      </select>

                      {/* Champ de saisie du numéro */}
                      <input
                        type="text"
                        value={phoneNumber}
                        onChange={handlePhoneNumberChange}
                        className="flex-1 border border-l-0 border-gray-300 rounded-r py-2 px-3 focus:outline-none focus:ring-1 focus:ring-teal-500 focus:border-teal-500"
                        placeholder="123456789"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>


            {/* Section: Filtrage par mots-clés */}
            <div>
              <h2 className="text-md font-medium mb-2">Filter by Keywords</h2>
              <p className="text-sm text-gray-500 mb-4">
                Receive alerts only for events containing these keywords. Add
                multiple notification times for each keyword:
              </p>

              {/* Formulaire d'ajout de mot-clé */}
              <div className="mb-6">
                <form
                  onSubmit={handleAddKeyword}
                  className="flex flex-wrap gap-2 items-end"
                >
                  <div className="flex-1">
                    <label className="block text-xs text-gray-500 mb-1">
                      Keyword
                    </label>
                    <input
                      type="text"
                      value={newKeyword}
                      onChange={(e) => setNewKeyword(e.target.value)}
                      placeholder="Add a new keyword"
                      className="w-full rounded border border-gray-300 py-2 px-3 text-sm focus:outline-none focus:ring-1 focus:ring-teal-500 focus:border-teal-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">
                      First Alert After
                    </label>
                    <div className="flex">
                      <input
                        type="number"
                        value={newKeywordMinutes}
                        onChange={(e) =>
                          setNewKeywordMinutes(parseInt(e.target.value) || 0)
                        }
                        className="w-16 border border-gray-300 rounded-l py-2 px-3 text-sm focus:outline-none focus:ring-1 focus:ring-teal-500 focus:border-teal-500"
                      />
                      <div className="px-3 py-2 border border-l-0 border-gray-300 bg-gray-50 text-sm text-gray-500 rounded-r">
                        Minutes
                      </div>
                    </div>
                  </div>
                  <button
                    type="submit"
                    className="bg-teal-500 text-white px-4 py-2 rounded flex items-center justify-center"
                  >
                    <Plus className="h-4 w-4 mr-1" />
                    <span>Add</span>
                  </button>
                </form>
              </div>

              {/* Liste des mots-clés et minuteries */}
              <div className="space-y-4">
                {keywords.map((keyword) => (
                  <div
                    key={keyword.text}
                    className="p-4 border border-gray-200 rounded bg-gray-50"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <span className="font-medium text-teal-600 px-3 py-1 bg-teal-100 rounded-full">
                        {keyword.text}
                      </span>
                      <div className="flex items-center gap-2">
                      <div className="flex">
                        <input
                          type="number"
                          value={newNotifMinutes}
                          onChange={(e) =>
                            setNewNotifMinutes(parseInt(e.target.value) || 15)
                          }
                          className="w-16 border border-gray-300 rounded-l py-2 px-3 text-sm focus:outline-none focus:ring-1 focus:ring-teal-500 focus:border-teal-500"
                        />
                        <div className="px-3 py-2 border border-l-0 border-gray-300 bg-gray-50 text-sm text-gray-500 rounded-r">
                          Minutes
                        </div>
                      </div>
                        <button
                          type="button"
                          className="text-teal-500 hover:text-teal-700 flex items-center text-sm"
                          onClick={() =>
                            handleAddNotificationTime(keyword.text)
                          }
                        >
                          <PlusCircle className="h-4 w-4 mr-1" />
                          <span>Add Time</span>
                        </button>
                        <button
                          type="button"
                          className="text-red-500 hover:text-red-700"
                          onClick={() => handleRemoveKeyword(keyword.text)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </div>

                    <div className="space-y-2">
                      {keyword.notificationTimes.map((time, index) => (
                        <div
                          key={index}
                          className="flex items-center justify-between p-2 border border-gray-200 rounded bg-white"
                        >
                          <span className="text-sm text-gray-500">
                            Notification #{index + 1}:
                          </span>
                          <div className="flex items-center gap-2">
                            <div className="flex items-center">
                              <span className="text-sm text-gray-500 mr-2">
                                Send after:
                              </span>
                              <input
                                type="number"
                                value={time}
                                onChange={(e) =>
                                  handleNotificationTimeChange(
                                    keyword.text,
                                    index,
                                    parseInt(e.target.value) || 0
                                  )
                                }
                                disabled
                                className="w-16 border border-gray-300 rounded-l py-1 px-2 text-sm focus:outline-none focus:ring-1 focus:ring-teal-500 focus:border-teal-500"
                              />
                              <div className="px-3 py-1 border border-l-0 border-gray-300 bg-gray-100 text-sm text-gray-500 rounded-r">
                                Minutes
                              </div>
                            </div>
                            {keyword.notificationTimes.length > 1 && (
                              <button
                                type="button"
                                className="text-red-500 hover:text-red-700"
                                onClick={() =>
                                  handleRemoveNotificationTime(
                                    keyword.text,
                                    index
                                  )
                                }
                              >
                                <MinusCircle className="h-4 w-4" />
                              </button>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default SMSNotificationSettings;