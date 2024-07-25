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
        <div className="">
          <img alt="img1" src={img1}></img>
        </div>
        <div className="">
          <img alt="img2" src={img2}></img>
        </div>
        <div className="">
          {" "}
          <img alt="img3" src={img3}></img>
        </div>
        <div className="">
          {" "}
          <img alt="img3" src={img4}></img>
        </div>
      </div>
    </div>
  );
}
