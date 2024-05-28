// background.js

chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
    if (request.action === "analyze") {
      chrome.tabs.executeScript(sender.tab.id, { file: ".js" }, function () {
        chrome.tabs.sendMessage(sender.tab.id, { url: request.url }, function (response) {
          sendResponse(response);
        });
      });
    }
    return true;  // Keep the message channel open for sendResponse
  });

  chrome.runtime.onInstalled.addListener(() => {
    console.log('Extension installed');
  });
  chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.url) {
      // Clear the stored output when the URL changes
      chrome.storage.local.remove('analyzeResult', () => {
        console.log('Stored result cleared due to URL change');
      });
    }
  });
  