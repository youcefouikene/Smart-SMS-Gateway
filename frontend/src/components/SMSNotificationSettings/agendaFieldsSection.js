// File: src/components/SMSNotificationSettings/AgendaFieldsSection.js
import React from "react";

const AgendaFieldsSection = ({ selectedFields, onFieldToggle }) => {
  const fields = [
    { id: "summary", label: "Title" },               
    { id: "start", label: "Start Date & Time" },     
    { id: "end", label: "End Date & Time" },         
    { id: "location", label: "Location" },           
    { id: "description", label: "Description" },     
    { id: "organizer", label: "Organizer" },         
  ];

  return (
    <div className="mb-8">
      <h2 className="text-md font-medium mb-2">
        Select Event Fields to Include in SMS
      </h2>
      <p className="text-sm text-gray-500 mb-4">
        Choose the event details to include in the SMS:
      </p>

      <div className="grid grid-cols-3 gap-4">
        {fields.map((field) => (
          <div key={field.id} className="flex items-center">
            <input
              type="checkbox"
              id={field.id}
              checked={selectedFields[field.id]}
              onChange={() => onFieldToggle(field.id)}
              className="w-4 h-4 rounded border-gray-300 text-teal-500 focus:ring-0 focus:ring-offset-0"
            />
            <label htmlFor={field.id} className="ml-2 text-sm text-gray-700">
              {field.label}
            </label>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AgendaFieldsSection;