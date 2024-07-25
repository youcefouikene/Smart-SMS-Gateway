import logo from "./logo.svg";
import "./App.css";
import NavBar from "./Components/navbar";
import NewArrival from "./Components/NewArrival";
import FirstPage from "./Pages/FirstPage";
import SecondPage from "./Pages/SecondPage";
import Submit from "./Components/submit";
import ThirdPage from "./Pages/ThirdPage";
import FourthPage from "./Pages/FourthPage";
import FifthPage from "./Pages/FifthPage";
import SixthPage from "./Pages/SixthPage";

function App() {
  return (
    <div>
      <SecondPage />
      <FifthPage />
      <ThirdPage />
      <FourthPage />
      <SixthPage />
    </div>
  );
}

export default App;
