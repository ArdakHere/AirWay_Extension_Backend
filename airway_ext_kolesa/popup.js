document.addEventListener('DOMContentLoaded', async function () {
  console.log('DOM fully loaded and parsed');
  const hasSavedResult = await displaySavedResult();
    document.getElementById('viewReport').addEventListener('click', viewReport);

  if (!hasSavedResult) {
    fetchData();

  }
});

function fetchData() {
  try {
    chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
      const activeTab = tabs[0];
      console.log('Active tab:', activeTab);

      // Clear stored image data when a new listing is accessed
      chrome.storage.local.remove('reportImageData', function () {
        console.log('Cleared stored report image data');
      });

      // Fetch the HTML content of the active tab
      chrome.scripting.executeScript(
        {
          target: { tabId: activeTab.id },
          func: () => document.documentElement.outerHTML
        },
        (results) => {
          if (chrome.runtime.lastError || !results || !results[0]) {
            console.error('Error executing script:', chrome.runtime.lastError);
            document.getElementById('result').innerHTML = '<p>Error retrieving HTML content</p>';
            return;
          }
          const htmlContent = results[0].result;
          if(parseDataFromHTML(htmlContent)){
            fetch('http://3.75.158.163/analyze/kolesa', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ url: activeTab.url, html: htmlContent }), // Include HTML content in the body
            })
            .then(response => {
              if (!response.ok) {
                throw new Error('Network response was not ok');
              }
              return response.json();
            })
            .then(data => {
              console.log('Response data:', data);
              displayResult(data);
              saveResult(activeTab.url, data);  // Save the result to chrome.storage.local
              fetchReportImage(data);
            })
            .catch(error => {
              console.error('Fetch error:', error);
              document.getElementById('result').innerHTML = '<p>Error retrieving data</p>';
            });
          } else {
            document.getElementById('result').innerHTML = '<p>Перейдите на страницу объявления для получения отчета</p>';
          }
        }
      );
    });
  } catch (error) {
    console.error('Error in fetchData:', error);
  }
}

function parseDataFromHTML(html) {
  // ... your existing code ...

  // Check if the string "Коробка передач" is present in the HTML
  const isPresent = html.includes("Коробка передач");

  // Return the result
  return isPresent;
}

function fetchReportImage(data_dict) {
  fetch('http://3.75.158.163/get_kolesa_report', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ data: data_dict }),
  })
  .then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  })
  .then(data => {
    if (data.report_image) {
      // Store the report image data for later use
      console.log("Storing report for future use");
      chrome.storage.local.set({ reportImageData: data.report_image }, () => {
        if (chrome.runtime.lastError) {
          console.error('Error saving report image data:', chrome.runtime.lastError);
        } else {
          console.log('Stored report image data successfully');
          document.getElementById('result').innerHTML += '<p>Отчет готов, нажмите на кнопку ниже</p>';
        }
      });
    } else {
      console.log('No image data received');
      document.getElementById('result').innerHTML += '<p>No image data received</p>';
    }
  })
  .catch(error => {
    console.error('Fetch error:', error);
    document.getElementById('result').innerHTML += '<p>Error retrieving report image</p>';
  });
}

function displayResult(data) {
  // Extract required properties
  const { gas_mileage, effect_index, rgbColor, recommendations } = data;
  console.log("Displaying result:", data);

  // Convert the rgbColor array to a CSS-compatible RGB string
  const rgbString = `rgb(${rgbColor.join(',')})`;

  // Generate the result HTML
  const resultHtml = `
    <div style="margin-top: 8px; margin-bottom: 8px">
      <img src="./assets/images/tank_icon.png" alt="Air Pollution Icon" style="width: 32px; height: 32px; transform: translateY(5px)" />
      <strong style="font-size: 20px">Расход топлива на 100км: <span style="color: black; font-size: 20px">${gas_mileage} л.</span></strong>
      <div style="margin-top: 8px; margin-bottom: 8px">
        <img src="./assets/images/emission_icon.png" alt="Park Icon" style="width: 32px; height: 32px; transform: translateY(5px)" />
        <strong style="font-size: 20px">Влияние машины на загрязнение воздуха: <span style="color: ${rgbString}; font-weight: bold;">${effect_index}</span></strong>
      </div>
      <div style="margin-top: 8px; margin-bottom: 8px">
        <img src="./assets/images/car_options.png" alt="Park Icon" style="width: 32px; height: 32px; transform: translateY(5px)" />
        <strong style="font-size: 20px">Рассмотрите более экологичные автомобили по схожей \n ценей : <span style="color: black"; font-weight: bold;">${recommendations}</span></strong>
      </div>
    </div>`;
    document.getElementById('viewReport').style.display = 'inline-block';

  document.getElementById('result').innerHTML = resultHtml;
}

function saveResult(url, data) {
  const result = {};
  result[url] = data;
  console.log('Saving result for URL:', url, 'with data:', data);
  chrome.storage.local.set(result, function () {
    if (chrome.runtime.lastError) {
      console.error('Error saving result:', chrome.runtime.lastError);
    } else {
      console.log('Result saved for URL:', url);
      chrome.storage.local.get(url, function (storedResult) {
        console.log('Retrieved stored result to confirm:', storedResult);
      });
    }
  });
}

function displaySavedResult() {
  return new Promise((resolve) => {
    chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
      const activeTab = tabs[0];
      const url = activeTab.url;
      
      chrome.storage.local.get(url, function (result) {
        if (chrome.runtime.lastError) {
          console.error('Error retrieving saved result:', chrome.runtime.lastError);
          resolve(false);
          return;
        }

        if (result[url]) {
          console.log('Displaying saved result for URL:', url, 'with data:', result[url]);
          displayResult(result[url]);
          document.getElementById('viewReport').style.display = 'inline-block';

          // Show the infrastructure section
          resolve(true);
        } else {
          console.log('No saved result found for URL:', url);
          // Clear stored image data if URL does not match
          chrome.storage.local.remove('reportImageData', function () {
            console.log('Cleared stored report image data due to URL mismatch');
          });
          resolve(false);
        }
      });
    });
  });
}

function viewReport() {
  chrome.storage.local.get('reportImageData', (result) => {
    if (chrome.runtime.lastError) {
      console.error('Error retrieving report image data:', chrome.runtime.lastError);
      return;
    }

    if (result.reportImageData) {
      const reportImageUrl = `data:image/png;base64,${result.reportImageData}`;
      console.log('Opening report image:', reportImageUrl);
      chrome.tabs.create({ url: reportImageUrl });
    } else {
      console.log('No report image data found');
    }
  });
}