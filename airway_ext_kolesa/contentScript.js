
function insertHTMLContent(data) {
  // Create a container for the injected content
  const container = document.createElement('div');
  container.style.position = 'fixed';
  container.style.top = '0';
  container.style.right = '0';
  container.style.backgroundColor = 'white';
  container.style.zIndex = '10000';
  container.style.border = '1px solid black';
  container.style.padding = '10px';
  container.style.maxHeight = '90%';
  container.style.overflowY = 'auto';

  // Generate the HTML content
  const { gas_mileage, effect_index, rgbColor, recommendations } = data;
  const rgbString = `rgb(${rgbColor.join(',')})`;
  const resultHtml = `
    <div style="margin-top: 8px; margin-bottom: 8px">
      <img src="${chrome.runtime.getURL('assets/images/tank_icon.png')}" alt="Air Pollution Icon" style="width: 32px; height: 32px; transform: translateY(5px)" />
      <strong style="font-size: 20px">Расход топлива на 100км: <span style="color: black; font-size: 20px">${gas_mileage} л.</span></strong>
      <div style="margin-top: 8px; margin-bottom: 8px">
        <img src="${chrome.runtime.getURL('assets/images/emission_icon.png')}" alt="Park Icon" style="width: 32px; height: 32px; transform: translateY(5px)" />
        <strong style="font-size: 20px">Влияние машины на загрязнение воздуха: <span style="color: ${rgbString}; font-weight: bold;">${effect_index}</span></strong>
      </div>
      <div style="margin-top: 8px; margin-bottom: 8px">
        <img src="${chrome.runtime.getURL('assets/images/car_options.png')}" alt="Park Icon" style="width: 32px; height: 32px; transform: translateY(5px)" />
        <strong style="font-size: 20px">Рассмотрите более экологичные автомобили по схожей цене: <span style="color: black; font-weight: bold;">${recommendations}</span></strong>
      </div>
    </div>`;

  container.innerHTML = resultHtml;

  // Append the container to the body
  document.body.appendChild(container);
}

// This is called by the injected script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'insertHTMLContent') {
    insertHTMLContent(request.data);
    sendResponse({ status: 'success' });
  }
});
