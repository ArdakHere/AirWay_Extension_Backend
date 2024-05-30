document.addEventListener('DOMContentLoaded', async function () {
  const hasSavedResult = await displaySavedResult();
  document.getElementById('viewReport').addEventListener('click', viewReport);

  if (!hasSavedResult) {
    fetchData();
  }
  document.getElementById('findObjects').addEventListener('click', findInfrastructure);
});

function fetchData() {
  try {
    chrome.tabs.query({active: true, currentWindow: true}, function (tabs) {
      const activeTab = tabs[0];

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
          const parsedData = parseDataFromHTML(htmlContent);
          // if(parseDataFromHTML(parsedData.coords)){
            console.log('Parsed data:', parsedData);
            fetch('https://airway-chrome-extension.onrender.com/analyze/krisha', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ url: activeTab.url, coords: parsedData.coords}), // Include HTML content in the body
            })
            .then(response => {
              if (!response.ok) {
                throw new Error('Network response was not ok');
              }
              return response.json();
            })
            .then(data => {
              data.city = parsedData.city;  // Add city data to the response data
              console.log('Response data:', data);
              displayResult(data);
              saveResult(activeTab.url, data);  // Save the result to chrome.storage.local
              // Show the infrastructure section
              document.querySelector('.infrastructure-section').classList.remove('hidden');
              console.log(data)
              fetchReportImage(data);
            })
            .catch(error => {
              console.error('Fetch error:', error);
              document.getElementById('result').innerHTML = '<p>Error retrieving data</p>';
            });
          // } else {
          //   document.getElementById('result').innerHTML = '<p>Перейдите на страницу объявления для получения отчета</p>';
          // }
        }
      );
    });
  } catch (error) {
    console.error('Error in fetchData:', error);
  }

}

function fetchReportImage(data_dict) {
  fetch('https://airway-chrome-extension.onrender.com/get_krisha_report', {
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
      chrome.storage.local.set({ reportImageData: data.report_image }, () => {
        document.getElementById('result').innerHTML += '<p>Отчет готов, нажмите на кнопку ниже</p>';
      });

    } else {
      document.getElementById('result').innerHTML += '<p>No image data received</p>';
    }
  })
  .catch(error => {
    console.error('Fetch error:', error);
    document.getElementById('result').innerHTML += '<p>Error retrieving report image</p>';
  });
}

function parseDataFromHTML(html) {
  const latMatch = html.match(/"lat":([\d.]+)/);
  const lonMatch = html.match(/"lon":([\d.]+)/);
  const cityMatch = html.match(/"city":"([^"]+)"/);

  const coords = latMatch && lonMatch ? { lat: parseFloat(latMatch[1]), lon: parseFloat(lonMatch[1]) } : null;
  const city = cityMatch ? cityMatch[1] : null;
  console.log(city);

  return { coords, city };
}

function displayResult(data) {
  // Extract required properties
  const { aq_index_color, aq_index_numeric, num_of_ev_chargers, num_of_parks, city } = data;

  // Convert color array to RGB format
  const colorRgb = `rgb(${aq_index_color.join(', ')})`;

  // Conditionally include the air quality index if the city is Алматы
  const airQualityHtml = city === 'Almaty' ? `
    <div style="margin-top: 8px; margin-bottom: 8px">
      <img src="./assets/images/air_q.png" alt="Air Pollution Icon" style="width: 32px; height: 32px; transform: translateY(5px)" />
      <strong style="font-size: 22px">Загрязненность воздуха: <span style="color: ${colorRgb}; font-size: 22px">${aq_index_numeric}</span></strong> 
    </div>` : '';

  const resultHtml = `
    <ul style="width: 300px">
      ${airQualityHtml}
      <div style="margin-top: 8px; margin-bottom: 8px">
        <img src="./assets/images/parks.png" alt="Park Icon" style="width: 32px; height: 32px; transform: translateY(5px)" />
        <strong style="font-size: 22px">Парки рядом: <span style="color: green; font-weight: bold;">${num_of_parks}</span></strong> 
      </div>
      <div style="margin-top: 8px; margin-bottom: 8px">
        <img src="./assets/images/ev_charger.png" alt="EV Charger Icon" style="width: 32px; height: 32px; transform: translateY(5px)" />
        <strong style="font-size: 22px">Зарядки для эл.мобилей рядом: <span style="color: green; font-weight: bold;">${num_of_ev_chargers}</span></strong> 
      </div>
    </ul>
  `;
  document.getElementById('viewReport').style.display = 'inline-block';


  document.getElementById('result').innerHTML = resultHtml;



}

function saveResult(url, data) {
  const result = {};
  result[url] = data;
  chrome.storage.local.set(result, function() {
    console.log('Result saved for URL:', url);
  });
}

function displaySavedResult() {
  return new Promise((resolve) => {
    chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
      const activeTab = tabs[0];
      const url = activeTab.url;

      chrome.storage.local.get(url, function (result) {
        if (result[url]) {
          displayResult(result[url]);
          // Show the infrastructure section
          document.querySelector('.infrastructure-section').classList.remove('hidden');
          resolve(true);
        } else {
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
    if (result.reportImageData) {
      const reportImageUrl = `data:image/png;base64,${result.reportImageData}`;
      chrome.tabs.create({ url: reportImageUrl });
    }
  });
}

function findInfrastructure() {
  const objectType = document.getElementById('objectType').value;
  const distance = document.getElementById('distance').value;

  chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
    const activeTab = tabs[0];

    chrome.scripting.executeScript(
      {
        target: { tabId: activeTab.id },
        func: () => document.documentElement.outerHTML
      },
      (results) => {
        if (chrome.runtime.lastError || !results || !results[0]) {
          console.error('Error executing script:', chrome.runtime.lastError);
          document.getElementById('infrastructureResult').innerHTML = '<p>Error retrieving HTML content</p>';
          return;
        }

        const htmlContent = results[0].result;
        const coords = parseDataFromHTML(htmlContent).coords;

        if (coords) {
          console.log('Coordinates found:', coords);

          fetch('https://airway-chrome-extension.onrender.com/find_objects', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ coords: coords, objectType: objectType, distance: distance }),
          })
          .then(response => {
            if (!response.ok) {
              throw new Error('Network response was not ok');
            }
            return response.json();
          })
          .then(data => {
            console.log('Infrastructure response data:', data);
            displayInfrastructureResult(data);
          })
          .catch(error => {
            console.error('Fetch error:', error);
            document.getElementById('infrastructureResult').innerHTML = '<p>Ошибка получения информации для отчета</p>';
          });
        } else {
          console.error('Coordinates not found');
          document.getElementById('infrastructureResult').innerHTML = '<p>Перейдите на страницу объявления для получения отчета</p>';
        }
      }
    );
  });
}

function displayInfrastructureResult(data) {
  if (!data.count) {
    document.getElementById('infrastructureResult').innerHTML = '<p>Ни один объект не найден</p>';
    return;
  }

  const infrastructureHtml = `
    <p>Кол-во найдено - ${data.count}</p>
  `;

  document.getElementById('infrastructureResult').innerHTML = infrastructureHtml;
}
