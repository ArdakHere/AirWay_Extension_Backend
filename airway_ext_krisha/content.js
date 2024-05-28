// content.js

function extractCoordinates() {
    // Adjust the selectors based on the actual HTML structure of the listing page
    const latElement = document.querySelector('meta[property="lat"]');
    const lonElement = document.querySelector('meta[property="lon"]');
    
    
    const lat = latElement ? latElement.getAttribute('content') : null;
    const lon = lonElement ? lonElement.getAttribute('content') : null;
  
    return { lat, lon };
  }
  chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
    if (request.action === "getCoordinates") {
      const lat = "43.443"; // Example lat, replace with actual extraction logic
      const lon = "75.223"; // Example lon, replace with actual extraction logic
      sendResponse({ text: { lat: lat, lon: lon } });
    }
  });
  
  