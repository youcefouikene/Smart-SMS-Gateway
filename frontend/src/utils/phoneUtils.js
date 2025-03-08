import countryCodes from "../data/countries.json";

export const removeCountryCode = (fullPhoneNumber) => {
  const foundCode = countryCodes.find(({ code }) => fullPhoneNumber.startsWith(code));
  return foundCode ? fullPhoneNumber.slice(foundCode.code.length) : fullPhoneNumber;
};