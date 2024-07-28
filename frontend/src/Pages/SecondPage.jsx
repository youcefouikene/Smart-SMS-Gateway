import img1 from "../Assets/Images/g1.png";
import img2 from "../Assets/Images/g2.png";
import img3 from "../Assets/Images/g3.png";

export default function SecondPage() {
  return (
    <div className="flex justify-center flex-col items-center">
      <div className="mt-[48px] mb-[20px] font-bold text-[30px]">
        Inspiration Collection
      </div>
      <div className="mb-[48px]">
        Lorem ipsum dolor sit amet, consectetur adipiscing elit.
      </div>
      <div className="flex gap-[20px] items-center justify-center pb-[60px]">
        <div className="mt-[40px]">
          <img alt="img1" src={img1}></img>
        </div>
        <div className="mb-[40px]">
          <img alt="img2" src={img2}></img>
        </div>
        <div className="mt-[40px]">
          {" "}
          <img alt="img3" src={img3}></img>
        </div>
      </div>
    </div>
  );
}
