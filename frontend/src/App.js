import React, { useState } from "react";
import {
  ChevronDown,
  Plus,
  User,
  Trash2,
  PlusCircle,
  MinusCircle,
} from "lucide-react";

const SMSNotificationSettings = () => {
  const [selectedFields, setSelectedFields] = useState({
    title: false,
    date: false,
    description: true,
    priority: true,
  });

  const [defaultMinutes, setDefaultMinutes] = useState(20);
  const [phoneNumber, setPhoneNumber] = useState("");
  const [keywords, setKeywords] = useState([
    {
      text: "Test A",
      notificationTimes: [15, 30, 45],
    },
    {
      text: "Test B",
      notificationTimes: [20, 40],
    },
    {
      text: "Test C",
      notificationTimes: [30],
    },
  ]);
  const [newKeyword, setNewKeyword] = useState("");
  const [newKeywordMinutes, setNewKeywordMinutes] = useState(15);

  const handleFieldToggle = (field) => {
    setSelectedFields((prev) => ({
      ...prev,
      [field]: !prev[field],
    }));
  };

  const handleRemoveKeyword = (keywordText) => {
    setKeywords(keywords.filter((k) => k.text !== keywordText));
  };

  const handleAddKeyword = (e) => {
    e.preventDefault();
    if (
      newKeyword.trim() !== "" &&
      !keywords.some((k) => k.text === newKeyword.trim())
    ) {
      setKeywords([
        ...keywords,
        { text: newKeyword.trim(), notificationTimes: [newKeywordMinutes] },
      ]);
      setNewKeyword("");
      setNewKeywordMinutes(15);
    }
  };

  const handleAddNotificationTime = (keywordText) => {
    setKeywords(
      keywords.map((k) =>
        k.text === keywordText
          ? { ...k, notificationTimes: [...k.notificationTimes, 15] }
          : k
      )
    );
  };

  const handleRemoveNotificationTime = (keywordText, index) => {
    setKeywords(
      keywords.map((k) =>
        k.text === keywordText
          ? {
              ...k,
              notificationTimes: k.notificationTimes.filter(
                (_, i) => i !== index
              ),
            }
          : k
      )
    );
  };

  const handleNotificationTimeChange = (keywordText, index, minutes) => {
    setKeywords(
      keywords.map((k) => {
        if (k.text === keywordText) {
          const newTimes = [...k.notificationTimes];
          newTimes[index] = minutes;
          return { ...k, notificationTimes: newTimes };
        }
        return k;
      })
    );
  };

  // Cette fonction pourrait être utilisée pour envoyer les données au backend
  const saveSettings = () => {
    // Créer un objet avec toutes les données à envoyer au backend
    const settings = {
      selectedFields,
      defaultNotificationTime: {
        value: defaultMinutes,
        unit: "Minutes",
      },
      phoneNumber,
      keywords,
    };

    console.log("Sending to backend:", settings);
    // Ici, vous pourriez implémenter un appel API, par exemple:
    // axios.post('/api/save-settings', settings)
    //   .then(response => console.log('Settings saved'))
    //   .catch(error => console.error('Error saving settings', error));
  };

  return (
    <div className="flex h-full bg-gray-100">
      {/* Main Content */}
      <div className="flex-1">
        <main className="mx-auto p-6">
          <div className="bg-white rounded-md shadow-sm p-6">
            <div className="flex justify-between items-center mb-8">
              <div>
                <h1 className="text-xl font-semibold text-gray-800">
                  SMS Notification Settings
                </h1>
                <p className="text-sm text-gray-500">Welcome back, John!</p>
              </div>
              <div className="flex space-x-2">
                <button className="px-4 py-2 border border-gray-300 rounded text-sm">
                  Edit
                </button>
                <button
                  className="px-4 py-2 bg-teal-500 text-white rounded text-sm"
                  onClick={saveSettings}
                >
                  Set Default
                </button>
              </div>
            </div>

            <div className="mb-8">
              <h2 className="text-md font-medium mb-2">
                Select Event Fields to Include in SMS
              </h2>
              <p className="text-sm text-gray-500 mb-4">
                Choose the event details to include in the SMS:
              </p>

              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="title"
                    checked={selectedFields.title}
                    onChange={() => handleFieldToggle("title")}
                    className="w-4 h-4 rounded border-gray-300 text-teal-500 focus:ring-0 focus:ring-offset-0"
                  />
                  <label htmlFor="title" className="ml-2 text-sm text-gray-700">
                    Title
                  </label>
                </div>
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="date"
                    checked={selectedFields.date}
                    onChange={() => handleFieldToggle("date")}
                    className="w-4 h-4 rounded border-gray-300 text-teal-500 focus:ring-0 focus:ring-offset-0"
                  />
                  <label htmlFor="date" className="ml-2 text-sm text-gray-700">
                    Date
                  </label>
                </div>
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="description"
                    checked={selectedFields.description}
                    onChange={() => handleFieldToggle("description")}
                    className="w-4 h-4 rounded border-gray-300 text-teal-500 focus:ring-0 focus:ring-offset-0"
                  />
                  <label
                    htmlFor="description"
                    className="ml-2 text-sm text-gray-700"
                  >
                    Description
                  </label>
                </div>
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="priority"
                    checked={selectedFields.priority}
                    onChange={() => handleFieldToggle("priority")}
                    className="w-4 h-4 rounded border-gray-300 text-teal-500 focus:ring-0 focus:ring-offset-0"
                  />
                  <label
                    htmlFor="priority"
                    className="ml-2 text-sm text-gray-700"
                  >
                    Priority
                  </label>
                </div>
              </div>
            </div>

            <div className="mb-8">
              <h2 className="text-md font-medium mb-2">
                Phone Number to Receive Notifications
              </h2>
              <p className="text-sm text-gray-500 mb-4">
                Phone number to receive SMS alerts:
              </p>

              <div className="mt-1">
                <div className="flex flex-col">
                  <label className="text-xs text-gray-500 mb-1">
                    Phone number
                  </label>
                  <div className="relative">
                    <div className="flex">
                      <div className="flex items-center justify-between border border-gray-300 rounded-l bg-white px-3 text-gray-600 text-sm">
                        <span className="mr-1">US +1</span>
                        <ChevronDown className="h-4 w-4 text-gray-400" />
                      </div>
                      <input
                        type="text"
                        value={phoneNumber}
                        onChange={(e) => setPhoneNumber(e.target.value)}
                        className="flex-1 border border-l-0 border-gray-300 rounded-r py-2 px-3 focus:outline-none focus:ring-1 focus:ring-teal-500 focus:border-teal-500"
                        placeholder="1234 5678"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div>
              <h2 className="text-md font-medium mb-2">Filter by Keywords</h2>
              <p className="text-sm text-gray-500 mb-4">
                Receive alerts only for events containing these keywords. Add
                multiple notification times for each keyword:
              </p>

              <div className="mb-6">
                <form
                  onSubmit={handleAddKeyword}
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
                        onChange={(e) =>
                          setNewKeywordMinutes(parseInt(e.target.value) || 0)
                        }
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

              <div className="space-y-4">
                {keywords.map((keyword) => (
                  <div
                    key={keyword.text}
                    className="p-4 border border-gray-200 rounded bg-gray-50"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <span className="font-medium text-teal-600 px-3 py-1 bg-teal-100 rounded-full">
                        {keyword.text}
                      </span>
                      <div className="flex items-center gap-2">
                        <button
                          type="button"
                          className="text-teal-500 hover:text-teal-700 flex items-center text-sm"
                          onClick={() =>
                            handleAddNotificationTime(keyword.text)
                          }
                        >
                          <PlusCircle className="h-4 w-4 mr-1" />
                          <span>Add Time</span>
                        </button>
                        <button
                          type="button"
                          className="text-red-500 hover:text-red-700"
                          onClick={() => handleRemoveKeyword(keyword.text)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </div>

                    <div className="space-y-2">
                      {keyword.notificationTimes.map((time, index) => (
                        <div
                          key={index}
                          className="flex items-center justify-between p-2 border border-gray-200 rounded bg-white"
                        >
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
                                onChange={(e) =>
                                  handleNotificationTimeChange(
                                    keyword.text,
                                    index,
                                    parseInt(e.target.value) || 0
                                  )
                                }
                                className="w-16 border border-gray-300 rounded-l py-1 px-2 text-sm focus:outline-none focus:ring-1 focus:ring-teal-500 focus:border-teal-500"
                              />
                              <div className="px-3 py-1 border border-l-0 border-gray-300 bg-gray-100 text-sm text-gray-500 rounded-r">
                                Minutes
                              </div>
                            </div>
                            {keyword.notificationTimes.length > 1 && (
                              <button
                                type="button"
                                className="text-red-500 hover:text-red-700"
                                onClick={() =>
                                  handleRemoveNotificationTime(
                                    keyword.text,
                                    index
                                  )
                                }
                              >
                                <MinusCircle className="h-4 w-4" />
                              </button>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default SMSNotificationSettings;
