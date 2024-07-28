import React from "react";
import Submit from "../Components/submit";
export default function SixthPage() {
  return (
    <div className="flex flex-col justify-center items-center bg-[#F2F5FF] h-[365px]">
      <div className="text-[30px] font-bold text-[#333333]">
        Join Our Mailing List
      </div>
      <div className=" pt-[10px] text-[#666666]">
        Sign up to receive inspiration, product updates, and{" "}
      </div>
      <div className="text-[#666666]">special offers from our team.</div>

      <Submit className="py-[60px]" />
    </div>
  );
}
