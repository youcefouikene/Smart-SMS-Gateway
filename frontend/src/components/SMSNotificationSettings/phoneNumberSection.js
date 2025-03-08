// File: src/components/SMSNotificationSettings/PhoneNumberSection.js
import React from "react";
import countryCodes from "../../data/countries.json";

const PhoneNumberSection = ({ 
  phoneNumber, 
  setPhoneNumber, 
  selectedCountry, 
  setSelectedCountry 
}) => {
  
  // Initialize selectedCountry if not set
  React.useEffect(() => {
    if (!selectedCountry) {
      setSelectedCountry(countryCodes[0]);
    }
  }, [selectedCountry, setSelectedCountry]);

  const handlePhoneNumberChange = (e) => {
    let value = e.target.value.replace(/\D/g, ""); // Remove all non-digits
  
    if (value.startsWith("0")) {
      value = value.substring(1); // Remove leading zero
    }
  
    setPhoneNumber(value);
  };

  return (
    <div className="mb-8">
      <h2 className="text-md font-medium mb-2">
        Phone Number to Receive Notifications
      </h2>
      <p className="text-sm text-gray-500 mb-4">
        Phone number to receive SMS alerts:
      </p>

      <div className="mt-1">
        <div className="flex flex-col">
          <label className="text-xs text-gray-500 mb-1">Phone number</label>
          <div className="relative">
            <div className="flex">
              {/* Country code dropdown */}
              <select
                className="border border-gray-300 rounded-l bg-white px-3 py-2 text-gray-600 text-sm focus:ring-teal-500 focus:border-teal-500"
                value={selectedCountry?.code || ""}
                onChange={(e) =>
                  setSelectedCountry(
                    countryCodes.find((c) => c.code === e.target.value)
                  )
                }
              >
                {countryCodes.map((country) => (
                  <option key={country.code} value={country.code}>
                    {country.name} {country.code}
                  </option>
                ))}
              </select>

              {/* Phone number input */}
              <input
                type="text"
                value={phoneNumber}
                onChange={handlePhoneNumberChange}
                className="flex-1 border border-l-0 border-gray-300 rounded-r py-2 px-3 focus:outline-none focus:ring-1 focus:ring-teal-500 focus:border-teal-500"
                placeholder="123456789"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PhoneNumberSection;