import React from "react";
import image from "../Assets/first-image.png";
import NavBar from "../Components/navbar";
import NewArrival from "../Components/NewArrival";

export default function FirstPage() {
  return (
    <div>
      <NavBar className="fixed top-0 w-full object-cover" />
      <img src={image} alt="imageyus" className="w-full h-screen " />
    </div>
  );
}
