// File: src/components/SMSNotificationSettings/KeywordItem.js
import React from "react";
import { Trash2, PlusCircle } from "lucide-react";
import NotificationTimeItem from "./notificationTimeItem";

const KeywordItem = ({ 
  keyword, 
  newNotifMinutes, 
  setNewNotifMinutes, 
  onAddNotificationTime, 
  onRemoveKeyword, 
  onRemoveNotificationTime 
}) => {
  return (
    <div className="p-4 border border-gray-200 rounded bg-gray-50">
      <div className="flex items-center justify-between mb-3">
        <span className="font-medium text-teal-600 px-3 py-1 bg-teal-100 rounded-full">
          {keyword.text}
        </span>
        <div className="flex items-center gap-2">
          <div className="flex">
            <input
              type="number"
              value={newNotifMinutes}
              min="0"
              onChange={(e) => {
                const value = parseInt(e.target.value, 10);
                setNewNotifMinutes(value >= 0 ? value : 0);
              }}
              className="w-16 border border-gray-300 rounded-l py-2 px-3 text-sm focus:outline-none focus:ring-1 focus:ring-teal-500 focus:border-teal-500"
            />
            <div className="px-3 py-2 border border-l-0 border-gray-300 bg-gray-50 text-sm text-gray-500 rounded-r">
              Minutes
            </div>
          </div>
          <button
            type="button"
            className="text-teal-500 hover:text-teal-700 flex items-center text-sm"
            onClick={() => onAddNotificationTime(keyword.text)}
          >
            <PlusCircle className="h-4 w-4 mr-1" />
            <span>Add Time</span>
          </button>
          <button
            type="button"
            className="text-red-500 hover:text-red-700"
            onClick={() => onRemoveKeyword(keyword.text)}
          >
            <Trash2 className="h-4 w-4" />
          </button>
        </div>
      </div>

      <div className="space-y-2">
        {keyword.notificationTimes.map((time, index) => (
          <NotificationTimeItem
            key={index}
            index={index}
            time={time}
            keywordText={keyword.text}
            canRemove={keyword.notificationTimes.length > 1}
            onRemoveNotificationTime={onRemoveNotificationTime}
          />
        ))}
      </div>
    </div>
  );
};

export default KeywordItem;