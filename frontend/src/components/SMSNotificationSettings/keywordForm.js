// File: src/components/SMSNotificationSettings/KeywordForm.js
import React from "react";
import { Plus } from "lucide-react";

const KeywordForm = ({ 
  newKeyword, 
  setNewKeyword, 
  newKeywordMinutes, 
  setNewKeywordMinutes, 
  onSubmit 
}) => {
  return (
    <div className="mb-6">
      <form
        onSubmit={onSubmit}
        className="flex flex-wrap gap-2 items-end"
      >
        <div className="flex-1">
          <label className="block text-xs text-gray-500 mb-1">
            Keyword
          </label>
          <input
            type="text"
            value={newKeyword}
            onChange={(e) => setNewKeyword(e.target.value)}
            placeholder="Add a new keyword"
            className="w-full rounded border border-gray-300 py-2 px-3 text-sm focus:outline-none focus:ring-1 focus:ring-teal-500 focus:border-teal-500"
          />
        </div>
        <div>
          <label className="block text-xs text-gray-500 mb-1">
            First Alert After
          </label>
          <div className="flex">
            <input
              type="number"
              value={newKeywordMinutes}
              min="0"
              onChange={(e) => {
                const value = parseInt(e.target.value, 10);
                setNewKeywordMinutes(value >= 0 ? value : 0);
              }}
              className="w-16 border border-gray-300 rounded-l py-2 px-3 text-sm focus:outline-none focus:ring-1 focus:ring-teal-500 focus:border-teal-500"
            />
            <div className="px-3 py-2 border border-l-0 border-gray-300 bg-gray-50 text-sm text-gray-500 rounded-r">
              Minutes
            </div>
          </div>
        </div>
        <button
          type="submit"
          className="bg-teal-500 text-white px-4 py-2 rounded flex items-center justify-center"
        >
          <Plus className="h-4 w-4 mr-1" />
          <span>Add</span>
        </button>
      </form>
    </div>
  );
};

export default KeywordForm;