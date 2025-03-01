// import React from 'react';
// import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
// import Login from './components/Login';
// import Register from './components/Register';
// import SMSNotificationSettings from './components/SMSNotificationSettings';
// import PrivateRoute from './components/PrivateRoute';

// function App() {
//   return (
//     <Router>
//       <Routes>
//         <Route path="/login" element={<Login />} />
//         <Route path="/register" element={<Register />} />
//         <Route 
//           path="/settings" 
//           element={
//             <PrivateRoute>
//               <SMSNotificationSettings />
//             </PrivateRoute>
//           } 
//         />
//         <Route path="/" element={<Navigate to="/settings" />} />
//       </Routes>
//     </Router>
//   );
// }

// export default App;

import Register from "./components/register";
import Login from "./components/login";
import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import SMSNotificationSettings from "./components/SMSNotificationSettings";

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Navigate to="/login" />} />
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
        <Route path="/settings" element={<SMSNotificationSettings />} />
      </Routes>
    </Router>
  );
};

export default App;