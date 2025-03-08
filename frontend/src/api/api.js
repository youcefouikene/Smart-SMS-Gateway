import axios from 'axios';

const API_URL = 'http://localhost:8000'; // Ajustez selon l'URL de votre backend


// Create an Axios instance
const api = axios.create({
  baseURL: API_URL,
});

// Add a response interceptor to handle token expiration
api.interceptors.response.use(
  (response) => response, // Return response normally if successful
  (error) => {
    if (error.response && error.response.status === 401) {
      // If the token is invalid or expired, remove user data and redirect to login
      localStorage.removeItem("user");
      window.location.href = "/login"; // Redirect to login
    }
    return Promise.reject(error);
  }
);

export const login = async (email, password) => {
  try {
    const response = await api.post(`${API_URL}/login`, {
      email: email,
      password: password,
    });

    // if (response.data.access_token) {
    //   localStorage.setItem("token", response.data.access_token); // Stocke le token
    // }
    console.log(response.data)

    return response.data;
  } catch (error) {
    console.error("Erreur de connexion:", error.response?.data || error.message);
    throw error;
  }
};

export const registerInit = async (username, email, password) => {
  const response = await api.post('/register/init', {
    username,
    email,
    password
  });
  return response.data;
};

export const registerComplete = async (registrationId, authCode) => {
  const response = await api.post('/register/complete', {
    registration_id: registrationId,
    auth_code: authCode
  });
  return response.data;
};

export const addKeyword = async (keyword, firstNotificationTime, token) => {
  try {
    // console.log("Données envoyées :", { keyword, firstNotificationTime });

    const response = await api.post(
      `${API_URL}/add-keyword`,
      null, // Pas de body JSON
      {
        params: { keyword: keyword.trim(), first_notification_time: firstNotificationTime },
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    return response.data;
  } catch (error) {
    console.error("Erreur lors de l'ajout du mot-clé :", error.response?.data || error);
    throw error;
  }
};

export const removeKeyword = async (keyword, token) => {
  try {
    const response = await api.delete(`${API_URL}/delete-keyword`, {
      params: { keyword },
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    return response.data;
  } catch (error) {
    console.error("Erreur lors de la suppression du mot-clé :", error.response?.data || error);
    throw error;
  }
};

export const getUserSettings = async (username) => {
  try {
    const response = await api.get(`${API_URL}/user-settings/${username}`);
    return response.data;
  } catch (error) {
    console.error("Erreur lors de la récupération des paramètres utilisateur :", error);
    throw error;
  }
};

export const addNotificationTime = async (keyword, notificationTime, token) => {
  try {
    const response = await api.post(
      `${API_URL}/add-notification-time`,
      null, 
      {
        params: {
          keyword: keyword.trim(),
          notification_time: notificationTime,
        },
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    return response.data;
  } catch (error) {
    console.error("Erreur lors de l'ajout du temps de notification :", error);
    throw error;
  }
};

export const deleteNotificationTime = async (keyword, notificationTime, token) => {
  try {
    const response = await api.delete(`${API_URL}/delete-notification-time`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      params: {
        keyword: keyword.trim(),
        notification_time: notificationTime,
      },
    });

    return response.data;
  } catch (error) {
    console.error("Erreur lors de la suppression du temps de notification :", error.response || error);
    throw error;
  }
};


export const saveSettings = async (phoneNumber, agendaFields, token) => {
  try {

    const response = await api.post(
      `${API_URL}/save-settings`,
      agendaFields,
      {
        params: {
          phoneNumber: phoneNumber.trim(),
        },
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    return response.data;
  } catch (error) {
    console.error("Erreur lors de l'enregistrement des parametres :", error.response?.data || error);
    throw error;
  }
};