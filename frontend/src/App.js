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
import SeventhPage from "./Pages/SeventhPage";
import Info from "./Components/informations";

function App() {
  return (
    <div>
      <NavBar />
      <FirstPage />
      <Info />
      <SecondPage />
      <SeventhPage />
      <FifthPage />
      <SixthPage />

      <ThirdPage />
      <FourthPage />
    </div>
  );
}

export default App;
