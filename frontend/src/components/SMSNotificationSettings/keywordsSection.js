// File: src/components/SMSNotificationSettings/KeywordsSection.js
import React, { useState } from "react";
import { addKeyword, removeKeyword, addNotificationTime, deleteNotificationTime } from "../../api/api";
import KeywordItem from "./keywordItem";
import KeywordForm from "./keywordForm";

const KeywordsSection = ({ keywords, setKeywords, userToken }) => {
  const [newKeyword, setNewKeyword] = useState("");
  const [newKeywordMinutes, setNewKeywordMinutes] = useState(15);
  const [newNotifMinutes, setNewNotifMinutes] = useState(0);

  const handleAddKeyword = async (e) => {
    e.preventDefault();
  
    if (newKeyword.trim() === "" || keywords.some((k) => k.text === newKeyword.trim())) {
      return;
    }
  
    try {
      await addKeyword(newKeyword, newKeywordMinutes, userToken);
  
      // Update local state if API call succeeds
      setKeywords([
        ...keywords,
        { text: newKeyword.trim(), notificationTimes: [newKeywordMinutes] },
      ]);
      setNewKeyword("");
      setNewKeywordMinutes(15);
    } catch (error) {
      alert("Unable to add keyword, please try again.");
    }
  };

  const handleRemoveKeyword = async (keywordText) => {
    try {
      await removeKeyword(keywordText, userToken);
      setKeywords(keywords.filter((k) => k.text !== keywordText));
    } catch (error) {
      alert("Error removing keyword!");
    }
  };

  const handleAddNotificationTime = async (keywordText) => {
    try {
      if (!userToken) {
        alert("You must be logged in to modify notifications.");
        return;
      }
  
      await addNotificationTime(keywordText, newNotifMinutes, userToken);
  
      // Update local state after successful API call
      setKeywords((prevKeywords) =>
        prevKeywords.map((k) =>
          k.text === keywordText
            ? { ...k, notificationTimes: [...k.notificationTimes, newNotifMinutes] }
            : k
        )
      );
    } catch (error) {
      alert("Unable to add notification time. Please try again.");
    }
  };

  const handleRemoveNotificationTime = async (keywordText, index) => {
    if (!userToken) {
      alert("You must be logged in to perform this action.");
      return;
    }
  
    const notificationTime = keywords.find(k => k.text === keywordText)?.notificationTimes[index];
  
    if (notificationTime === undefined) return;
  
    try {
      await deleteNotificationTime(keywordText, notificationTime, userToken);
      
      // Update local state after successful API call
      setKeywords(
        keywords.map((k) =>
          k.text === keywordText
            ? {
                ...k,
                notificationTimes: k.notificationTimes.filter((_, i) => i !== index),
              }
            : k
        )
      );
    } catch (error) {
      alert("Error removing notification time.");
    }
  };

  return (
    <div>
      <h2 className="text-md font-medium mb-2">Filter by Keywords</h2>
      <p className="text-sm text-gray-500 mb-4">
        Receive alerts only for events containing these keywords. Add
        multiple notification times for each keyword:
      </p>

      <KeywordForm
        newKeyword={newKeyword}
        setNewKeyword={setNewKeyword}
        newKeywordMinutes={newKeywordMinutes}
        setNewKeywordMinutes={setNewKeywordMinutes}
        onSubmit={handleAddKeyword}
      />

      <div className="space-y-4">
        {keywords.map((keyword) => (
          <KeywordItem
            key={keyword.text}
            keyword={keyword}
            newNotifMinutes={newNotifMinutes}
            setNewNotifMinutes={setNewNotifMinutes}
            onAddNotificationTime={handleAddNotificationTime}
            onRemoveKeyword={handleRemoveKeyword}
            onRemoveNotificationTime={handleRemoveNotificationTime}
          />
        ))}
      </div>
    </div>
  );
};

export default KeywordsSection;