// File: src/components/SMSNotificationSettings/NotificationTimeItem.js
import React from "react";
import { MinusCircle } from "lucide-react";

const NotificationTimeItem = ({ 
  index, 
  time, 
  keywordText, 
  canRemove, 
  onRemoveNotificationTime 
}) => {
  return (
    <div className="flex items-center justify-between p-2 border border-gray-200 rounded bg-white">
      <span className="text-sm text-gray-500">
        Notification #{index + 1}:
      </span>
      <div className="flex items-center gap-2">
        <div className="flex items-center">
          <span className="text-sm text-gray-500 mr-2">
            Send after:
          </span>
          <input
            type="number"
            value={time}
            disabled
            className="w-16 border border-gray-300 rounded-l py-1 px-2 text-sm focus:outline-none focus:ring-1 focus:ring-teal-500 focus:border-teal-500"
          />
          <div className="px-3 py-1 border border-l-0 border-gray-300 bg-gray-100 text-sm text-gray-500 rounded-r">
            Minutes
          </div>
        </div>
        {canRemove && (
          <button
            type="button"
            className="text-red-500 hover:text-red-700"
            onClick={() => onRemoveNotificationTime(keywordText, index)}
          >
            <MinusCircle className="h-4 w-4" />
          </button>
        )}
      </div>
    </div>
  );
};

export default NotificationTimeItem;