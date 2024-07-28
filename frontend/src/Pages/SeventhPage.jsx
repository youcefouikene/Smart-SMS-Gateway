import React from "react";
import IG1 from "../Assets/Images/IG-1.png";
import IG2 from "../Assets/Images/IG-2.png";
import IG3 from "../Assets/Images/IG-3.png";
import IG4 from "../Assets/Images/IG-4.png";

export default function SeventhPage() {
  return (
    <div className="flex justify-between items-center bg-[#03344F] text-white h-[365px]">
      <div className="ml-[140px] w-[400px]">
        <div className="text-white font-bold mb-[20px] text-[23px]">
          Beauty Care
        </div>
        <div className="mb-[20px]">
          Do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim
          ad minim veniam, quis nostrud exercitation ullamco laboris.
        </div>
        <div className="font-bold text-[23px]">Follow Us</div>
      </div>
      <div>
        <div className="font-bold text-[23px] mb-[20px]">Instagram Shop</div>
        <div className="flex gap-[20px]">
          <img src={IG1} alt="first" />
          <img src={IG2} alt="second" />
          <img src={IG3} alt="third" />
          <img src={IG4} alt="fourth" className="mr-[140px]" />
        </div>
      </div>
    </div>
  );
}
