import img from "../Assets/eclipse.png";
export default function SeventhPage() {
  return (
    <div className="bg-[#F2F5FF] flex justify-between items-center">
      <div className="ml-[160px]">
        <div className="font-bold text-[32px] mb-[20px]">
          Beautify Your Space
        </div>
        <div className="text-[#666666] text-[20px]">
          Do eiusmod tempor incididunt ut labore et
        </div>
        <div className="text-[#666666] text-[20px]">
          dolore magna aliqua. Ut enim ad minim veniam,
        </div>
        <div className="text-[#666666] text-[20px] mb-[30px]">
          quis nostrud exercitation ullamco laboris.
        </div>
        <div>
          <button className="bg-[#054C73] rounded-[50px]">
            <div className="font-bold text-white px-[57px] py-[24px]">
              Learn More
            </div>
          </button>
        </div>
      </div>
      <img className="py-[60px] pr-[140px]" alt="img" src={img} />
    </div>
  );
}
