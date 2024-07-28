import React from "react";
import NewArrival from "../Components/NewArrival";
import image from "../Assets/Images/first-image.png";
import Info from "../Components/informations";

export default function FirstPage() {
  return (
    <div>
      <div
        className="h-screen w-full"
        style={{
          backgroundImage: `url(${image})`,
          backgroundSize: "cover",
          backgroundPosition: "center",
        }}
      >
        <div className="pl-[720px] pt-[165px] flex items-center justify-center">
          <NewArrival />
        </div>
      </div>
      <Info />
    </div>
  );
}
