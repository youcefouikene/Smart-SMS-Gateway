import img1 from "../Assets/Purchase Securely.png";
import img2 from "../Assets/Ships From Warehouse.png";
import img3 from "../Assets/Style Your Room.png";
export default function SixthPage() {
  return (
    <div className="flex flex-col justify-center items-center">
      <div className="mt-[48px] mb-[20px] font-bold text-[30px]">
        How it Works
      </div>
      <div className="mb-[48px]">
        Lorem ipsum dolor sit amet, consectetur adipiscing elit.
      </div>
      <div className="flex justify-center items-center gap-[20px] pb-[186px]">
        <div>
          <img src={img1} alt="img1"></img>
          <div className="flex justify-center items-center flex-col">
            <div className="font-bold text-[23px] pb-[9px]">
              Purchase Surely
            </div>
            <div className="text-[#666666] text-[17px] ">
              Lorem ipsum dolor sit amet, consectetur
            </div>
            <div className="text-[#666666] text-[17px]">adipiscing elit.</div>
          </div>
        </div>
        <div>
          <img src={img2} alt="img2"></img>
          <div className="flex justify-center items-center flex-col">
            <div className="font-bold text-[23px] pb-[9px]">
              Ships From WareHouse
            </div>
            <div className="text-[#666666] text-[17px] ">
              Lorem ipsum dolor sit amet, consectetur
            </div>
            <div className="text-[#666666] text-[17px]">adipiscing elit.</div>
          </div>
        </div>
        <div>
          <img src={img3} alt="img3"></img>
          <div className="flex justify-center items-center flex-col">
            <div className="font-bold text-[23px] pb-[9px]">
              Style Your Room
            </div>
            <div className="text-[#666666] text-[17px] ">
              Lorem ipsum dolor sit amet, consectetur
            </div>
            <div className="text-[#666666] text-[17px]">adipiscing elit.</div>
          </div>
        </div>
      </div>
    </div>
  );
}
