import img1 from "../Assets/room1.png";
import img2 from "../Assets/room2.png";
import img3 from "../Assets/room3.png";
import img4 from "../Assets/room3.png";

export default function FifthPage() {
  return (
    <div className="flex justify-center flex-col items-center">
      <div className="mt-[48px] mb-[20px] font-bold text-[30px]">
        Browse The Range
      </div>
      <div className="mb-[48px]">
        Lorem ipsum dolor sit amet, consectetur adipiscing elit.
      </div>
      <div className="flex gap-[20px] items-center justify-center">
        <div className="flex flex-col items-center justify-center font-semibold text-[24px]">
          <img alt="img1" src={img1}></img>
          <div className="pt-[30px] pb-[60px]">Dinning</div>
        </div>
        <div className="flex flex-col items-center justify-center font-semibold text-[24px] ">
          <img alt="img2" src={img2}></img>
          <div className="pt-[30px] pb-[60px]">Living</div>
        </div>
        <div className="flex flex-col items-center justify-center font-semibold text-[24px]">
          {" "}
          <img alt="img3" src={img3}></img>
          <div className="pt-[30px] pb-[60px]">Bedroom</div>
        </div>
      </div>
      <div className="w-full h-[1px] flex-shrink-0 bg-gray-300"></div>
    </div>
  );
}
