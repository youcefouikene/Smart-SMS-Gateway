import React from "react";
export default function NavBar() {
  return (
    <div className="fixed top-0 w-full">
      <div className="flex justify-between items-center h-[100px] bg-white">
        <div className="pl-[160px] text-[#054C73] text-[30px] font-bold ">
          Interior
        </div>
        <div className="flex gap-[70px] pr-[160px] font-semibold text-[13px]">
          <div>Home</div>
          <div>Services</div>
          <div>Doctors</div>
          <div>Products</div>
          <div>Gallery</div>
        </div>
      </div>
    </div>
  );
}
