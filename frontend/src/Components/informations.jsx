import img1 from "../Assets/icons/camion.svg";
export default function Info() {
  return (
    <div>
      <div className="flex gap-[120px] justify-center items-center py-[46px] bg-[#F2F5FF]">
        <div className="flex gap-[24px]">
          <img src={img1} alt="camion" />
          <div>
            <div className="font-semibold text-[24px] text-[#333333]">
              Free Delivery
            </div>
            <div className=" text-[16px] text-[#333333] ">
              Lorem ipsum dolor sit amet.
            </div>
          </div>
        </div>
        <div className="flex gap-[24px]">
          <img src={img1} alt="camion" />
          <div>
            <div className="font-semibold text-[24px] text-[#333333]">
              Free Delivery
            </div>
            <div className=" text-[16px] text-[#333333]">
              Lorem ipsum dolor sit amet.
            </div>
          </div>
        </div>
        <div className="flex gap-[24px]">
          <img src={img1} alt="camion" />
          <div>
            <div className="font-semibold text-[24px] text-[#333333]">
              Free Delivery
            </div>
            <div className=" text-[16px] text-[#333333]">
              Lorem ipsum dolor sit amet.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
